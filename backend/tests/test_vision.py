from pathlib import Path

from app.config import Settings
from app.services.ai_decision_service import AIDecisionService
from app.services.traffic_service import TrafficService
from app.services.vision_service import VisionService
from app.state.manager import StateManager


def test_vision_status_is_explicit_when_model_is_not_installed(tmp_path: Path) -> None:
    state = StateManager()
    service = VisionService(state, TrafficService(state, AIDecisionService()), Settings(vision_model_path="missing.pt", upload_directory="uploads"), tmp_path)
    assert service.status()["status"] == "MODEL_NOT_INSTALLED"
