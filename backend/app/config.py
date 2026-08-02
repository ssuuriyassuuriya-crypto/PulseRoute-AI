from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "PulseRoute AI"
    api_prefix: str = "/api"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 480
    jwt_secret: str = "pulseroute-local-development-secret-change-before-deployment"
    vision_model_path: str = "models/yolov8n.pt"
    upload_directory: str = "data/uploads"
    cors_origins: tuple[str, ...] = ("http://127.0.0.1:5173", "http://localhost:5173")

    @classmethod
    def from_environment(cls) -> "Settings":
        origins = tuple(origin.strip() for origin in os.getenv("PULSEROUTE_CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(",") if origin.strip())
        return cls(
            jwt_secret=os.getenv("PULSEROUTE_JWT_SECRET", "pulseroute-local-development-secret-change-before-deployment"),
            jwt_expiry_minutes=int(os.getenv("PULSEROUTE_JWT_EXPIRY_MINUTES", "480")),
            vision_model_path=os.getenv("PULSEROUTE_VISION_MODEL_PATH", "models/yolov8n.pt"),
            upload_directory=os.getenv("PULSEROUTE_UPLOAD_DIRECTORY", "data/uploads"),
            cors_origins=origins,
        )


settings = Settings.from_environment()
