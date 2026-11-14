"""
Page 04: Support Case Management
Manages academic triage tickets, staff workflows, escalation rules, and case lifecycles.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
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
from application.services.support_service import SupportService
from application.services.student_service import StudentService

st.set_page_config(page_title="Support Cases — EduRisk AI", page_icon="📋", layout="wide")
apply_theme()
render_sidebar()

st.title("📋 Support Case Management & Triage")
st.markdown("Track and triage student support incidents, staff assignments, and escalation states.")

support_service = SupportService()
student_service = StudentService()

# Metric summary
cases = support_service.get_all_cases(limit=1000)
open_c = sum(1 for c in cases if c.status == "Open")
assigned_c = sum(1 for c in cases if c.status == "Assigned")
in_prog_c = sum(1 for c in cases if c.status == "In Progress")
escalated_c = sum(1 for c in cases if c.status == "Escalated")
resolved_c = sum(1 for c in cases if c.status in ("Resolved", "Closed"))

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("Open Queue", open_c)
with m2:
    st.metric("Assigned", assigned_c)
with m3:
    st.metric("In Progress", in_prog_c)
with m4:
    st.metric("Escalated", escalated_c, delta_color="inverse")
with m5:
    st.metric("Resolved / Closed", resolved_c)

st.markdown("---")

tab_list, tab_create, tab_update = st.tabs(["📑 All Active Cases", "➕ Create New Support Case", "⚙️ Update Case Status"])

with tab_list:
    filter_col1, filter_col2 = st.columns([1, 1])
    with filter_col1:
        status_sel = st.selectbox("Filter Status", ["All", "Open", "Assigned", "In Progress", "Escalated", "Resolved", "Closed"])
    with filter_col2:
        prio_sel = st.selectbox("Filter Priority", ["All", "Critical", "High", "Medium", "Low"])

    filtered_cases = cases
    if status_sel != "All":
        filtered_cases = [c for c in filtered_cases if c.status == status_sel]
    if prio_sel != "All":
        filtered_cases = [c for c in filtered_cases if c.priority == prio_sel]

    if filtered_cases:
        df_cases = pd.DataFrame([
            {
                "Case ID": c.id,
                "Student ID": c.student_id,
                "Opened At": c.opened_at.strftime("%Y-%m-%d %H:%M"),
                "Priority": c.priority,
                "Status": c.status,
                "Assigned Staff": c.assigned_staff,
                "Trigger Reason": c.trigger_reason,
                "Resolved At": c.resolved_at.strftime("%Y-%m-%d") if c.resolved_at else "—",
            }
            for c in filtered_cases
        ])
        st.dataframe(df_cases, use_container_width=True)
    else:
        st.info("No support cases match the filter criteria.")

with tab_create:
    st.subheader("Initiate Support Case")
    students = student_service.get_all_students(limit=500)
    
    with st.form("form_create_case"):
        c_student_id = st.selectbox(
            "Student",
            options=[s.id for s in students],
            format_func=lambda x: f"{x} - {next((s.first_name + ' ' + s.last_name for s in students if s.id == x), '')}"
        )
        c_reason = st.text_input("Trigger Reason", placeholder="e.g. Attendance dropped below 55% with 3 consecutive unexcused absences")
        c_prio = st.selectbox("Priority Level", ["Medium", "High", "Critical", "Low"])
        c_staff = st.selectbox(
            "Assigned Advisor / Staff",
            [
                "Dr. Eleanor Vance (Lead Academic Advisor)",
                "Marcus Holloway (Student Success Specialist)",
                "Aria Montgomery (Retention Coordinator)",
                "David Chen (Academic Counselor)",
                "Sarah Jenkins (Learning Support Coach)"
            ]
        )
        c_notes = st.text_area("Initial Triage Notes", placeholder="Context or specific instructor observations...")
        submit_create = st.form_submit_button("Create Support Case", type="primary")

        if submit_create:
            if not c_reason.strip():
                st.error("Please provide a valid trigger reason.")
            else:
                try:
                    new_c = support_service.create_case(
                        student_id=c_student_id,
                        trigger_reason=c_reason,
                        priority=c_prio,
                        assigned_staff=c_staff,
                        notes=c_notes
                    )
                    st.success(f"Support Case {new_c.id} created successfully!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error creating case: {ex}")

with tab_update:
    st.subheader("Update Support Case State")
    if cases:
        case_to_up = st.selectbox("Select Case to Modify", options=[c.id for c in cases], format_func=lambda x: f"{x} ({next((c.student_id + ' - ' + c.status for c in cases if c.id == x), '')})")
        curr_c = next((c for c in cases if c.id == case_to_up), None)

        if curr_c:
            st.info(f"Current State: **{curr_c.status}** | Assigned: **{curr_c.assigned_staff}** | Reason: *{curr_c.trigger_reason}*")
            with st.form("form_update_case"):
                new_status = st.selectbox("New Status", ["Open", "Assigned", "In Progress", "Escalated", "Resolved", "Closed"], index=["Open", "Assigned", "In Progress", "Escalated", "Resolved", "Closed"].index(curr_c.status))
                new_staff = st.selectbox("Reassign Staff", [
                    "Dr. Eleanor Vance (Lead Academic Advisor)",
                    "Marcus Holloway (Student Success Specialist)",
                    "Aria Montgomery (Retention Coordinator)",
                    "David Chen (Academic Counselor)",
                    "Sarah Jenkins (Learning Support Coach)"
                ], index=0)
                update_notes = st.text_area("Status Progression Notes", placeholder="Action items completed or next escalation step...")
                submit_up = st.form_submit_button("Commit Case Update")

                if submit_up:
                    try:
                        support_service.assign_staff(curr_c.id, new_staff)
                        support_service.update_case_status(curr_c.id, new_status, notes=update_notes)
                        st.success(f"Case {curr_c.id} successfully updated to {new_status}!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Update failed: {err}")
