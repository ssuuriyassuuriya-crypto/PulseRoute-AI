"""
PulseRoute AI - Analytics & Decision Intelligence API Endpoints
"""
from fastapi import APIRouter
from backend.services.analytics_service import analytics_service
from backend.state.state_manager import state_manager
from backend.services.report_service import report_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/junction/{junction_id}")
def get_analytics(junction_id: str):
    snapshot = state_manager.get_full_snapshot()
    j_data = snapshot["junctions"].get(junction_id)
    if not j_data:
        return {"error": "Junction not found"}
        
    return analytics_service.compute_junction_analytics(junction_id, j_data["name"], j_data["counts"])

@router.get("/reports")
def get_reports():
    return report_service.get_all_reports()
