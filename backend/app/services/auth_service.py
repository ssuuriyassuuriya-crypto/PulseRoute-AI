from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.config import Settings
from app.constants.roles import Role
from app.schemas.auth import AuthenticatedUser, LoginData


class AuthenticationError(Exception):
    """Raised when credentials or a bearer token are invalid."""


class AuthService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._users = {
            "admin": {"password_hash": self._hash("admin123"), "role": Role.ADMIN},
            "driver": {"password_hash": self._hash("driver123"), "role": Role.AMBULANCE_DRIVER},
        }

    @staticmethod
    def _hash(password: str) -> bytes:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def login(self, username: str, password: str) -> LoginData:
        record = self._users.get(username.lower())
        if record is None or not bcrypt.checkpw(password.encode(), record["password_hash"]):
            raise AuthenticationError("Invalid username or password")
        user = AuthenticatedUser(username=username.lower(), role=record["role"])
        expires_at = datetime.now(UTC) + timedelta(minutes=self._settings.jwt_expiry_minutes)
        token = jwt.encode(
            {"sub": user.username, "role": user.role.value, "exp": expires_at},
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )
        return LoginData(access_token=token, user=user)

    def authenticate_token(self, token: str) -> AuthenticatedUser:
        try:
            payload = jwt.decode(token, self._settings.jwt_secret, algorithms=[self._settings.jwt_algorithm])
            username, role = payload.get("sub"), payload.get("role")
            if not isinstance(username, str) or not isinstance(role, str):
                raise AuthenticationError("Malformed access token")
            return AuthenticatedUser(username=username, role=Role(role))
        except (JWTError, ValueError) as exc:
            raise AuthenticationError("Invalid or expired access token") from exc
