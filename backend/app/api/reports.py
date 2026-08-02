from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.dependencies import require_role
from app.constants.traffic import ADMIN_ONLY
from app.schemas.auth import AuthenticatedUser
from app.schemas.common import SuccessResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_service(request: Request) -> ReportService:
    return request.app.state.report_service


@router.get("", response_model=SuccessResponse)
def get_report(
    _: Annotated[AuthenticatedUser, Depends(require_role(*ADMIN_ONLY))],
    service: Annotated[ReportService, Depends(get_report_service)],
) -> SuccessResponse:
    return SuccessResponse(data=service.generate())
