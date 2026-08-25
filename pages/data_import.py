"""
Data Import Page — Upload CSV/Excel files and import into database.
"""

import streamlit as st
import pandas as pd
from utils.ui_helpers import (
    inject_css, section_header, require_auth, require_role,
    show_success, show_error, kpi_card
)
from database.services.data_service import DataService
from database.connection import get_db
from database.models import Student, Module, StudentModule


def render():
    inject_css()
    if not require_role("Admin"):
        return

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        📁 Data Import
    </h1>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👨‍🎓 Import Students", "📚 Import Modules", "📝 Import Academic Records"])

    # ── Students ──
    with tab1:
        section_header("Upload Student Data")
        uploaded = st.file_uploader("Choose CSV or Excel file", type=["csv", "xlsx", "xls"], key="import_students")

        if uploaded:
            try:
                if uploaded.name.endswith('.csv'):
                    df = pd.read_csv(uploaded)
                else:
                    df = pd.read_excel(uploaded)

                st.success(f"📄 File loaded: {len(df)} rows, {len(df.columns)} columns")

                # Preview
                section_header("Preview")
                st.dataframe(df.head(10), use_container_width=True, hide_index=True)

                # Column mapping info
                with st.expander("📋 Expected Columns"):
                    st.code("""
Required: student_id, register_number, student_name, email, department
Optional: phone, gender, course, year, semester, section, academic_year,
          previous_gpa, previous_percentage, internal_marks, assignment_score,
          quiz_score, midterm_score, final_exam_score, classes_held,
          classes_attended, attendance_percentage, study_hours_per_day,
          assignment_completion_rate, online_learning_hours, library_usage,
          participation_score, final_score, grade, pass_fail, risk_level
                    """)

                # Validation
                required = ['student_id', 'student_name', 'email', 'department']
                missing = [c for c in required if c not in df.columns]
                if missing:
                    st.error(f"❌ Missing required columns: {', '.join(missing)}")
                else:
                    st.success("✅ All required columns present.")

                    if st.button("🚀 Import Students", type="primary", key="btn_import_students"):
                        with st.spinner("Importing..."):
                            db = get_db()
                            try:
                                inserted = 0
                                duplicates = 0
                                errors = 0

                                for _, row in df.iterrows():
                                    try:
                                        sid = int(row['student_id'])
                                        existing = db.query(Student).filter(Student.student_id == sid).first()
                                        if existing:
                                            duplicates += 1
                                            continue

                                        data = {col: row[col] for col in df.columns if hasattr(Student, col)}
                                        data['student_id'] = sid
                                        student = Student(**data)
                                        db.add(student)
                                        inserted += 1

                                        if inserted % 100 == 0:
                                            db.commit()
                                    except Exception:
                                        errors += 1

                                db.commit()

                                # Summary
                                section_header("📊 Import Summary")
                                sc1, sc2, sc3, sc4 = st.columns(4)
                                with sc1: kpi_card("📄", len(df), "Total Rows")
                                with sc2: kpi_card("✅", inserted, "Inserted")
                                with sc3: kpi_card("🔄", duplicates, "Duplicates")
                                with sc4: kpi_card("❌", errors, "Errors")
                            finally:
                                db.close()
            except Exception as e:
                show_error(f"Failed to read file: {e}")

    # ── Modules ──
    with tab2:
        section_header("Upload Module Data")
        uploaded_mod = st.file_uploader("Choose CSV or Excel file", type=["csv", "xlsx", "xls"], key="import_modules")

        if uploaded_mod:
            try:
                if uploaded_mod.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_mod)
                else:
                    df = pd.read_excel(uploaded_mod)

                st.success(f"📄 File loaded: {len(df)} rows")
                st.dataframe(df.head(10), use_container_width=True, hide_index=True)

                required = ['module_id', 'module_code', 'module_name', 'department']
                missing = [c for c in required if c not in df.columns]

                if missing:
                    st.error(f"❌ Missing: {', '.join(missing)}")
                else:
                    if st.button("🚀 Import Modules", type="primary", key="btn_import_modules"):
                        with st.spinner("Importing..."):
                            db = get_db()
                            try:
                                inserted = duplicates = errors = 0
                                for _, row in df.iterrows():
                                    try:
                                        mid = int(row['module_id'])
                                        if db.query(Module).filter(Module.module_id == mid).first():
                                            duplicates += 1
                                            continue
                                        data = {col: row[col] for col in df.columns if hasattr(Module, col)}
                                        data['module_id'] = mid
                                        db.add(Module(**data))
                                        inserted += 1
                                    except Exception:
                                        errors += 1
                                db.commit()
                                sc1, sc2, sc3 = st.columns(3)
                                with sc1: kpi_card("✅", inserted, "Inserted")
                                with sc2: kpi_card("🔄", duplicates, "Duplicates")
                                with sc3: kpi_card("❌", errors, "Errors")
                            finally:
                                db.close()
            except Exception as e:
                show_error(f"Failed: {e}")

    # ── Academic Records ──
    with tab3:
        section_header("Upload Academic Records")
        uploaded_sm = st.file_uploader("Choose CSV or Excel file", type=["csv", "xlsx", "xls"], key="import_sm")

        if uploaded_sm:
            try:
                if uploaded_sm.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_sm)
                else:
                    df = pd.read_excel(uploaded_sm)

                st.success(f"📄 File loaded: {len(df)} rows")
                st.dataframe(df.head(10), use_container_width=True, hide_index=True)

                required = ['student_id', 'module_id']
                missing = [c for c in required if c not in df.columns]

                if missing:
                    st.error(f"❌ Missing: {', '.join(missing)}")
                else:
                    if st.button("🚀 Import Records", type="primary", key="btn_import_sm"):
                        with st.spinner("Importing..."):
                            db = get_db()
                            try:
                                inserted = duplicates = errors = 0
                                for _, row in df.iterrows():
                                    try:
                                        sid = int(row['student_id'])
                                        mid = int(row['module_id'])
                                        if db.query(StudentModule).filter(
                                            StudentModule.student_id == sid,
                                            StudentModule.module_id == mid,
                                        ).first():
                                            duplicates += 1
                                            continue
                                        data = {col: row[col] for col in df.columns
                                                if hasattr(StudentModule, col) and col not in ['id']}
                                        db.add(StudentModule(**data))
                                        inserted += 1
                                        if inserted % 200 == 0:
                                            db.commit()
                                    except Exception:
                                        errors += 1
                                db.commit()
                                sc1, sc2, sc3 = st.columns(3)
                                with sc1: kpi_card("✅", inserted, "Inserted")
                                with sc2: kpi_card("🔄", duplicates, "Duplicates")
                                with sc3: kpi_card("❌", errors, "Errors")
                            finally:
                                db.close()
            except Exception as e:
                show_error(f"Failed: {e}")
