from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.dependencies import require_role
from app.constants.traffic import ADMIN_ONLY
from app.schemas.auth import AuthenticatedUser
from app.schemas.common import SuccessResponse
from app.state.manager import StateManager

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=SuccessResponse)
def get_analytics(
    _: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))], request: Request
) -> SuccessResponse:
    state: StateManager = request.app.state.state_manager
    return SuccessResponse(data={"analytics": state.get("analytics"), "decision": state.get("ai_decision")})
