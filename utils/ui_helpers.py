"""
Shared UI helpers and styling for Streamlit pages.
"""

import streamlit as st


# ─── Custom CSS ────────────────────────────────────────────────────

CUSTOM_CSS = """
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Hide default Streamlit menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #e2e8f0;
    }

    /* KPI Card styling */
    .kpi-card {
        background: linear-gradient(135deg, #1e1e3f 0%, #2d2d5e 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 20px 24px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.2);
        border-color: rgba(99, 102, 241, 0.5);
    }
    .kpi-icon { font-size: 28px; margin-bottom: 6px; }
    .kpi-value {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 4px 0;
    }
    .kpi-label {
        font-size: 13px;
        color: #94a3b8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Risk badge */
    .risk-high {
        background: linear-gradient(135deg, #dc2626, #ef4444);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .risk-medium {
        background: linear-gradient(135deg, #d97706, #f59e0b);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .risk-low {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }

    /* Section headers */
    .section-header {
        font-size: 20px;
        font-weight: 700;
        color: #e2e8f0;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(99, 102, 241, 0.3);
    }

    /* Sidebar nav button */
    .nav-item {
        display: flex;
        align-items: center;
        padding: 10px 16px;
        border-radius: 10px;
        margin: 3px 0;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #cbd5e1;
        font-size: 14px;
        font-weight: 500;
    }
    .nav-item:hover {
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
    }
    .nav-item.active {
        background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.2));
        color: #a5b4fc;
        border-left: 3px solid #818cf8;
    }

    /* Streamlit button overrides */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
    }

    /* Success/Error boxes */
    .success-box {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 10px;
        padding: 12px 16px;
        color: #6ee7b7;
    }
    .error-box {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 10px;
        padding: 12px 16px;
        color: #fca5a5;
    }

    /* Profile card */
    .profile-card {
        background: linear-gradient(135deg, #1e1e3f, #2d2d5e);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    }

    /* Table styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-weight: 600;
    }

    /* Login card */
    .login-container {
        max-width: 440px;
        margin: 60px auto;
        background: linear-gradient(135deg, #1e1e3f, #2d2d5e);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }
    .login-title {
        text-align: center;
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .login-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 24px;
    }
</style>
"""


def inject_css():
    """Inject custom CSS into the Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def kpi_card(icon: str, value, label: str, delta: str = None):
    """Render a KPI metric card."""
    delta_html = f'<div style="font-size:12px;color:#6ee7b7;margin-top:4px;">▲ {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def risk_badge(level: str):
    """Return HTML for a risk badge."""
    cls = f"risk-{level.lower()}"
    return f'<span class="{cls}">{level}</span>'


def section_header(text: str):
    """Render a styled section header."""
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def show_success(message: str):
    st.success(f"✅ {message}")


def show_error(message: str):
    st.error(f"❌ {message}")


def show_warning(message: str):
    st.warning(f"⚠️ {message}")


def show_info(message: str):
    st.info(f"ℹ️ {message}")


def require_auth():
    """Check if user is authenticated. Redirect to login if not."""
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.session_state.current_page = "Login"
        st.rerun()
        return False
    return True


def require_role(*allowed_roles):
    """Check if user has an allowed role."""
    if not require_auth():
        return False
    role = st.session_state.get('user_role', '')
    if role not in allowed_roles:
        st.error("🚫 You do not have permission to access this page.")
        return False
    return True


def get_user_info():
    """Get current logged-in user info from session state."""
    return {
        "id": st.session_state.get("user_id"),
        "name": st.session_state.get("user_name", ""),
        "email": st.session_state.get("user_email", ""),
        "role": st.session_state.get("user_role", ""),
    }


# ─── Plotly Defaults ──────────────────────────────────────────────

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0"),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=11),
    ),
)

COLORS = {
    "primary": "#818cf8",
    "secondary": "#a78bfa",
    "accent": "#c084fc",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "palette": ["#818cf8", "#a78bfa", "#c084fc", "#f472b6", "#fb923c",
                "#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#06b6d4"],
}


DEPARTMENTS = [
    "AI & Data Science",
    "Computer Science Engineering",
    "Information Technology",
    "Electronics & Communication Engineering",
    "Electrical & Electronics Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
]
