from app.constants.roles import Role

ROAD_NAMES = ("North", "South", "East", "West")
VEHICLE_CLASSES = ("car", "bus", "truck", "motorcycle")
LOW_CONGESTION_MAX_VEHICLES = 15
MEDIUM_CONGESTION_MAX_VEHICLES = 35
AVERAGE_VEHICLE_LENGTH_METERS = 5.0
GREEN_SECONDS_BY_CONGESTION = {"LOW": 20, "MEDIUM": 35, "HIGH": 50}
ADMIN_ONLY = (Role.ADMIN,)
