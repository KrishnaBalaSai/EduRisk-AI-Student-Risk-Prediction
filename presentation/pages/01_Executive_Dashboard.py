"""
Page 01: Executive Dashboard
Presents all 10 institutional KPIs and 7 interactive Plotly visualizations derived directly from live database records.
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Add project root to sys.path
# Robust project root resolution
_curr = Path(__file__).resolve()
while _curr.name != 'EduRisk-AI' and _curr.parent != _curr:
    _curr = _curr.parent
project_root = _curr
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from presentation.components.header import apply_theme, render_sidebar
from application.services.analytics_service import AnalyticsService

st.set_page_config(page_title="Executive Dashboard — EduRisk AI", page_icon="📊", layout="wide")
apply_theme()
render_sidebar()

st.title("📊 Institutional Executive Dashboard")
st.markdown("Live macro-level indicators across student retention, academic performance, and intervention efficacy.")

analytics = AnalyticsService()
kpis = analytics.get_executive_kpis()

# Render 10 KPIs in 2 clean rows
r1_col1, r1_col2, r1_col3, r1_col4, r1_col5 = st.columns(5)
with r1_col1:
    st.metric("Total Students", f"{kpis['total_students']:,}", "Enrolled Cohorts")
with r1_col2:
    st.metric("Total Courses", f"{kpis['total_courses']:,}", "Active Curriculum")
with r1_col3:
    st.metric("Total Enrollments", f"{kpis['total_enrollments']:,}", "Course Registrations")
with r1_col4:
    st.metric("High-Risk Students", f"{kpis['high_risk_count']:,}", "Critical Priority", delta_color="inverse")
with r1_col5:
    st.metric("Medium-Risk Students", f"{kpis['medium_risk_count']:,}", "Monitoring Queue")

r2_col1, r2_col2, r2_col3, r2_col4, r2_col5 = st.columns(5)
with r2_col1:
    st.metric("Low-Risk Students", f"{kpis['low_risk_count']:,}", "Satisfactory Standing")
with r2_col2:
    st.metric("Open Support Cases", f"{kpis['open_support_cases']:,}", "Pending Resolution")
with r2_col3:
    st.metric("Active Interventions", f"{kpis['active_interventions']:,}", "In Flight")
with r2_col4:
    st.metric("Intervention Success", f"{kpis['intervention_success_rate']:.1f}%", "Positive Engagement")
with r2_col5:
    st.metric("Average Attendance", f"{kpis['average_attendance']:.1f}%", "Eligible Sessions")

st.markdown("---")

# Chart Row 1: Risk Distribution (Chart 1) & Attendance Longitudinal Trend (Chart 2)
c1_col, c2_col = st.columns([1, 2])

with c1_col:
    st.subheader("1. Student Risk Distribution")
    risk_dist = analytics.get_risk_distribution()
    df_risk = pd.DataFrame([
        {"Category": cat, "Count": count} for cat, count in risk_dist.items()
    ])
    fig_risk = px.pie(
        df_risk,
        names="Category",
        values="Count",
        color="Category",
        color_discrete_map={
            "Low Risk": "#10B981",
            "Medium Risk": "#F59E0B",
            "High Risk": "#EF4444"
        },
        hole=0.45,
    )
    fig_risk.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320)
    st.plotly_chart(fig_risk, use_container_width=True)

with c2_col:
    st.subheader("2. Longitudinal Attendance Trends")
    att_trends = analytics.get_attendance_trends()
    if att_trends:
        df_att = pd.DataFrame(att_trends)
        fig_att = px.line(
            df_att,
            x="date",
            y=["Present", "Late", "Absent_Unapproved", "Absent_Approved"],
            color_discrete_map={
                "Present": "#10B981",
                "Late": "#F59E0B",
                "Absent_Unapproved": "#EF4444",
                "Absent_Approved": "#60A5FA"
            },
            labels={"value": "Session Count", "date": "Date"}
        )
        fig_att.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_att, use_container_width=True)
    else:
        st.info("No attendance trends available. Generate dataset first.")

# Chart Row 2: Assessment Performance (Chart 3) & LMS Engagement (Chart 4)
c3_col, c4_col = st.columns(2)

with c3_col:
    st.subheader("3. Assessment Score Distribution")
    scores = analytics.get_assessment_performance_distribution()
    if scores:
        df_scores = pd.DataFrame({"Score": scores})
        fig_scores = px.histogram(
            df_scores,
            x="Score",
            nbins=25,
            color_discrete_sequence=["#3B82F6"],
            marginal="box"
        )
        fig_scores.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320, xaxis_title="Assessment Grade (%)", yaxis_title="Submissions")
        st.plotly_chart(fig_scores, use_container_width=True)
    else:
        st.info("No assessment scores found.")

with c4_col:
    st.subheader("4. LMS Digital Engagement")
    lms_data = analytics.get_lms_engagement_by_type()
    if lms_data:
        df_lms = pd.DataFrame([{"Activity Type": k, "Volume": v} for k, v in lms_data.items()])
        fig_lms = px.bar(
            df_lms,
            x="Activity Type",
            y="Volume",
            color="Activity Type",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_lms.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320, showlegend=False)
        st.plotly_chart(fig_lms, use_container_width=True)
    else:
        st.info("No LMS activity logged.")

# Chart Row 3: Risk by Course (Chart 5), Intervention Outcomes (Chart 6) & Monthly Trends (Chart 7)
c5_col, c6_col = st.columns([1, 1])

with c5_col:
    st.subheader("5. Highest Risk Courses")
    course_risk = analytics.get_risk_by_course()
    if course_risk:
        df_crs = pd.DataFrame(course_risk)
        fig_crs = px.bar(
            df_crs,
            x="avg_risk",
            y="course_code",
            orientation="h",
            color="avg_risk",
            color_continuous_scale="Reds",
            hover_data=["course_title", "student_count"],
            labels={"avg_risk": "Avg Risk Score", "course_code": "Course"}
        )
        fig_crs.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_crs, use_container_width=True)
    else:
        st.info("No course risk records.")

with c6_col:
    st.subheader("6. Post-Intervention Ground Truth Outcomes")
    outcomes_summary = analytics.get_intervention_outcomes_summary()
    if outcomes_summary:
        df_out = pd.DataFrame([{"Outcome": k, "Count": v} for k, v in outcomes_summary.items()])
        fig_out = px.bar(
            df_out,
            x="Outcome",
            y="Count",
            color="Outcome",
            color_discrete_map={
                "Course completion": "#10B981",
                "Improved academic performance": "#3B82F6",
                "Successful recovery": "#059669",
                "Continued academic risk": "#EF4444",
                "Course withdrawal": "#9CA3AF"
            }
        )
        fig_out.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320, showlegend=False)
        st.plotly_chart(fig_out, use_container_width=True)
    else:
        st.info("No outcome records evaluated.")

st.subheader("7. Monthly Student Performance & Attendance Trends")
monthly_data = analytics.get_monthly_student_performance_trends()
if monthly_data:
    df_m = pd.DataFrame(monthly_data)
    fig_m = px.line(
        df_m,
        x="month",
        y="attendance_rate",
        markers=True,
        labels={"attendance_rate": "Attendance Rate (%)", "month": "Month"},
        color_discrete_sequence=["#1E3A8A"]
    )
    fig_m.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=280)
    st.plotly_chart(fig_m, use_container_width=True)
