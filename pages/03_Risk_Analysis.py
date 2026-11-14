"""
Page 03: Explainable Risk Prediction Analysis
Provides interactive risk scoring, factor explainability, cutoff date temporal safety controls,
and batch recalculation workflows.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import date, datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add project root to sys.path
# Robust project root resolution
_curr = Path(__file__).resolve()
while _curr.name != 'EduRisk-AI' and _curr.parent != _curr:
    _curr = _curr.parent
project_root = _curr
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from presentation.components.header import apply_theme, render_sidebar
from application.services.risk_service import RiskService
from application.services.student_service import StudentService

st.set_page_config(page_title="Risk Analysis — EduRisk AI", page_icon="🔍", layout="wide")
apply_theme()
render_sidebar()

st.title("🔍 Explainable Risk Prediction Engine")
st.markdown("Multi-factor explainable risk scoring using strictly historical signals without temporal data leakage.")

risk_service = RiskService()
student_service = StudentService()

# Interactive Configuration Controls
with st.expander("⚙️ Engine Configuration & Temporal Cutoff Controls", expanded=True):
    col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
    with col_c1:
        st.markdown("##### Temporal Safety Observation Window")
        selected_cutoff = st.date_input(
            "Observation Cutoff Date (No Future Leakage)",
            value=date.today(),
            min_value=date(2026, 9, 1),
            max_value=date.today(),
            help="Signals occurring after this date are strictly hidden from the prediction engine."
        )
    with col_c2:
        st.markdown("##### Configurable Factor Weights")
        st.caption("Attendance (35%) | Assessment (30%) | LMS (20%) | Support (15%)")
        w_att = st.slider("Attendance Weight", 0.1, 0.6, 0.35, 0.05)
        w_asm = st.slider("Assessment Weight", 0.1, 0.6, 0.30, 0.05)
    with col_c3:
        st.markdown("##### Risk Thresholds")
        low_th = st.number_input("Low Risk Ceiling", value=34.0, step=1.0)
        med_th = st.number_input("Medium Risk Ceiling", value=64.0, step=1.0)

    st.markdown("---")
    btn_col1, btn_col2 = st.columns([1, 3])
    with btn_col1:
        if st.button("🚀 Run Institutional Batch Scoring", type="primary", use_container_width=True):
            with st.spinner("Executing explainable risk evaluation across all student cohorts..."):
                preds = risk_service.predict_all_students(observation_window_end=selected_cutoff, persist=True)
                st.success(f"Evaluated and updated risk predictions for {len(preds)} students!")
                st.rerun()

st.markdown("### Individual Student Risk Evaluation")
students = student_service.get_all_students(limit=500)
if not students:
    st.info("No students found. Please generate starter dataset first.")
    st.stop()

eval_col1, eval_col2 = st.columns([2, 1])
with eval_col1:
    selected_stu_id = st.selectbox(
        "Select Student for Explainable Evaluation",
        options=[s.id for s in students],
        format_func=lambda x: f"{x} - {next((s.first_name + ' ' + s.last_name for s in students if s.id == x), '')}"
    )

with eval_col2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    recompute = st.button("⚡ Evaluate Student on Cutoff Date", use_container_width=True)

# Compute prediction for selected student
if recompute:
    pred = risk_service.predict_student_risk(
        selected_stu_id,
        observation_window_end=selected_cutoff,
        persist=True
    )
else:
    pred = risk_service.get_student_risk(selected_stu_id)

    if pred and pred.observation_window_end != selected_cutoff:
        st.warning(
            f"The latest saved prediction is for "
            f"{pred.observation_window_end}. "
            f"Click 'Evaluate Student on Cutoff Date' "
            f"to calculate the prediction for {selected_cutoff}."
        )
        pred = None

if pred:
    score_col1, score_col2 = st.columns([1, 1])

    with score_col1:
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; text-align: center;">
                <div style="font-size: 14px; font-weight: 600; color: #64748B;">OVERALL RISK SCORE</div>
                <div style="font-size: 48px; font-weight: 800; color: { '#EF4444' if pred.risk_category == 'High Risk' else ('#F59E0B' if pred.risk_category == 'Medium Risk' else '#10B981') };">
                    {pred.overall_score:.1f}
                </div>
                <div style="font-size: 16px; font-weight: 700; margin-top: 4px;">
                    <span class="badge { 'badge-high' if pred.risk_category == 'High Risk' else ('badge-med' if pred.risk_category == 'Medium Risk' else 'badge-low') }">
                        {pred.risk_category}
                    </span>
                </div>
                <p style="font-size: 12px; color: #94A3B8; margin-top: 12px;">Observation Cutoff: {pred.observation_window_end.isoformat()}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        # Factor Bar Chart
        df_factors = pd.DataFrame([
            {"Factor": "Attendance (35%)", "Risk": pred.attendance_risk, "Color": "#1E3A8A"},
            {"Factor": "Assessment (30%)", "Risk": pred.assessment_risk, "Color": "#3B82F6"},
            {"Factor": "LMS Engagement (20%)", "Risk": pred.lms_risk, "Color": "#60A5FA"},
            {"Factor": "Support History (15%)", "Risk": pred.support_risk, "Color": "#93C5FD"},
        ])
        fig_bar = px.bar(
            df_factors,
            x="Risk",
            y="Factor",
            orientation="h",
            color="Risk",
            color_continuous_scale="Reds",
            range_x=[0, 100],
            text="Risk"
        )
        fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=220)
        st.plotly_chart(fig_bar, use_container_width=True)

    with score_col2:
        st.markdown("#### 📖 Explainability Narrative")
        st.markdown(
            f"""
            <div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 10px; padding: 20px; min-height: 220px;">
                <p style="font-size: 15px; line-height: 1.7; color: #1E293B; margin: 0;">
                    {pred.explanation}
                </p>
                <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 16px 0;">
                <div style="font-size: 12px; color: #64748B; line-height: 1.6;">
                    <div>🛡️ <b>Temporal Safety:</b> Strict cutoff verified. Signals past <code>{pred.observation_window_end}</code> excluded.</div>
                    <div>🏷️ <b>Engine Model:</b> <code>{pred.model_version}</code></div>
                    <div>⏱️ <b>Generated At:</b> {pred.prediction_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Recommended Interventions preview
        from application.engines.intervention_engine import InterventionEngine
        recs = InterventionEngine.recommend_interventions(pred)
        if recs:
            st.markdown("#### 🎯 AI Recommended Interventions")
            for rec in recs:
                st.markdown(
                    f"""
                    <div style="border-left: 4px solid #1E3A8A; background: #FFFFFF; padding: 10px 14px; margin-bottom: 8px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                        <b>{rec['type']}</b> <span style="font-size: 11px; color: #EF4444; font-weight:600;">[{rec['urgency']} Urgency]</span>
                        <div style="font-size: 12px; color: #475569;">{rec['reason']}</div>
                        <div style="font-size: 11px; color: #64748B;">Assigned: {rec['assigned_staff']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
