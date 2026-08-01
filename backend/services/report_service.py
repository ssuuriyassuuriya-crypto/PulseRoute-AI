"""
PulseRoute AI - Report & Session KPI Generator Service
"""
import time
from backend.models.database import REPORTS_DB

class ReportService:
    def generate_session_report(self) -> dict:
        report_id = f"RPT-{int(time.time())}"
        report_data = {
            "session_id": report_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_vehicles_processed": 1420,
            "avg_wait_time_reduction_pct": 34.5,
            "total_emergency_corridors_opened": 3,
            "ambulance_delay_saved_minutes": 8.4,
            "junction_efficiency_score": 94.2
        }
        REPORTS_DB.append(report_data)
        return report_data

    def get_all_reports(self):
        if not REPORTS_DB:
            self.generate_session_report()
        return REPORTS_DB

report_service = ReportService()
