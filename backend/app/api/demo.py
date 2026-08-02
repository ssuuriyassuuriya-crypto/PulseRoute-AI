from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.dependencies import require_role
from app.constants.traffic import ADMIN_ONLY
from app.schemas.auth import AuthenticatedUser
from app.schemas.common import SuccessResponse
from app.services.demo_control_service import DemoControlService
from app.services.emergency_service import MissionStateError

router = APIRouter(prefix="/demo", tags=["demo controls"])


def get_demo_service(request: Request) -> DemoControlService:
    return request.app.state.demo_control_service


@router.post("/play-traffic", response_model=SuccessResponse)
def play_traffic(_: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))], service: Annotated[DemoControlService, Depends(get_demo_service)]) -> SuccessResponse:
    return SuccessResponse(message="Demo traffic playing", data=service.play_traffic())


@router.post("/trigger-emergency", response_model=SuccessResponse)
def trigger_emergency(_: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))], service: Annotated[DemoControlService, Depends(get_demo_service)]) -> SuccessResponse:
    try:
        return SuccessResponse(message="Demo emergency started", data=service.trigger_emergency())
    except MissionStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/stop-emergency", response_model=SuccessResponse)
def stop_emergency(_: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))], service: Annotated[DemoControlService, Depends(get_demo_service)]) -> SuccessResponse:
    return SuccessResponse(message="Demo emergency stopped", data=service.stop_emergency())


@router.post("/reset-simulation", response_model=SuccessResponse)
def reset_simulation(_: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))], service: Annotated[DemoControlService, Depends(get_demo_service)]) -> SuccessResponse:
    return SuccessResponse(message="Simulation reset", data=service.reset_simulation())


@router.post("/clear-logs", response_model=SuccessResponse)
def clear_logs(_: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))], service: Annotated[DemoControlService, Depends(get_demo_service)]) -> SuccessResponse:
    service.clear_logs()
    return SuccessResponse(message="Timeline cleared")
