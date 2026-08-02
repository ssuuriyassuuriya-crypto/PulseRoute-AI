from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.dependencies import require_role
from app.constants.traffic import ADMIN_ONLY
from app.schemas.auth import AuthenticatedUser
from app.schemas.common import SuccessResponse
from app.schemas.signals import ManualOverrideRequest
from app.services.signal_service import AdaptiveSignalService, SignalStateError

router = APIRouter(prefix="/signals", tags=["signals"])


def get_signal_service(request: Request) -> AdaptiveSignalService:
    return request.app.state.signal_service


@router.get("", response_model=SuccessResponse)
def get_signals(
    _: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))],
    service: Annotated[AdaptiveSignalService, Depends(get_signal_service)],
) -> SuccessResponse:
    return SuccessResponse(data=service.tick().model_dump())


@router.post("/override", response_model=SuccessResponse)
def override_signal(
    payload: ManualOverrideRequest,
    _: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))],
    service: Annotated[AdaptiveSignalService, Depends(get_signal_service)],
) -> SuccessResponse:
    try:
        snapshot = service.manual_override(payload)
    except SignalStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return SuccessResponse(message="Manual signal override active", data=snapshot.model_dump())


@router.post("/reset", response_model=SuccessResponse)
def reset_signals(
    _: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))],
    service: Annotated[AdaptiveSignalService, Depends(get_signal_service)],
) -> SuccessResponse:
    return SuccessResponse(message="Adaptive signal mode restored", data=service.reset_adaptive_mode().model_dump())
