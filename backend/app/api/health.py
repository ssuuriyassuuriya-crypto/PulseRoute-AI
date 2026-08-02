from fastapi import APIRouter, Request

from app.schemas.common import SuccessResponse
from app.schemas.health import HealthData
from app.state.manager import StateManager

router = APIRouter(tags=["health"])


@router.get("/health", response_model=SuccessResponse)
@router.get("/status", response_model=SuccessResponse)
def health(request: Request) -> SuccessResponse:
    state: StateManager = request.app.state.state_manager
    data = HealthData(services=state.get("system_health"))
    return SuccessResponse(message="PulseRoute backend is healthy", data=data.model_dump())


@router.get("/health/model", response_model=SuccessResponse)
def model_health(request: Request) -> SuccessResponse:
    return SuccessResponse(data=request.app.state.vision_service.status())


@router.get("/health/websocket", response_model=SuccessResponse)
def websocket_health(request: Request) -> SuccessResponse:
    manager = request.app.state.websocket_manager
    return SuccessResponse(data={"status": "healthy", "connections": manager.connection_count})
