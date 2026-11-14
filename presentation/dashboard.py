"""
Presentation Dashboard Module
Central dashboard utility bridging Streamlit views with Tier 2 services.
"""

from typing import Dict, Any
from application.services.analytics_service import AnalyticsService
from application.services.risk_service import RiskService
from application.services.student_service import StudentService


class PresentationDashboard:
    def __init__(self):
        self.analytics = AnalyticsService()
        self.risk_service = RiskService()
        self.student_service = StudentService()

    def get_kpis(self) -> Dict[str, Any]:
        return self.analytics.get_executive_kpis()

    def get_risk_chart_data(self) -> Dict[str, int]:
        return self.analytics.get_risk_distribution()

