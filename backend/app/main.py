import asyncio
from contextlib import asynccontextmanager, suppress
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import analytics, auth, demo, emergency, health, reports, signals, timeline, traffic, websocket
from app.config import settings
from app.schemas.common import ErrorResponse
from app.services.auth_service import AuthService
from app.services.ai_decision_service import AIDecisionService
from app.services.traffic_service import TrafficService
from app.services.signal_service import AdaptiveSignalService
from app.services.map_service import MapService
from app.services.green_corridor_service import GreenCorridorService
from app.services.simulation_service import GpsSimulationService
from app.services.emergency_service import EmergencyService
from app.services.report_service import ReportService
from app.services.websocket_service import DashboardConnectionManager
from app.services.demo_control_service import DemoControlService
from app.services.vision_service import VisionService
from pathlib import Path
from app.state.manager import StateManager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.state_manager = StateManager()
    app.state.auth_service = AuthService(settings)
    app.state.traffic_service = TrafficService(app.state.state_manager, AIDecisionService())
    app.state.vision_service = VisionService(app.state.state_manager, app.state.traffic_service, settings, Path(__file__).resolve().parents[1])
    app.state.signal_service = AdaptiveSignalService(app.state.state_manager)
    app.state.signal_service.initialize()
    map_service = MapService(Path(__file__).resolve().parents[1] / "routes_data" / "hospital_route.json")
    gps_service = GpsSimulationService(app.state.state_manager, map_service)
    corridor_service = GreenCorridorService(app.state.state_manager, app.state.signal_service)
    app.state.emergency_service = EmergencyService(app.state.state_manager, gps_service, corridor_service, map_service)
    app.state.demo_control_service = DemoControlService(app.state.state_manager, app.state.traffic_service, app.state.signal_service, app.state.emergency_service)
    app.state.report_service = ReportService(app.state.state_manager)
    app.state.websocket_manager = DashboardConnectionManager()
    app.state.state_manager.merge("system_health", {"websocket": "healthy", "vision": str(app.state.vision_service.status()["status"]).lower()})
    app.state.state_manager.add_log("PulseRoute platform core initialized")
    async def signal_loop() -> None:
        while True:
            app.state.signal_service.tick()
            await asyncio.sleep(1)

    async def gps_loop() -> None:
        while True:
            app.state.emergency_service.tick()
            await asyncio.sleep(1)

    async def broadcast_loop() -> None:
        while True:
            await app.state.websocket_manager.broadcast(app.state.state_manager.snapshot())
            await asyncio.sleep(1)

    scheduler_task = asyncio.create_task(signal_loop())
    gps_task = asyncio.create_task(gps_loop())
    broadcast_task = asyncio.create_task(broadcast_loop())
    try:
        yield
    finally:
        scheduler_task.cancel()
        gps_task.cancel()
        broadcast_task.cancel()
        with suppress(asyncio.CancelledError):
            await scheduler_task
        with suppress(asyncio.CancelledError):
            await gps_task
        with suppress(asyncio.CancelledError):
            await broadcast_task


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(traffic.router, prefix=settings.api_prefix)
app.include_router(analytics.router, prefix=settings.api_prefix)
app.include_router(signals.router, prefix=settings.api_prefix)
app.include_router(emergency.router, prefix=settings.api_prefix)
app.include_router(timeline.router, prefix=settings.api_prefix)
app.include_router(reports.router, prefix=settings.api_prefix)
app.include_router(websocket.router)
app.include_router(demo.router, prefix=settings.api_prefix)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content=ErrorResponse(error=str(exc.errors())).model_dump())


@app.exception_handler(Exception)
async def unhandled_error_handler(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content=ErrorResponse(error="Internal server error").model_dump())
