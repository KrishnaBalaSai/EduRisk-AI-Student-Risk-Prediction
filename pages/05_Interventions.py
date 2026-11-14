"""
Page 05: Intervention Management & Effectiveness
Provides full lifecycle management for academic interventions across all 7 evidence-based types,
including scheduling, completion recording, and efficacy tracking.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px

# Add project root to sys.path
# Robust project root resolution
_curr = Path(__file__).resolve()
while _curr.name != 'EduRisk-AI' and _curr.parent != _curr:
    _curr = _curr.parent
project_root = _curr
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from presentation.components.header import apply_theme, render_sidebar
from application.services.intervention_service import InterventionService
from application.services.student_service import StudentService
from application.services.support_service import SupportService

st.set_page_config(page_title="Interventions — EduRisk AI", page_icon="🛡️", layout="wide")
apply_theme()
render_sidebar()

st.title("🛡️ Intervention Management & Efficacy Tracking")
st.markdown("Schedule, deliver, and evaluate structured interventions across all seven supported student success protocols.")

int_service = InterventionService()
student_service = StudentService()
support_service = SupportService()

# Efficacy metrics
interventions = int_service.get_all_interventions(limit=5000)
total_int = len(interventions)
active_int = sum(1 for i in interventions if i.status in ("Scheduled", "In Progress"))
completed_int = sum(1 for i in interventions if i.status == "Completed")
success_rate = int_service.get_success_rate()

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Total Interventions", f"{total_int:,}")
with k2:
    st.metric("Active Sessions", f"{active_int:,}")
with k3:
    st.metric("Completed Sessions", f"{completed_int:,}")
with k4:
    st.metric("Intervention Success", f"{success_rate:.1f}%")

st.markdown("---")

tab_manage, tab_schedule, tab_complete = st.tabs([
    "📋 All Interventions",
    "📅 Schedule Intervention",
    "✅ Record Session Completion"
])

with tab_manage:
    type_filter = st.selectbox(
        "Filter by Intervention Type",
        [
            "All",
            "Academic Counselling",
            "Attendance Follow-up",
            "Mentoring",
            "Learning Support",
            "Parent/Guardian Communication",
            "Study Plan",
            "Faculty Meeting"
        ]
    )
    status_filter = st.selectbox("Filter by Status", ["All", "Scheduled", "In Progress", "Completed", "Cancelled", "No Show"])

    filtered_ints = interventions
    if type_filter != "All":
        filtered_ints = [i for i in filtered_ints if i.intervention_type == type_filter]
    if status_filter != "All":
        filtered_ints = [i for i in filtered_ints if i.status == status_filter]

    if filtered_ints:
        df_int = pd.DataFrame([
            {
                "ID": i.id,
                "Student ID": i.student_id,
                "Type": i.intervention_type,
                "Staff": i.assigned_staff,
                "Scheduled Date": i.scheduled_date.isoformat(),
                "Completion Date": i.completion_date.isoformat() if i.completion_date else "Pending",
                "Status": i.status,
                "Outcome Notes": i.outcome_notes or "—"
            }
            for i in filtered_ints
        ])
        st.dataframe(df_int, use_container_width=True)
    else:
        st.info("No interventions found matching filter.")

with tab_schedule:
    st.subheader("Schedule New Intervention")
    students = student_service.get_all_students(limit=500)
    
    with st.form("form_schedule_intervention"):
        s_student_id = st.selectbox(
            "Target Student",
            options=[s.id for s in students],
            format_func=lambda x: f"{x} - {next((s.first_name + ' ' + s.last_name for s in students if s.id == x), '')}"
        )
        s_type = st.selectbox(
            "Intervention Protocol",
            [
                "Academic Counselling",
                "Attendance Follow-up",
                "Mentoring",
                "Learning Support",
                "Parent/Guardian Communication",
                "Study Plan",
                "Faculty Meeting"
            ]
        )
        s_staff = st.selectbox(
            "Assigned Staff",
            [
                "Dr. Eleanor Vance (Lead Academic Advisor)",
                "Marcus Holloway (Student Success Specialist)",
                "Aria Montgomery (Retention Coordinator)",
                "David Chen (Academic Counselor)",
                "Sarah Jenkins (Learning Support Coach)"
            ]
        )
        s_date = st.date_input("Scheduled Session Date", value=date.today() + timedelta(days=3))
        s_notes = st.text_area("Objective & Preparation Notes", placeholder="e.g. Review calculus fundamentals and establish weekly study check-ins.")
        submit_sched = st.form_submit_button("Schedule Session", type="primary")

        if submit_sched:
            try:
                new_int = int_service.schedule_intervention(
                    student_id=s_student_id,
                    intervention_type=s_type,
                    assigned_staff=s_staff,
                    scheduled_date=s_date,
                    notes=s_notes
                )
                st.success(f"Intervention {new_int.id} scheduled successfully for {s_date.isoformat()}!")
                st.rerun()
            except Exception as ex:
                st.error(f"Scheduling error: {ex}")

with tab_complete:
    st.subheader("Record Completed Session & Outcomes")
    pending_ints = [i for i in interventions if i.status in ("Scheduled", "In Progress")]
    if pending_ints:
        sel_int_id = st.selectbox(
            "Select Session to Complete",
            options=[i.id for i in pending_ints],
            format_func=lambda x: f"{x} - {next((i.intervention_type + ' for ' + i.student_id for i in pending_ints if i.id == x), '')}"
        )
        target_int = next((i for i in pending_ints if i.id == sel_int_id), None)

        if target_int:
            with st.form("form_complete_int"):
                comp_date = st.date_input("Completion Date", value=target_int.scheduled_date)
                comp_status = st.selectbox("Outcome Status", ["Completed", "No Show", "Cancelled"])
                outcome_notes = st.text_area(
                    "Session Findings & Student Commitment",
                    value="Positive engagement. Action plan established; student committed to weekly check-ins."
                )
                submit_comp = st.form_submit_button("Record Completion", type="primary")

                if submit_comp:
                    try:
                        int_service.complete_intervention(
                            intervention_id=target_int.id,
                            completion_date=comp_date,
                            outcome_notes=outcome_notes,
                            status=comp_status
                        )
                        st.success(f"Session {target_int.id} marked as {comp_status}!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Completion failed: {err}")
    else:
        st.info("No active or pending scheduled sessions to record.")
