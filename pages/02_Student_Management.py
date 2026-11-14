"""
Page 02: Student Management & 360 Degree Profile
Provides searchable student directory and deep-dive multi-domain student profiles.
"""

import streamlit as st
import sys
from pathlib import Path
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
from application.services.student_service import StudentService
from application.services.risk_service import RiskService

st.set_page_config(page_title="Student Management - EduRisk AI", page_icon="S", layout="wide")
apply_theme()
render_sidebar()

st.title("Student Management & Longitudinal Profile")
st.markdown("Holistic 360-degree learner records integrating enrollments, attendance, assessments, digital footprints, and interventions.")

student_service = StudentService()
risk_service = RiskService()

# Search and Filtering Controls
f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
with f_col1:
    search_query = st.text_input("Search Student (Name, ID, Email, Cohort)", placeholder="e.g. STU-2026-000001 or Emily")
with f_col2:
    status_filter = st.selectbox("Status", ["All", "Active", "Withdrawn", "Graduated", "Suspended"])
with f_col3:
    cohort_filter = st.selectbox("Cohort", ["All", "Cohort 2026-A", "Cohort 2026-B", "Cohort 2026-C"])

# Fetch Students
if search_query:
    students = student_service.search_students(search_query)
else:
    students = student_service.get_all_students(limit=500)

if status_filter != "All":
    students = [s for s in students if s.status == status_filter]
if cohort_filter != "All":
    students = [s for s in students if s.cohort == cohort_filter]

st.caption(f"Showing {len(students)} matching student records.")

if not students:
    st.warning("No student records found matching filter criteria.")
    st.stop()

# Convert to DataFrame for table view
student_rows = []
for s in students:
    student_rows.append({
        "ID": s.id,
        "Name": f"{s.first_name} {s.last_name}",
        "Email": s.email,
        "Cohort": s.cohort,
        "Status": s.status,
        "Enrollment Date": s.enrollment_date.isoformat() if s.enrollment_date else "N/A",
        "Withdrawal Date": s.withdrawal_date.isoformat() if s.withdrawal_date else "None"
    })

df_students = pd.DataFrame(student_rows)

selected_student_id = st.selectbox(
    "Select a student to view complete 360-degree Profile:",
    options=[s.id for s in students],
    format_func=lambda x: f"{x} - {next((s.first_name + ' ' + s.last_name for s in students if s.id == x), '')}"
)

st.markdown("---")

# Load Student 360 Profile
from datetime import date

profile = student_service.get_student_profile(
    selected_student_id,
    cutoff_date=date.today()
)
if not profile:
    st.error(f"Could not load profile for student {selected_student_id}.")
    st.stop()

s = profile["student"]
latest_risk = profile["latest_risk"]


# Profile Header Banner
st.html(
    f"""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; color: #1E3A8A;">{s.first_name} {s.last_name}</h2>
                <p style="margin: 4px 0 0 0; color: #64748B; font-size: 14px;">
                    <code>{s.id}</code> | {s.email} | {s.cohort} | Enrolled: {s.enrollment_date}
                    {f" | <b style='color:#EF4444;'>Withdrawn: {s.withdrawal_date}</b>" if s.withdrawal_date else ""}
                </p>
            </div>
            <div>
                <span class="badge { 'badge-high' if latest_risk and latest_risk.risk_category == 'High Risk' else ('badge-med' if latest_risk and latest_risk.risk_category == 'Medium Risk' else 'badge-low') }">
                    {latest_risk.risk_category if latest_risk else 'Risk Not Evaluated'}
                    {f" ({latest_risk.overall_score:.1f}/100)" if latest_risk else ""}
                </span>
            </div>
        </div>
    </div>
    """
)


# Tabs
tab_overview, tab_att, tab_asm, tab_lms, tab_support, tab_risk = st.tabs([
    "Overview & Courses",
    "Attendance Record",
    "Assessment Results",
    "LMS Activity",
    "Support Cases & Interventions",
    "Risk Analysis"
])

with tab_overview:
    st.subheader("Registered Course Enrollments")
    enrs = profile["enrollments"]
    if enrs:
        enr_data = []
        for e in enrs:
            c = e.course
            enr_data.append({
                "Enrollment ID": e.id,
                "Course Code": c.code if c else "N/A",
                "Course Title": c.title if c else "N/A",
                "Department": c.department if c else "N/A",
                "Credits": c.credits if c else "N/A",
                "Semester": c.semester if c else "N/A",
                "Status": e.status,
                "Final Grade": f"{e.final_grade:.1f}%" if e.final_grade is not None else "In Progress"
            })
        st.dataframe(pd.DataFrame(enr_data), use_container_width=True)
    else:
        st.info("No course enrollments found.")

with tab_att:
    st.subheader("Attendance Summary & History")
    att_sum = profile["attendance_summary"]
    a1, a2, a3, a4, a5 = st.columns(5)
    with a1:
        st.metric("Attendance Rate", f"{att_sum['attendance_rate']:.1f}%" if att_sum['attendance_rate'] is not None else "N/A")
    with a2:
        st.metric("Total Sessions", att_sum["total_sessions"])
    with a3:
        st.metric("Present / Late", f"{att_sum['present']} / {att_sum['late']}")
    with a4:
        st.metric("Approved Absences", att_sum["absent_approved"])
    with a5:
        st.metric("Unapproved Absences", att_sum["absent_unapproved"], delta_color="inverse")

    att_events = profile["attendance_events"]
    if att_events:
        st.markdown("#### Weekly Attendance Log")
        att_df = pd.DataFrame([
            {
                "Date": ev.session_date.isoformat(),
                "Course": ev.course_id,
                "Status": ev.status,
                "Type": ev.session_type,
                "Notes": ev.notes or "-"
            }
            for ev in att_events
        ])
        st.dataframe(att_df, use_container_width=True)

with tab_asm:
    st.subheader("Assessment Scores & Milestone Progress")
    asm_sum = profile["assessment_summary"]
    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("Average Score", f"{asm_sum['average_score']:.1f}%" if asm_sum['average_score'] is not None else "N/A")
    with s2:
        st.metric("Completed Assessments", asm_sum["completed_count"])
    with s3:
        st.metric("Missing Submissions", asm_sum["missing_count"], delta_color="inverse")

    results = profile["assessment_results"]
    if results:
        res_df = pd.DataFrame([
            {
                "Assessment ID": r.assessment_id,
                "Title": r.assessment.title if r.assessment else "Assessment",
                "Type": r.assessment.assessment_type if r.assessment else "N/A",
                "Weight": f"{r.assessment.weight * 100:.0f}%" if r.assessment else "N/A",
                "Due Date": r.assessment.due_date.isoformat() if (r.assessment and r.assessment.due_date) else "N/A",
                "Submission Date": r.submission_date.isoformat() if r.submission_date else "Not Submitted",
                "Score": f"{r.score:.1f}%" if r.score is not None else "Missing (Null)",
                "Status": r.status
            }
            for r in results
        ])
        st.dataframe(res_df, use_container_width=True)

with tab_lms:
    st.subheader("LMS Portal Digital Footprint")
    lms_sum = profile["lms_summary"]
    l1, l2, l3 = st.columns(3)
    with l1:
        st.metric("Recent Activity Count (30d)", lms_sum["recent_count"])
    with l2:
        st.metric("Time Spent", f"{lms_sum['recent_duration_mins']} mins")
    with l3:
        st.metric("Engagement Trend", f"{lms_sum['trend_pct']:+.1f}%")

    lms_events = profile["lms_events"]
    if lms_events:
        lms_df = pd.DataFrame([
            {
                "Timestamp": ev.timestamp.strftime("%Y-%m-%d %H:%M"),
                "Activity": ev.activity_type,
                "Duration (s)": ev.duration_seconds,
                "Course": ev.course_id or "Platform Portal"
            }
            for ev in lms_events[-20:]
        ])
        st.dataframe(lms_df, use_container_width=True)

with tab_support:
    st.subheader("Support Cases & Interventions")
    cases = profile["support_cases"]
    if cases:
        st.markdown("#### Logged Support Cases")
        case_df = pd.DataFrame([
            {
                "Case ID": c.id,
                "Opened At": c.opened_at.strftime("%Y-%m-%d"),
                "Trigger Reason": c.trigger_reason,
                "Status": c.status,
                "Priority": c.priority,
                "Assigned Staff": c.assigned_staff,
                "Resolved": c.resolved_at.strftime("%Y-%m-%d") if c.resolved_at else "Open"
            }
            for c in cases
        ])
        st.dataframe(case_df, use_container_width=True)
    else:
        st.info("No support cases on record for this student.")

    ints = profile["interventions"]
    if ints:
        st.markdown("#### Assigned Interventions")
        int_df = pd.DataFrame([
            {
                "Intervention ID": it.id,
                "Type": it.intervention_type,
                "Staff": it.assigned_staff,
                "Scheduled Date": it.scheduled_date.isoformat(),
                "Completion Date": it.completion_date.isoformat() if it.completion_date else "Pending",
                "Status": it.status,
                "Outcome Notes": it.outcome_notes or "-"
            }
            for it in ints
        ])
        st.dataframe(int_df, use_container_width=True)
    else:
        st.info("No interventions scheduled for this student.")

with tab_risk:
    st.subheader("Risk Score & Explainability Breakdown")
    if latest_risk:
        r_col1, r_col2 = st.columns([1, 1])
        with r_col1:
            categories = ["Attendance (35%)", "Assessment (30%)", "LMS (20%)", "Support (15%)"]
            values = [
                latest_risk.attendance_risk,
                latest_risk.assessment_risk,
                latest_risk.lms_risk,
                latest_risk.support_risk,
            ]
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                fillcolor="rgba(30, 58, 138, 0.2)",
                line=dict(color="#1E3A8A", width=2)
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                margin=dict(t=20, b=20, l=40, r=40),
                height=300
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with r_col2:
            st.markdown(
                f"""
                <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px;">
                    <h4 style="margin: 0 0 8px 0; color: #1E3A8A;">Explainability Narrative</h4>
                    <p style="font-size: 14px; line-height: 1.6; color: #334155;">{latest_risk.explanation}</p>
                    <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 12px 0;">
                    <div style="font-size: 12px; color: #64748B;">
                        <div><b>Model Version:</b> <code>{latest_risk.model_version}</code></div>
                        <div><b>Prediction Date:</b> {latest_risk.prediction_timestamp.strftime('%Y-%m-%d %H:%M')}</div>
                        <div><b>Observation Cutoff:</b> {latest_risk.observation_window_end.isoformat()}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No risk prediction recorded yet. Run risk prediction on the Risk Analysis page.")
