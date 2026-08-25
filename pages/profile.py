"""
Profile Page — View and update user profile.
"""

import streamlit as st
from utils.ui_helpers import inject_css, section_header, require_auth, show_success, show_error, kpi_card
from database.services.auth_service import AuthService


def render():
    inject_css()
    if not require_auth():
        return

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        👤 Profile
    </h1>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get("user_id")
    user_name = st.session_state.get("user_name", "")
    user_email = st.session_state.get("user_email", "")
    user_role = st.session_state.get("user_role", "")

    # Display current info
    section_header("📋 Current Information")
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("👤", user_name, "Full Name")
    with c2:
        kpi_card("📧", user_email, "Email")
    with c3:
        kpi_card("🎭", user_role, "Role")

    # Edit profile
    section_header("✏️ Update Profile")
    with st.form("profile_form"):
        new_name = st.text_input("Full Name", value=user_name)
        new_email = st.text_input("Email", value=user_email)

        st.markdown("---")
        st.markdown("**Change Password** (leave blank to keep current)")
        new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
        confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")

        if st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary"):
            updates = {}
            if new_name and new_name != user_name:
                updates["full_name"] = new_name
            if new_email and new_email != user_email:
                updates["email"] = new_email
            if new_password:
                if new_password != confirm_password:
                    show_error("Passwords do not match.")
                elif len(new_password) < 6:
                    show_error("Password must be at least 6 characters.")
                else:
                    updates["password"] = new_password

            if updates:
                try:
                    result = AuthService.update_profile(user_id, **updates)
                    if result:
                        if "full_name" in updates:
                            st.session_state.user_name = updates["full_name"]
                        if "email" in updates:
                            st.session_state.user_email = updates["email"]
                        show_success("Profile updated successfully!")
                        st.rerun()
                    else:
                        show_error("Failed to update profile.")
                except Exception as e:
                    show_error(f"Error: {e}")
            else:
                st.info("No changes to save.")
