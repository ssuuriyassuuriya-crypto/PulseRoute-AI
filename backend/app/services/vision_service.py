from pathlib import Path
import os
from threading import Lock
from time import perf_counter
from typing import Any
from uuid import uuid4

from app.config import Settings
from app.schemas.traffic import BoundingBox, TrafficFrameRequest, VehicleClass, VehicleObservation
from app.services.traffic_service import TrafficService
from app.state.manager import StateManager


class VisionService:
    """Optional YOLOv8 + ByteTrack worker that feeds observations into traffic analytics."""

    _COCO_VEHICLES = {2: VehicleClass.CAR, 3: VehicleClass.MOTORCYCLE, 5: VehicleClass.BUS, 7: VehicleClass.TRUCK}

    def __init__(self, state: StateManager, traffic: TrafficService, settings: Settings, backend_root: Path) -> None:
        self._state = state
        self._traffic = traffic
        self._model_path = self._resolve_path(settings.vision_model_path, backend_root)
        self._uploads = self._resolve_path(settings.upload_directory, backend_root)
        self._uploads.mkdir(parents=True, exist_ok=True)
        self._ultralytics_config = backend_root / "data" / "ultralytics"
        self._ultralytics_config.mkdir(parents=True, exist_ok=True)
        self._model: Any | None = None
        self._model_lock = Lock()

    @staticmethod
    def _resolve_path(value: str, backend_root: Path) -> Path:
        path = Path(value)
        return path if path.is_absolute() else backend_root / path

    def status(self) -> dict[str, object]:
        if not self._model_path.is_file():
            return {"status": "MODEL_NOT_INSTALLED", "model_path": str(self._model_path), "message": "Place yolov8n.pt at the configured model path to enable video processing."}
        try:
            self._imports()
        except Exception as exc:
            return {"status": "RUNTIME_UNAVAILABLE", "model_path": str(self._model_path), "message": f"Vision runtime is unavailable: {exc}"}
        return {"status": "READY", "model_path": str(self._model_path), "message": "YOLOv8 and OpenCV runtime available."}

    def queue_video(self, file_path: Path) -> None:
        self._state.update("video", {"status": "QUEUED", "file_name": file_path.name, "frames_processed": 0})
        self._state.add_log(f"Video queued for vision processing: {file_path.name}")

    def create_upload_destination(self, suffix: str) -> Path:
        return self._uploads / f"{uuid4().hex}{suffix}"

    def process_video(self, file_path: Path) -> None:
        self._state.merge("system_health", {"vision": "processing"})
        self._state.merge("video", {"status": "PROCESSING"})
        started_at = perf_counter()
        try:
            cv2, _ = self._imports()
            model = self._load_model()
            capture = cv2.VideoCapture(str(file_path))
            if not capture.isOpened():
                raise RuntimeError("OpenCV could not open the uploaded video")
            frame_number = 0
            processed = 0
            last_observations: list[VehicleObservation] = []
            while True:
                success, frame = capture.read()
                if not success:
                    break
                frame_number += 1
                if frame_number % 5:
                    continue
                processed += 1
                last_observations = self._detect_frame(model, frame)
                self._traffic.process_frame(TrafficFrameRequest(observations=last_observations))
                self._state.merge("video", {"frames_processed": processed, "last_frame": frame_number})
            capture.release()
            elapsed = max(perf_counter() - started_at, 0.001)
            self._state.update("video", {
                "status": "COMPLETED", "file_name": file_path.name, "frames_processed": processed,
                "fps": round(processed / elapsed, 2), "last_observation_count": len(last_observations),
            })
            self._state.merge("system_health", {"vision": "healthy"})
            self._state.add_log(f"Vision processing completed: {processed} sampled frames from {file_path.name}")
        except Exception as exc:
            self._state.update("video", {"status": "FAILED", "file_name": file_path.name, "error": str(exc)})
            self._state.merge("system_health", {"vision": "degraded"})
            self._state.add_log(f"Vision processing failed: {exc}", level="WARNING")

    def _load_model(self) -> Any:
        with self._model_lock:
            if self._model is None:
                _, YOLO = self._imports()
                self._model = YOLO(str(self._model_path))
            return self._model

    def _imports(self) -> tuple[Any, Any]:
        os.environ.setdefault("YOLO_CONFIG_DIR", str(self._ultralytics_config))
        import cv2
        from ultralytics import YOLO
        return cv2, YOLO

    def _detect_frame(self, model: Any, frame: Any) -> list[VehicleObservation]:
        height, width = frame.shape[:2]
        results = model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)
        observations: list[VehicleObservation] = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for index, class_id in enumerate(boxes.cls.tolist()):
                vehicle_class = self._COCO_VEHICLES.get(int(class_id))
                if vehicle_class is None:
                    continue
                x1, y1, x2, y2 = boxes.xyxy[index].tolist()
                track_id = int(boxes.id[index].item()) if boxes.id is not None else index
                observations.append(VehicleObservation(
                    tracking_id=f"yolo-{track_id}", vehicle_class=vehicle_class,
                    confidence=round(float(boxes.conf[index].item()), 4),
                    bbox=BoundingBox(x1=max(0, x1 / width), y1=max(0, y1 / height), x2=min(1, x2 / width), y2=min(1, y2 / height)),
                ))
        return observations
