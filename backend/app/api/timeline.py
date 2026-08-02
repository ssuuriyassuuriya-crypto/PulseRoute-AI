from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies import require_role
from app.constants.traffic import ADMIN_ONLY
from app.schemas.auth import AuthenticatedUser
from app.schemas.common import SuccessResponse
from app.state.manager import StateManager

router = APIRouter(prefix="/timeline", tags=["timeline"])


@router.get("", response_model=SuccessResponse)
def get_timeline(
    _: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))],
    request: Request,
    limit: int = Query(default=50, ge=1, le=250),
) -> SuccessResponse:
    state: StateManager = request.app.state.state_manager
    return SuccessResponse(data=state.get("logs")[-limit:])
