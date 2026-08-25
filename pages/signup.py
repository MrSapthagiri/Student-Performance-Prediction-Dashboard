"""
Sign Up Page
"""

import streamlit as st
from utils.ui_helpers import inject_css
from database.services.auth_service import AuthService


def render():
    inject_css()

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown("""
        <div style="text-align:center;margin-top:40px;margin-bottom:20px;">
            <div style="font-size:56px;">🎓</div>
            <div class="login-title">Create Account</div>
            <div class="login-subtitle">Join the AI Student Success Platform</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("signup_form", clear_on_submit=False):
            st.markdown("#### 📝 Sign Up")

            full_name = st.text_input("Full Name", placeholder="Enter your full name")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            role = st.selectbox("Role", ["Student", "Faculty"])

            submitted = st.form_submit_button("📝 SIGN UP", use_container_width=True)

            if submitted:
                # Validation
                if not full_name or not email or not password or not confirm_password:
                    st.error("❌ Please fill in all fields.")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match.")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters.")
                elif "@" not in email:
                    st.error("❌ Please enter a valid email address.")
                else:
                    user, error = AuthService.signup(
                        full_name.strip(), email.strip(), password, role
                    )
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        st.success("✅ Account created successfully! Please login.")
                        st.balloons()

        if st.button("Already have an account? **Sign In**", use_container_width=True):
            st.session_state.show_signup = False
            st.rerun()
