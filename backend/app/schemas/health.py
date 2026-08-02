from typing import Literal

from pydantic import BaseModel


class HealthData(BaseModel):
    status: Literal["healthy"] = "healthy"
    services: dict[str, str]
