"""
PulseRoute AI - Authentication API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from backend.schemas.login import LoginRequest, LoginResponse
from backend.models.database import USERS
from backend.auth.jwt_handler import create_access_token, verify_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    user = USERS.get(req.username.lower())
    if not user or user["password_hash"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    token = create_access_token(user["username"], user["role"])
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        role=user["role"],
        username=user["username"],
        name=user["name"]
    )

@router.get("/me")
def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Expired or invalid token")
    return payload
