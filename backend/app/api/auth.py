from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.dependencies import current_user, get_auth_service
from app.schemas.auth import AuthenticatedUser, LoginData, LoginRequest
from app.schemas.common import SuccessResponse
from app.services.auth_service import AuthenticationError, AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=SuccessResponse)
def login(payload: LoginRequest, auth_service: Annotated[AuthService, Depends(get_auth_service)]) -> SuccessResponse:
    try:
        result: LoginData = auth_service.login(payload.username, payload.password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return SuccessResponse(message="Login successful", data=result.model_dump())


@router.get("/me", response_model=SuccessResponse)
def me(user: Annotated[AuthenticatedUser, Depends(current_user)]) -> SuccessResponse:
    return SuccessResponse(data=user.model_dump())
