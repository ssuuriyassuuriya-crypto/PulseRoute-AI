from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.constants.roles import Role
from app.services.auth_service import AuthenticationError
from app.services.websocket_service import DashboardConnectionManager
from app.state.manager import StateManager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/dashboard")
async def dashboard_socket(socket: WebSocket) -> None:
    token = socket.query_params.get("token")
    if not token:
        await socket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Bearer token required")
        return
    try:
        user = socket.app.state.auth_service.authenticate_token(token)
    except AuthenticationError:
        await socket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid access token")
        return
    if user.role != Role.ADMIN:
        await socket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Admin role required")
        return

    manager: DashboardConnectionManager = socket.app.state.websocket_manager
    state: StateManager = socket.app.state.state_manager
    await manager.connect(socket)
    try:
        await socket.send_json(state.snapshot())
        while True:
            await socket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(socket)
