"""
Enterprise Header & Navigation Component
Renders the professional Navy/Blue styling and sidebar demo user switcher.
"""

import streamlit as st
from presentation.auth import DEMO_ACCOUNTS, get_demo_account


def apply_theme():
    """Inject modern, clean enterprise CSS styling."""
    st.markdown(
        """
        <style>
        /* Base typography & palette */
        :root {
            --primary: #1E3A8A;
            --primary-light: #3B82F6;
            --primary-dark: #0F172A;
            --background: #F8FAFC;
            --card-bg: #FFFFFF;
            --text-main: #0F172A;
            --text-muted: #64748B;
            --border: #E2E8F0;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
        }

        .main-header {
            background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
            color: white;
            padding: 24px 32px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .main-header h1 {
            font-size: 28px;
            font-weight: 700;
            margin: 0;
            color: #FFFFFF;
        }

        .main-header p {
            font-size: 14px;
            color: #93C5FD;
            margin: 6px 0 0 0;
        }

        .kpi-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 18px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .kpi-title {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748B;
            margin-bottom: 4px;
        }

        .kpi-value {
            font-size: 26px;
            font-weight: 700;
            color: #0F172A;
            margin: 0;
        }

        .kpi-delta {
            font-size: 12px;
            font-weight: 500;
            margin-top: 4px;
        }

        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
        }

        .badge-low {
            background-color: #DCFCE7;
            color: #166534;
        }

        .badge-med {
            background-color: #FEF3C7;
            color: #92400E;
        }

        .badge-high {
            background-color: #FEE2E2;
            color: #991B1B;
        }

        /* Streamlit adjustments */
        [data-testid="stSidebar"] {
            background-color: #0F172A;
        }

        [data-testid="stSidebar"] * {
            color: #F8FAFC !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_sidebar():
    """Render sidebar branding, demo role selection, and user info."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 12px 0; border-bottom: 1px solid #334155; margin-bottom: 16px;">
                <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #60A5FA !important;">EduRisk AI</h2>
                <p style="margin: 2px 0 0 0; font-size: 11px; color: #94A3B8 !important;">YottaFlex Hackathon Edition</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption("DEMO AUTHENTICATION")
        role_options = {
            "Platform Administrator": "admin",
            "Academic Administrator": "dean",
            "Instructor": "instructor",
            "Support Staff": "support",
            "Learner": "student",
        }

        current_role_name = st.session_state.get("user_role_name", "Platform Administrator")
        selected_role_name = st.selectbox(
            "Switch Demo Role",
            options=list(role_options.keys()),
            index=list(role_options.keys()).index(current_role_name) if current_role_name in role_options else 0,
            key="role_selector"
        )

        role_key = role_options[selected_role_name]
        user_info = get_demo_account(role_key)
        st.session_state["user_role_name"] = selected_role_name
        st.session_state["current_user"] = user_info

        st.markdown(
            f"""
            <div style="background-color: #1E293B; border-radius: 8px; padding: 12px; margin-top: 8px;">
                <div style="font-size: 11px; color: #94A3B8 !important;">SIGNED IN AS</div>
                <div style="font-size: 14px; font-weight: 600; color: #F8FAFC !important;">{user_info['name']}</div>
                <div style="font-size: 12px; color: #38BDF8 !important;">{user_info['role']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.caption("SYSTEM STATUS")
        st.markdown(
            """
            <div style="font-size: 12px; color: #94A3B8 !important; line-height: 1.6;">
                <div>🟢 Database: Active (SQLAlchemy)</div>
                <div>⚡ Engine: Explainable Rule/ML</div>
                <div>🔒 Architecture: 3-Tier Enforced</div>
                <div>🌱 Seed: <code>20261022</code></div>
            </div>
            """,
            unsafe_allow_html=True
        )

