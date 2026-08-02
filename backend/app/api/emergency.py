from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.dependencies import current_user
from app.schemas.auth import AuthenticatedUser
from app.schemas.common import SuccessResponse
from app.schemas.emergency import StartMissionRequest
from app.services.emergency_service import EmergencyService, MissionStateError

router = APIRouter(prefix="/emergency", tags=["emergency"])


def get_emergency_service(request: Request) -> EmergencyService:
    return request.app.state.emergency_service


@router.get("/status", response_model=SuccessResponse)
def status(
    _: Annotated[AuthenticatedUser, Depends(current_user)],
    service: Annotated[EmergencyService, Depends(get_emergency_service)],
) -> SuccessResponse:
    return SuccessResponse(data=service.snapshot().model_dump())


@router.post("/start", response_model=SuccessResponse)
def start(
    payload: StartMissionRequest,
    user: Annotated[AuthenticatedUser, Depends(current_user)],
    service: Annotated[EmergencyService, Depends(get_emergency_service)],
) -> SuccessResponse:
    try:
        result = service.start(user.username, payload)
    except MissionStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return SuccessResponse(message="Emergency mission started", data=result.model_dump())


@router.post("/stop", response_model=SuccessResponse)
def stop(
    _: Annotated[AuthenticatedUser, Depends(current_user)],
    service: Annotated[EmergencyService, Depends(get_emergency_service)],
) -> SuccessResponse:
    try:
        result = service.stop()
    except MissionStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return SuccessResponse(message="Emergency mission stopped", data=result.model_dump())


@router.post("/priority", response_model=SuccessResponse)
def priority(
    _: Annotated[AuthenticatedUser, Depends(current_user)],
    service: Annotated[EmergencyService, Depends(get_emergency_service)],
) -> SuccessResponse:
    try:
        result = service.request_priority()
    except MissionStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return SuccessResponse(message="High priority enabled", data=result.model_dump())
