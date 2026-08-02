from pydantic import BaseModel, Field

from app.constants.roles import Role


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class AuthenticatedUser(BaseModel):
    username: str
    role: Role


class LoginData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthenticatedUser
