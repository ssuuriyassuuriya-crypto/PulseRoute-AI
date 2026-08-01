"""
PulseRoute AI - Traffic Video Upload & Detection API Endpoints
"""
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config.config import MEDIA_DIR
from backend.services.yolo_service import yolo_service
from backend.state.state_manager import state_manager

router = APIRouter(prefix="/api/traffic", tags=["Traffic"])

@router.post("/upload")
async def upload_traffic_video(file: UploadFile = File(...)):
    if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="Invalid video format. Supported: mp4, avi, mov, mkv")
        
    save_path = os.path.join(MEDIA_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    state_manager.add_timeline_event("VIDEO_UPLOAD", f"Uploaded new traffic video: {file.filename}")
    return {"message": "Traffic video uploaded successfully", "filename": file.filename, "path": save_path}

@router.get("/detect/{junction_id}")
def get_junction_detections(junction_id: str):
    res = yolo_service.process_frame_simulation(junction_id)
    state_manager.update_junction_counts(junction_id, res["counts"])
    return res
