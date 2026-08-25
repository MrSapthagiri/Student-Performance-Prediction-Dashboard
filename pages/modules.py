"""
Module Management Page — Full CRUD.
"""

import streamlit as st
import pandas as pd
from utils.ui_helpers import (
    inject_css, section_header, require_auth, require_role,
    show_success, show_error, DEPARTMENTS, kpi_card, PLOTLY_LAYOUT, COLORS
)
from database.services.data_service import DataService
import plotly.graph_objects as go


def render():
    inject_css()
    if not require_role("Admin", "Faculty"):
        return

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        📚 Module Management
    </h1>
    """, unsafe_allow_html=True)

    # Controls
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 1.5, 1, 1.2])
    with ctrl1:
        search = st.text_input("🔍 Search modules", placeholder="Name or code...", label_visibility="collapsed", key="mod_search")
    with ctrl2:
        dept_filter = st.selectbox("Department", ["All"] + DEPARTMENTS, key="mod_dept")
    with ctrl3:
        sem_filter = st.selectbox("Semester", [0] + list(range(1, 9)),
                                  format_func=lambda x: "All" if x == 0 else f"Sem {x}", key="mod_sem")
    with ctrl4:
        if st.button("➕ Add Module", use_container_width=True, type="primary"):
            st.session_state["show_add_module"] = True

    # Add Module Form
    if st.session_state.get("show_add_module", False):
        section_header("➕ Add New Module")
        with st.form("add_module_form", clear_on_submit=True):
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                new_mid = st.number_input("Module ID", value=DataService.get_next_module_id(), min_value=1)
                new_code = st.text_input("Module Code")
                new_name = st.text_input("Module Name")
            with mc2:
                new_dept = st.selectbox("Department", DEPARTMENTS, key="new_mod_dept")
                new_sem = st.selectbox("Semester", list(range(1, 9)), key="new_mod_sem")
            with mc3:
                new_credits = st.number_input("Credits", value=3, min_value=1, max_value=6)
                new_max = st.number_input("Max Marks", value=100, min_value=50, max_value=200)
                new_pass = st.number_input("Pass Marks", value=40, min_value=20, max_value=100)

            fc1, fc2 = st.columns(2)
            with fc1:
                submitted = st.form_submit_button("💾 Save Module", use_container_width=True, type="primary")
            with fc2:
                cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)

            if submitted:
                if not new_code or not new_name:
                    show_error("Module Code and Name are required.")
                else:
                    try:
                        DataService.create_module({
                            "module_id": new_mid, "module_code": new_code,
                            "module_name": new_name, "department": new_dept,
                            "semester": new_sem, "credits": new_credits,
                            "max_marks": new_max, "pass_marks": new_pass,
                        })
                        show_success(f"Module '{new_name}' added!")
                        st.session_state["show_add_module"] = False
                        st.rerun()
                    except Exception as e:
                        show_error(f"Failed: {e}")
            if cancelled:
                st.session_state["show_add_module"] = False
                st.rerun()

    # Fetch modules
    page_size = 20
    page_num = st.session_state.get("mod_page", 1)

    try:
        modules, total = DataService.get_modules(
            offset=(page_num - 1) * page_size, limit=page_size,
            search=search if search else None,
            department=dept_filter, semester=sem_filter,
        )
    except Exception as e:
        st.error(f"Database error: {e}")
        return

    total_pages = max(1, (total + page_size - 1) // page_size)
    st.markdown(f"<div style='color:#94a3b8;font-size:13px;margin:8px 0;'>Showing {len(modules)} of {total} modules</div>", unsafe_allow_html=True)

    # Module list
    if not modules:
        st.info("No modules found.")
    else:
        edit_mod = st.session_state.get("edit_module_id")
        del_mod = st.session_state.get("delete_module_id")
        view_mod = st.session_state.get("view_module_id")

        for m in modules:
            with st.container():
                cols = st.columns([0.8, 1.5, 2.5, 2, 0.8, 0.8, 0.8])
                cols[0].markdown(f"**{m.module_id}**")
                cols[1].markdown(f"`{m.module_code}`")
                cols[2].markdown(f"**{m.module_name}**")
                cols[3].markdown(f"{m.department}")
                cols[4].markdown(f"Sem {m.semester}")
                cols[5].markdown(f"{m.credits} cr")
                cols[6].markdown(f"{m.max_marks}")

                ac1, ac2, ac3 = st.columns([1, 1, 1])
                with ac1:
                    if st.button("👁️ View", key=f"view_mod_{m.module_id}", use_container_width=True):
                        st.session_state["view_module_id"] = m.module_id
                        st.rerun()
                with ac2:
                    if st.button("✏️ Edit", key=f"edit_mod_{m.module_id}", use_container_width=True):
                        st.session_state["edit_module_id"] = m.module_id
                        st.rerun()
                with ac3:
                    if st.button("🗑️ Delete", key=f"del_mod_{m.module_id}", use_container_width=True):
                        st.session_state["delete_module_id"] = m.module_id
                        st.rerun()
                st.markdown("---")

        # View Module Details
        if view_mod:
            mod = DataService.get_module(view_mod)
            if mod:
                section_header(f"📚 {mod.module_name} ({mod.module_code})")
                stats = DataService.get_module_stats(view_mod)
                vc1, vc2, vc3, vc4 = st.columns(4)
                with vc1: kpi_card("👨‍🎓", stats['enrolled'], "Enrolled")
                with vc2: kpi_card("📊", f"{stats['avg_marks']:.1f}", "Avg Marks")
                with vc3: kpi_card("🏆", f"{stats['highest']:.1f}", "Highest")
                with vc4: kpi_card("📉", f"{stats['lowest']:.1f}", "Lowest")

                vc5, vc6, vc7 = st.columns(3)
                with vc5: kpi_card("✅", f"{stats['pass_rate']:.1f}%", "Pass Rate")
                with vc6: kpi_card("❌", f"{stats['fail_rate']:.1f}%", "Fail Rate")
                with vc7: kpi_card("📅", f"{stats['avg_attendance']:.1f}%", "Avg Attendance")

                if st.button("Close Details", key="close_mod_view"):
                    st.session_state["view_module_id"] = None
                    st.rerun()

        # Edit Module
        if edit_mod:
            mod = DataService.get_module(edit_mod)
            if mod:
                section_header(f"✏️ Edit Module: {mod.module_name}")
                with st.form(f"edit_mod_form_{edit_mod}"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        ed_name = st.text_input("Name", value=mod.module_name)
                        ed_code = st.text_input("Code", value=mod.module_code)
                        ed_dept = st.selectbox("Dept", DEPARTMENTS,
                                               index=DEPARTMENTS.index(mod.department) if mod.department in DEPARTMENTS else 0)
                    with ec2:
                        ed_sem = st.selectbox("Semester", list(range(1, 9)), index=(mod.semester or 1) - 1)
                        ed_credits = st.number_input("Credits", value=mod.credits or 3, min_value=1, max_value=6)
                        ed_max = st.number_input("Max Marks", value=mod.max_marks or 100)
                        ed_pass = st.number_input("Pass Marks", value=mod.pass_marks or 40)
                    fc1, fc2 = st.columns(2)
                    with fc1:
                        if st.form_submit_button("💾 Save", use_container_width=True, type="primary"):
                            DataService.update_module(edit_mod, {
                                "module_name": ed_name, "module_code": ed_code,
                                "department": ed_dept, "semester": ed_sem,
                                "credits": ed_credits, "max_marks": ed_max, "pass_marks": ed_pass,
                            })
                            show_success("Module updated!")
                            st.session_state["edit_module_id"] = None
                            st.rerun()
                    with fc2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state["edit_module_id"] = None
                            st.rerun()

        # Delete Module
        if del_mod:
            mod = DataService.get_module(del_mod)
            if mod:
                st.warning(f"⚠️ Are you sure you want to archive **{mod.module_name}**?")
                dc1, dc2 = st.columns(2)
                with dc1:
                    if st.button("🗑️ Confirm", key="confirm_del_mod", type="primary", use_container_width=True):
                        DataService.delete_module(del_mod)
                        show_success(f"Module '{mod.module_name}' archived.")
                        st.session_state["delete_module_id"] = None
                        st.rerun()
                with dc2:
                    if st.button("❌ Cancel", key="cancel_del_mod", use_container_width=True):
                        st.session_state["delete_module_id"] = None
                        st.rerun()

    # Pagination
    pc1, pc2, pc3, pc4 = st.columns([1, 1, 2, 1])
    with pc1:
        if st.button("◀ Prev", disabled=(page_num <= 1), key="mod_prev", use_container_width=True):
            st.session_state["mod_page"] = page_num - 1
            st.rerun()
    with pc2:
        st.markdown(f"<div style='text-align:center;padding:8px;color:#94a3b8;'>Page {page_num}/{total_pages}</div>", unsafe_allow_html=True)
    with pc3:
        if st.button("Next ▶", disabled=(page_num >= total_pages), key="mod_next", use_container_width=True):
            st.session_state["mod_page"] = page_num + 1
            st.rerun()
