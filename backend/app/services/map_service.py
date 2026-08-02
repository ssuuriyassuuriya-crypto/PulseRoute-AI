import json
from math import asin, cos, radians, sin, sqrt
from pathlib import Path

from app.schemas.traffic import Road


class RoutePoint:
    def __init__(self, junction: str, road: Road, latitude: float, longitude: float) -> None:
        self.junction = junction
        self.road = road
        self.latitude = latitude
        self.longitude = longitude


class MapService:
    """Provides an offline route and distance calculations for the GPS simulator."""

    def __init__(self, route_file: Path) -> None:
        data = json.loads(route_file.read_text(encoding="utf-8"))
        self.hospital = data["hospital"]
        self.route = [
            RoutePoint(item["junction"], Road(item["road"]), item["latitude"], item["longitude"])
            for item in data["route"]
        ]
        if len(self.route) < 2:
            raise ValueError("A hospital route must contain at least two points")

    @staticmethod
    def distance_meters(first: RoutePoint, second: RoutePoint) -> float:
        radius_meters = 6_371_000
        latitude_delta = radians(second.latitude - first.latitude)
        longitude_delta = radians(second.longitude - first.longitude)
        a = sin(latitude_delta / 2) ** 2 + cos(radians(first.latitude)) * cos(radians(second.latitude)) * sin(longitude_delta / 2) ** 2
        return 2 * radius_meters * asin(sqrt(a))

    def remaining_distance(self, index: int) -> float:
        return sum(self.distance_meters(self.route[position], self.route[position + 1]) for position in range(index, len(self.route) - 1))
