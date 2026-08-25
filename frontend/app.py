import streamlit as st

st.set_page_config(
    page_title="AI Student Success Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern SaaS look
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    h1, h2, h3 {
        color: #1e3a8a;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        border-color: #1d4ed8;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# App Navigation
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # When using pages in Streamlit 1.x, we just let the user navigate to login or signup
    # Since we want a robust multi-page app, we will use st.navigation or traditional st.sidebar
    st.title("🎓 AI Student Success Platform")
    st.write("Please select 'Login' or 'Sign Up' from the sidebar to continue.")
else:
    st.title("🎓 Welcome to the AI Student Success Dashboard")
    st.write("Navigate using the sidebar to view Analytics, Students, and Predictions.")
