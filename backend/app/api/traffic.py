from typing import Annotated

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, UploadFile, status

from app.api.dependencies import require_role
from app.constants.traffic import ADMIN_ONLY
from app.schemas.auth import AuthenticatedUser
from app.schemas.common import SuccessResponse
from app.schemas.traffic import TrafficFrameRequest
from app.services.traffic_service import TrafficService
from app.services.vision_service import VisionService
from app.state.manager import StateManager

router = APIRouter(prefix="/traffic", tags=["traffic"])


def get_traffic_service(request: Request) -> TrafficService:
    return request.app.state.traffic_service


def get_vision_service(request: Request) -> VisionService:
    return request.app.state.vision_service


@router.post("/observations", response_model=SuccessResponse)
def submit_observations(
    frame: TrafficFrameRequest,
    _: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))],
    service: Annotated[TrafficService, Depends(get_traffic_service)],
) -> SuccessResponse:
    result = service.process_frame(frame)
    return SuccessResponse(message="Traffic frame processed", data=result.model_dump())


@router.post("/demo", response_model=SuccessResponse)
def generate_demo_traffic(
    _: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))],
    service: Annotated[TrafficService, Depends(get_traffic_service)],
) -> SuccessResponse:
    return SuccessResponse(message="Demo traffic frame generated", data=service.generate_demo_frame().model_dump())


@router.post("/upload", response_model=SuccessResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_video(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    _: AuthenticatedUser = Depends(require_role(*ADMIN_ONLY)),
    service: VisionService = Depends(get_vision_service),
) -> SuccessResponse:
    if not video.content_type or not video.content_type.startswith("video/"):
        raise HTTPException(status_code=415, detail="Only video uploads are supported")
    suffix = Path(video.filename or "upload.mp4").suffix.lower() or ".mp4"
    if suffix not in {".mp4", ".avi", ".mov", ".mkv"}:
        raise HTTPException(status_code=415, detail="Supported formats: MP4, AVI, MOV, MKV")
    destination = service.create_upload_destination(suffix)
    with destination.open("wb") as handle:
        while chunk := await video.read(1024 * 1024):
            handle.write(chunk)
    await video.close()
    service.queue_video(destination)
    background_tasks.add_task(service.process_video, destination)
    return SuccessResponse(message="Video accepted for background processing", data={"file_name": destination.name, "vision": service.status()})


@router.get("/video", response_model=SuccessResponse)
def video_status(
    _: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))],
    request: Request,
    service: Annotated[VisionService, Depends(get_vision_service)],
) -> SuccessResponse:
    return SuccessResponse(data={"video": request.app.state.state_manager.get("video"), "vision": service.status()})


@router.get("/snapshot", response_model=SuccessResponse)
def traffic_snapshot(
    _: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))], request: Request
) -> SuccessResponse:
    state: StateManager = request.app.state.state_manager
    return SuccessResponse(data={"roads": state.get("roads"), "metrics": state.get("metrics")})
