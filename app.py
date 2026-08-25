"""
AI Student Success Platform — Main Streamlit Application
=========================================================
Entry point: streamlit run app.py
"""

import streamlit as st
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.ui_helpers import inject_css, CUSTOM_CSS

# ─── Page Configuration ──────────────────────────────────────────
st.set_page_config(
    page_title="AI Student Success Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ─── Session State Initialization ─────────────────────────────────
defaults = {
    "authenticated": False,
    "user_id": None,
    "user_name": "",
    "user_email": "",
    "user_role": "",
    "current_page": "Login",
    "selected_student_id": None,
    "selected_module_id": None,
    "show_signup": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ─── Navigation Menu Definitions ──────────────────────────────────
ADMIN_MENU = {
    "🏠 Dashboard": "Dashboard",
    "👨‍🎓 Students": "Students",
    "📚 Modules": "Modules",
    "📊 Academic Performance": "Academic",
    "📅 Attendance": "Attendance",
    "🤖 AI Prediction": "Predictions",
    "⚠️ Risk Analysis": "Risk Analysis",
    "🧠 Explainable AI": "Explainable AI",
    "💡 Recommendations": "Recommendations",
    "🚨 Early Intervention": "Early Intervention",
    "📈 Analytics": "Analytics",
    "📁 Data Import": "Data Import",
    "🧪 Model Performance": "Model Performance",
    "👤 Profile": "Profile",
    "⚙️ Settings": "Settings",
}

FACULTY_MENU = {
    "🏠 Dashboard": "Dashboard",
    "👨‍🎓 Students": "Students",
    "📚 Modules": "Modules",
    "📊 Academic Performance": "Academic",
    "📅 Attendance": "Attendance",
    "🤖 AI Prediction": "Predictions",
    "⚠️ Risk Analysis": "Risk Analysis",
    "🧠 Explainable AI": "Explainable AI",
    "💡 Recommendations": "Recommendations",
    "🚨 Early Intervention": "Early Intervention",
    "📈 Analytics": "Analytics",
    "👤 Profile": "Profile",
}

STUDENT_MENU = {
    "🏠 Dashboard": "Dashboard",
    "📊 My Performance": "Academic",
    "📅 My Attendance": "Attendance",
    "🤖 AI Prediction": "Predictions",
    "💡 Recommendations": "Recommendations",
    "👤 Profile": "Profile",
}


def get_menu_for_role(role: str) -> dict:
    if role == "Admin":
        return ADMIN_MENU
    elif role == "Faculty":
        return FACULTY_MENU
    else:
        return STUDENT_MENU


# ─── Sidebar ─────────────────────────────────────────────────────
def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        # Logo / Branding
        st.markdown("""
        <div style="text-align:center;padding:20px 0 10px 0;">
            <div style="font-size:40px;">🎓</div>
            <div style="font-size:18px;font-weight:800;
                 background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 margin-top:4px;">AI Student Success</div>
            <div style="font-size:11px;color:#64748b;margin-top:2px;">
                Prediction & Intervention Platform
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # User info
        if st.session_state.authenticated:
            role = st.session_state.user_role
            role_colors = {"Admin": "#ef4444", "Faculty": "#f59e0b", "Student": "#10b981"}
            role_color = role_colors.get(role, "#818cf8")
            st.markdown(f"""
            <div style="padding:8px 12px;background:rgba(99,102,241,0.1);
                        border-radius:10px;margin-bottom:12px;">
                <div style="font-size:14px;font-weight:600;color:#e2e8f0;">
                    👤 {st.session_state.user_name}
                </div>
                <div style="font-size:11px;color:{role_color};font-weight:600;
                            text-transform:uppercase;letter-spacing:0.5px;">
                    {role}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Navigation
            menu = get_menu_for_role(role)
            for label, page in menu.items():
                if st.button(label, key=f"nav_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.session_state.selected_student_id = None
                    st.session_state.selected_module_id = None
                    st.rerun()

            st.markdown("---")

            # Logout
            if st.button("🚪 Logout", key="nav_logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state.authenticated = False
                st.session_state.current_page = "Login"
                st.rerun()


# ─── Page Router ─────────────────────────────────────────────────
def render_page():
    """Route to the appropriate page based on session state."""
    page = st.session_state.current_page

    if not st.session_state.authenticated:
        if st.session_state.get("show_signup", False):
            from pages.signup import render as signup_render
            signup_render()
        else:
            from pages.login import render as login_render
            login_render()
        return

    # Render sidebar for authenticated users
    render_sidebar()

    # Route pages
    if page == "Dashboard":
        from pages.dashboard import render
        render()
    elif page == "Students":
        if st.session_state.selected_student_id:
            # pyrefly: ignore [missing-import]
            from pages.student_profile import render
            render()
        else:
            from pages.students import render
            render()
    elif page == "Modules":
        from pages.modules import render
        render()
    elif page == "Academic":
        from pages.academic import render
        render()
    elif page == "Attendance":
        from pages.attendance import render
        render()
    elif page == "Predictions":
        from pages.predictions import render
        render()
    elif page == "Risk Analysis":
        from pages.risk_analysis import render
        render()
    elif page == "Explainable AI":
        from pages.explainable_ai import render
        render()
    elif page == "Recommendations":
        from pages.recommendations import render
        render()
    elif page == "Early Intervention":
        from pages.early_intervention import render
        render()
    elif page == "Analytics":
        # pyrefly: ignore [missing-import]
        from pages.analytics import render
        render()
    elif page == "Data Import":
        # pyrefly: ignore [missing-import]
        from pages.data_import import render
        render()
    elif page == "Model Performance":
        from pages.model_performance import render
        render()
    elif page == "Profile":
        from pages.profile import render
        render()
    elif page == "Settings":
        from pages.settings import render
        render()
    else:
        from pages.dashboard import render
        render()


# ─── Main ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    render_page()
