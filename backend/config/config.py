"""
PulseRoute AI - Configuration Settings
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "uploads")
ROUTES_DIR = os.path.join(BASE_DIR, "routes_data")

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(ROUTES_DIR, exist_ok=True)

JWT_SECRET = "pulseroute_super_secret_hackathon_jwt_key_2026"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

YOLO_MODEL_NAME = "yolov8n.pt" # Nano model for fast CPU inference
CONFIDENCE_THRESHOLD = 0.4
