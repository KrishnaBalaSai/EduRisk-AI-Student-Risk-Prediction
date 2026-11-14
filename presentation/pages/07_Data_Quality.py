"""
Page 07: Data Quality & Anomaly Detection
Provides comprehensive anomaly detection, reconciliation audits, and automated validation reports.
Directly verifies detection of all 5 mandatory negative scenarios against injected fixtures.
"""

import streamlit as st
import sys
from pathlib import Path
import json
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
from application.validators.validation_suite import ValidationSuite

st.set_page_config(page_title="Data Quality & Anomalies — EduRisk AI", page_icon="✅", layout="wide")
apply_theme()
render_sidebar()

st.title("✅ Data Quality & Anomaly Detection Center")
st.markdown("Automated validation suite evaluating primary/foreign keys, lifecycle transitions, temporal safety, and all 5 mandatory negative scenarios.")

suite = ValidationSuite()

col_act1, col_act2 = st.columns([1, 3])
with col_act1:
    run_val = st.button("🔍 Run Full Validation Suite", type="primary", use_container_width=True)

results = suite.run_all()
export_paths = suite.export_reports(results)

# High Level Validation Metrics
v1, v2, v3, v4 = st.columns(4)
with v1:
    st.metric("Total Checks Passed", f"{results['total_passed']:,}")
with v2:
    st.metric("Detected Inconsistencies", f"{results['total_failed']:,}", delta_color="inverse")
with v3:
    all_det = results["all_anomalies_detected"]
    st.metric("5 Mandatory Anomalies", "100% Detected" if all_det else "Partial")
with v4:
    st.metric("Validation Status", results["summary_status"])

st.markdown("---")

st.subheader("🎯 Required 5 Negative Scenarios Verification")
recon = results["ground_truth_reconciliation"]
fixtures = recon.get("fixtures", [])

if fixtures:
    df_fix = pd.DataFrame([
        {
            "Fixture ID": f["fixture_id"],
            "Issue Type": f["issue_type"],
            "Target Record": f["record_id"],
            "Detection Status": f["status"],
            "Description": f["description"],
        }
        for f in fixtures
    ])
    st.dataframe(df_fix, use_container_width=True)
else:
    st.info("No anomaly fixtures loaded. Generate dataset with anomalies enabled.")

st.markdown("---")

st.subheader("Validator Module Breakdown")
v_tabs = st.tabs([
    "🛡️ Integrity Validator",
    "⏳ Temporal Validator (Leakage)",
    "➗ Reconciliation Validator",
    "🔄 Lifecycle Validator",
    "👯 Duplicate Validator"
])

validators = results["validators"]

with v_tabs[0]:
    v_data = validators.get("IntegrityValidator", {})
    st.markdown(f"**Passed Checks:** {v_data.get('passed', 0)} | **Errors:** {v_data.get('failed', 0)}")
    errors = v_data.get("errors", [])
    if errors:
        for err in errors:
            st.error(err)
    else:
        st.success("All primary keys, foreign keys, and allowed enum constraints are valid.")

with v_tabs[1]:
    v_data = validators.get("TemporalValidator", {})
    st.markdown(f"**Passed Checks:** {v_data.get('passed', 0)} | **Temporal Violations:** {v_data.get('failed', 0)}")
    anomalies = [a for a in results["all_detected_anomalies"] if a["issue_type"] == "future_data_leakage"]
    if anomalies:
        for a in anomalies:
            st.warning(f"🚨 {a['message']}")
    else:
        st.success("No future-data leakage detected in risk predictions.")

with v_tabs[2]:
    v_data = validators.get("ReconciliationValidator", {})
    st.markdown(f"**Passed Checks:** {v_data.get('passed', 0)} | **Arithmetic Inconsistencies:** {v_data.get('failed', 0)}")
    errors = v_data.get("errors", [])
    if errors:
        for err in errors:
            st.warning(f"⚠️ {err}")
    else:
        st.success("All arithmetic reconciliations and risk score formulas verified.")

with v_tabs[3]:
    v_data = validators.get("LifecycleValidator", {})
    st.markdown(f"**Passed Checks:** {v_data.get('passed', 0)} | **Lifecycle Violations:** {v_data.get('failed', 0)}")
    errors = v_data.get("errors", [])
    if errors:
        for err in errors:
            st.warning(f"⚠️ {err}")
    else:
        st.success("All student statuses, enrollments, and intervention chronological rules satisfied.")

with v_tabs[4]:
    v_data = validators.get("DuplicateValidator", {})
    st.markdown(f"**Passed Checks:** {v_data.get('passed', 0)} | **Duplicate Records:** {v_data.get('failed', 0)}")
    errors = v_data.get("errors", [])
    if errors:
        for err in errors:
            st.error(err)
    else:
        st.success("No duplicate events or keys detected.")

st.markdown("---")
st.subheader("📥 Export Validation Findings")
d_col1, d_col2 = st.columns(2)

with d_col1:
    json_str = json.dumps(results, indent=2)
    st.download_button(
        "⬇️ Download Validation Report (JSON)",
        data=json_str,
        file_name="validation_report.json",
        mime="application/json",
        use_container_width=True
    )

with d_col2:
    csv_file = Path(export_paths["csv_report"])
    if csv_file.exists():
        csv_data = csv_file.read_text(encoding="utf-8")
        st.download_button(
            "⬇️ Download Validation Report (CSV)",
            data=csv_data,
            file_name="validation_report.csv",
            mime="text/csv",
            use_container_width=True
        )
