"""
EduRisk AI — Explainable Student Risk Prediction and Intervention Management System
Main Application Entry Point.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from presentation.components.header import apply_theme, render_sidebar
from application.services.analytics_service import AnalyticsService

st.set_page_config(
    page_title="EduRisk AI — Enterprise Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar()

# Hero Header
st.markdown(
    """
    <div class="main-header">
        <h1>🎓 EduRisk AI</h1>
        <p>Explainable Student Risk Prediction and Intervention Management System — YottaFlex Hackathon Edition</p>
    </div>
    """,
    unsafe_allow_html=True
)

user = st.session_state.get("current_user", {})
st.info(f"👋 Welcome back, **{user.get('name', 'User')}**! You are operating with the **{user.get('role', 'Platform Administrator')}** profile.")

# Fetch real database stats
try:
    analytics = AnalyticsService()
    kpis = analytics.get_executive_kpis()
except Exception as exc:
    st.warning(f"Database connection note: {exc}. Run starter generation or verify database initialization.")
    kpis = {
        "total_students": 0,
        "total_courses": 0,
        "total_enrollments": 0,
        "high_risk_count": 0,
        "medium_risk_count": 0,
        "low_risk_count": 0,
        "open_support_cases": 0,
        "active_interventions": 0,
        "intervention_success_rate": 0.0,
        "average_attendance": 0.0
    }

# High-Level Quick Metrics
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Enrolled</div>
            <div class="kpi-value">{kpis['total_students']:,}</div>
            <div class="kpi-delta" style="color: #3B82F6;">Across {kpis['total_courses']} Courses</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">High Risk</div>
            <div class="kpi-value" style="color: #EF4444;">{kpis['high_risk_count']:,}</div>
            <div class="kpi-delta" style="color: #EF4444;">Requires Immediate Action</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Open Cases</div>
            <div class="kpi-value">{kpis['open_support_cases']:,}</div>
            <div class="kpi-delta" style="color: #F59E0B;">In Support Triage</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Active Interventions</div>
            <div class="kpi-value">{kpis['active_interventions']:,}</div>
            <div class="kpi-delta" style="color: #10B981;">{kpis['intervention_success_rate']}% Success Rate</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Attendance</div>
            <div class="kpi-value">{kpis['average_attendance']:.1f}%</div>
            <div class="kpi-delta" style="color: #3B82F6;">Institution Baseline</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# System Architecture & Feature Navigation Cards
st.subheader("System Modules & Architecture")
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    st.markdown(
        """
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; min-height: 170px;">
            <h4 style="margin: 0 0 8px 0; color: #1E3A8A;">📊 Executive Dashboard</h4>
            <p style="font-size: 13px; color: #64748B; margin: 0 0 12px 0;">Executive KPI scorecards, risk distributions, longitudinal attendance, and course heatmaps.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Dashboard", key="btn_nav_dash"):
        st.switch_page("pages/01_Executive_Dashboard.py")

with nav_col2:
    st.markdown(
        """
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; min-height: 170px;">
            <h4 style="margin: 0 0 8px 0; color: #1E3A8A;">👤 Student 360 Profile</h4>
            <p style="font-size: 13px; color: #64748B; margin: 0 0 12px 0;">Searchable student directory, academic transcripts, weekly attendance, and LMS timeline.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Students", key="btn_nav_stu"):
        st.switch_page("pages/02_Student_Management.py")

with nav_col3:
    st.markdown(
        """
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; min-height: 170px;">
            <h4 style="margin: 0 0 8px 0; color: #1E3A8A;">🔍 Explainable Risk</h4>
            <p style="font-size: 13px; color: #64748B; margin: 0 0 12px 0;">Explainable factor breakdowns, cutoff date selectors (temporal safety), and prediction engines.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Risk Engine", key="btn_nav_risk"):
        st.switch_page("pages/03_Risk_Analysis.py")

with nav_col4:
    st.markdown(
        """
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; min-height: 170px;">
            <h4 style="margin: 0 0 8px 0; color: #1E3A8A;">🛡️ Interventions & Triage</h4>
            <p style="font-size: 13px; color: #64748B; margin: 0 0 12px 0;">Case escalation pipelines, 7 intervention workflows, and longitudinal efficacy evaluation.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Interventions", key="btn_nav_int"):
        st.switch_page("pages/05_Interventions.py")

st.markdown("<br>", unsafe_allow_html=True)
sub_col1, sub_col2, sub_col3, sub_col4 = st.columns(4)

with sub_col1:
    st.markdown(
        """
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; min-height: 170px;">
            <h4 style="margin: 0 0 8px 0; color: #1E3A8A;">⚙️ Synthetic Generator</h4>
            <p style="font-size: 13px; color: #64748B; margin: 0 0 12px 0;">Configurable Starter (100) and Full-Scale (5,000) dataset generation with seed <code>20261022</code>.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Generator", key="btn_nav_gen"):
        st.switch_page("pages/06_Data_Generator.py")

with sub_col2:
    st.markdown(
        """
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; min-height: 170px;">
            <h4 style="margin: 0 0 8px 0; color: #1E3A8A;">✅ Anomaly & Quality</h4>
            <p style="font-size: 13px; color: #64748B; margin: 0 0 12px 0;">Detection for all 5 negative scenarios, reconciliation reports, and ground-truth verification.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Data Quality", key="btn_nav_dq"):
        st.switch_page("pages/07_Data_Quality.py")

with sub_col3:
    st.markdown(
        """
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; min-height: 170px;">
            <h4 style="margin: 0 0 8px 0; color: #1E3A8A;">📁 Export Center</h4>
            <p style="font-size: 13px; color: #64748B; margin: 0 0 12px 0;">Direct downloads for CSV, JSON, and SQL schema & seed datasets across all 10 domain entities.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Exports", key="btn_nav_rep"):
        st.switch_page("pages/08_Reports.py")

with sub_col4:
    st.markdown(
        """
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; min-height: 170px;">
            <h4 style="margin: 0 0 8px 0; color: #1E3A8A;">📋 Support Cases</h4>
            <p style="font-size: 13px; color: #64748B; margin: 0 0 12px 0;">Support case management, staff assignments, status pipelines, and case triage history.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Support Cases", key="btn_nav_sup"):
        st.switch_page("pages/04_Support_Cases.py")

