"""
Login Page
"""

import streamlit as st
from utils.ui_helpers import inject_css
from database.services.auth_service import AuthService


def render():
    inject_css()

    # Center the login form
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown("""
        <div style="text-align:center;margin-top:40px;margin-bottom:20px;">
            <div style="font-size:56px;">🎓</div>
            <div class="login-title">AI Student Success Platform</div>
            <div class="login-subtitle">Prediction & Early Intervention System</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            st.markdown("#### 🔐 Sign In")

            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            submitted = st.form_submit_button("🔓 LOGIN", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("❌ Please enter both email and password.")
                else:
                    user, error = AuthService.login(email.strip(), password)
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user["id"]
                        st.session_state.user_name = user["full_name"]
                        st.session_state.user_email = user["email"]
                        st.session_state.user_role = user["role"]
                        st.session_state.current_page = "Dashboard"
                        st.session_state.show_signup = False
                        st.rerun()

        st.markdown("<div style='text-align:center;margin-top:16px;'>", unsafe_allow_html=True)
        if st.button("Don't have an account? **Sign Up**", use_container_width=True):
            st.session_state.show_signup = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Demo credentials helper
        st.markdown("---")
        with st.expander("📋 Demo Credentials"):
            st.code("""
Admin Login:
  Email: admin@studentai.edu
  Password: Admin@123
            """)
