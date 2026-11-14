"""
Page 06: Synthetic Data Generation Engine
Provides interface to generate reproducible datasets at Starter or Full production scale.
"""

import streamlit as st
import sys
import time
from pathlib import Path
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
from generators.master_generator import PROFILES
from application.services.generator_service import GeneratorService

st.set_page_config(page_title="Data Generator — EduRisk AI", page_icon="⚙️", layout="wide")
apply_theme()
render_sidebar()

st.title("⚙️ Synthetic Data Generation Engine")
st.markdown("Generate fully reproducible, entity-correlated datasets with fixed seed `20261022`.")

col_p1, col_p2 = st.columns([1, 1])

with col_p1:
    st.markdown("### Generation Profile")
    profile_choice = st.radio(
        "Choose Target Scale Profile:",
        [
            "Starter Profile (100 Students, 20 Courses, 300 Enrollments)",
            "Full Profile (5,000 Students, 200 Courses, 20,000 Enrollments)"
        ]
    )
    profile_key = "starter" if "Starter" in profile_choice else "full"
    profile_meta = PROFILES[profile_key]

with col_p2:
    st.markdown("### Reproducibility Parameters")
    seed_input = st.number_input("Deterministic Random Seed", value=20261022, step=1)
    inject_anomalies_flag = st.checkbox("Inject Labelled Negative Scenarios (5 Anomalies)", value=True)

st.markdown(
    f"""
    <div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 16px; margin: 16px 0;">
        <h4 style="margin: 0 0 8px 0; color: #1E3A8A;">Target Profile Specification: {profile_key.upper()}</h4>
        <div style="font-size: 13px; color: #475569; display: flex; gap: 24px;">
            <div>👥 <b>Students:</b> {profile_meta['student_count']:,}</div>
            <div>📚 <b>Courses:</b> {profile_meta['course_count']:,}</div>
            <div>📝 <b>Enrollments:</b> {profile_meta['enrollment_count']:,}</div>
            <div>🌱 <b>Seed:</b> <code>{seed_input}</code></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if st.button("🚀 Start Dataset Generation", type="primary", use_container_width=True):
    progress_bar = st.progress(0, text="Initializing database schema...")
    status_text = st.empty()
    
    start_t = time.time()
    try:
        progress_bar.progress(30, text=f"Executing generation and persistence for profile: {profile_key}...")
        
        counts = GeneratorService.generate_and_persist(
            profile_name=profile_key,
            seed=int(seed_input),
            inject_anomalies=inject_anomalies_flag,
            clean_first=True
        )
        
        progress_bar.progress(100, text="Generation and persistence completed!")
        elapsed = time.time() - start_t
        
        st.success(f"🎉 Successfully generated and persisted dataset in {elapsed:.2f} seconds!")

        st.subheader("Persisted Entity Counts")
        summary_rows = [{"Entity Type": k, "Record Count": f"{v:,}"} for k, v in counts.items()]
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

    except Exception as exc:
        st.error(f"Generation encountered an error: {exc}")
