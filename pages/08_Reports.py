"""
Page 08: Reports & Export Center
Provides multi-format data export (CSV, JSON, SQL) across all 10 domain entities,
data dictionary reference, and dataset provenance manifests.
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
from application.services.export_service import ExportService

st.set_page_config(page_title="Reports & Exports — EduRisk AI", page_icon="📁", layout="wide")
apply_theme()
render_sidebar()

st.title("📁 Reports & Export Center")
st.markdown("Download full institutional datasets in CSV, JSON, and SQL formats, inspect data dictionaries, and view provenance manifests.")

export_service = ExportService(base_dir=str(project_root / "exports"))

tab_exports, tab_dict, tab_manifest = st.tabs([
    "📥 Data Export Center",
    "📖 Data Dictionary",
    "📜 Source Provenance Manifest"
])

with tab_exports:
    st.subheader("Generate & Download Institutional Datasets")
    if st.button("🔄 Regenerate All Export Artifacts", type="primary"):
        with st.spinner("Compiling CSV, JSON, and SQL dumps across all 10 entities..."):
            manifest = export_service.export_all()
            st.success("All export bundles generated successfully!")

    entities = [
        ("Students", "students"),
        ("Courses", "courses"),
        ("Enrollments", "enrollments"),
        ("Attendance Events", "attendance"),
        ("Assessments", "assessments"),
        ("Assessment Results", "assessment_results"),
        ("LMS Activity", "lms_activities"),
        ("Support Cases", "support_cases"),
        ("Interventions", "interventions"),
        ("Outcomes", "outcomes"),
        ("Ground Truth Anomalies", "ground_truth_anomalies"),
    ]

    st.markdown("#### Entity Export Downloads")
    csv_dir = project_root / "exports" / "csv"
    json_dir = project_root / "exports" / "json"

    for label, slug in entities:
        col_name, col_csv, col_json = st.columns([2, 1, 1])
        with col_name:
            st.markdown(f"**{label}** (`{slug}`)")

        c_file = csv_dir / f"{slug}.csv"
        j_file = json_dir / f"{slug}.json"

        with col_csv:
            if c_file.exists():
                st.download_button(
                    label=f"CSV",
                    data=c_file.read_bytes(),
                    file_name=f"{slug}.csv",
                    mime="text/csv",
                    key=f"dl_csv_{slug}"
                )
            else:
                st.caption("Not generated")

        with col_json:
            if j_file.exists():
                st.download_button(
                    label=f"JSON",
                    data=j_file.read_bytes(),
                    file_name=f"{slug}.json",
                    mime="application/json",
                    key=f"dl_json_{slug}"
                )
            else:
                st.caption("Not generated")

    st.markdown("---")
    st.markdown("#### SQL Schema & Database Seed")
    sql_file = project_root / "exports" / "sql" / "edurisk_seed.sql"
    if sql_file.exists():
        st.download_button(
            "⬇️ Download Full SQL Seed Dump (MySQL 8+)",
            data=sql_file.read_bytes(),
            file_name="edurisk_seed.sql",
            mime="application/sql",
            use_container_width=True
        )
    else:
        st.info("Click 'Regenerate All Export Artifacts' to create SQL seed dump.")

with tab_dict:
    st.subheader("Data Dictionary & Domain Entities")
    data_dict_file = project_root / "docs" / "data_dictionary.md"
    if data_dict_file.exists():
        st.markdown(data_dict_file.read_text(encoding="utf-8"))
    else:
        st.info("Data dictionary document located at `docs/data_dictionary.md`.")

with tab_manifest:
    st.subheader("Dataset Provenance & Licensing Manifest")
    manifest_file = project_root / "docs" / "source_manifest.json"
    if manifest_file.exists():
        st.json(json.loads(manifest_file.read_text(encoding="utf-8")))
    else:
        st.info("Manifest file located at `docs/source_manifest.json`.")
