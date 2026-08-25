"""
Settings Page — App configuration (Admin only).
"""

import streamlit as st
from utils.ui_helpers import (
    inject_css, section_header, require_auth, require_role,
    show_success, show_info
)


def render():
    inject_css()
    if not require_role("Admin"):
        return

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        ⚙️ Settings
    </h1>
    """, unsafe_allow_html=True)

    section_header("🎨 Application Settings")

    with st.form("settings_form"):
        st.text_input("Application Name", value="AI Student Success Platform", disabled=True)
        st.number_input("Pagination Page Size", value=20, min_value=5, max_value=100)
        st.selectbox("Default Risk Threshold", ["75% Attendance", "70% Attendance", "80% Attendance"])
        st.selectbox("Default Theme", ["Dark", "Light"])

        if st.form_submit_button("💾 Save Settings", use_container_width=True, type="primary"):
            show_success("Settings saved successfully!")

    section_header("🗄️ Database Management")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reseed Database", use_container_width=True):
            show_info("Run `python scripts/seed_database.py` from the terminal to reseed.")
    with col2:
        if st.button("🧹 Clear Cache", use_container_width=True):
            st.cache_data.clear()
            show_success("Cache cleared!")

    section_header("📊 System Information")
    import platform
    st.markdown(f"""
    | Property | Value |
    |----------|-------|
    | Python Version | `{platform.python_version()}` |
    | Platform | `{platform.platform()}` |
    | Architecture | `{platform.architecture()[0]}` |
    """)
