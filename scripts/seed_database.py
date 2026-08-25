"""
Seed the PostgreSQL database from CSV files.
Creates tables, reads CSVs, validates, and inserts records.
Also creates the initial admin user.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

from database.connection import engine, SessionLocal, init_db
from database.models import Student, Module, StudentModule, User
from database.repositories.user_repo import UserRepository


DATA_DIR = os.path.join(PROJECT_ROOT, 'data')


def seed_students(db, csv_path):
    """Read students.csv and insert into DB, skipping duplicates."""
    df = pd.read_csv(csv_path)
    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        existing = db.query(Student).filter(Student.student_id == int(row['student_id'])).first()
        if existing:
            skipped += 1
            continue
        student = Student(
            student_id=int(row['student_id']),
            register_number=str(row['register_number']),
            student_name=str(row['student_name']),
            email=str(row['email']),
            phone=str(row['phone']),
            gender=str(row['gender']),
            department=str(row['department']),
            course=str(row['course']),
            year=int(row['year']),
            semester=int(row['semester']),
            section=str(row['section']),
            academic_year=str(row['academic_year']),
            previous_gpa=float(row['previous_gpa']),
            previous_percentage=float(row['previous_percentage']),
            internal_marks=float(row['internal_marks']),
            assignment_score=float(row['assignment_score']),
            quiz_score=float(row['quiz_score']),
            midterm_score=float(row['midterm_score']),
            final_exam_score=float(row['final_exam_score']),
            classes_held=int(row['classes_held']),
            classes_attended=int(row['classes_attended']),
            attendance_percentage=float(row['attendance_percentage']),
            study_hours_per_day=float(row['study_hours_per_day']),
            assignment_completion_rate=float(row['assignment_completion_rate']),
            online_learning_hours=float(row['online_learning_hours']),
            library_usage=int(row['library_usage']),
            participation_score=float(row['participation_score']),
            final_score=float(row['final_score']),
            grade=str(row['grade']),
            pass_fail=str(row['pass_fail']),
            risk_level=str(row['risk_level']),
        )
        db.add(student)
        inserted += 1

    db.commit()
    print(f"  Students: {inserted} inserted, {skipped} skipped (duplicates)")


def seed_modules(db, csv_path):
    """Read modules.csv and insert into DB, skipping duplicates."""
    df = pd.read_csv(csv_path)
    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        existing = db.query(Module).filter(Module.module_id == int(row['module_id'])).first()
        if existing:
            skipped += 1
            continue
        module = Module(
            module_id=int(row['module_id']),
            module_code=str(row['module_code']),
            module_name=str(row['module_name']),
            department=str(row['department']),
            semester=int(row['semester']),
            credits=int(row['credits']),
            max_marks=int(row['max_marks']),
            pass_marks=int(row['pass_marks']),
        )
        db.add(module)
        inserted += 1

    db.commit()
    print(f"  Modules: {inserted} inserted, {skipped} skipped (duplicates)")


def seed_student_modules(db, csv_path):
    """Read student_modules.csv and insert into DB, skipping duplicates."""
    df = pd.read_csv(csv_path)
    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        existing = db.query(StudentModule).filter(
            StudentModule.student_id == int(row['student_id']),
            StudentModule.module_id == int(row['module_id']),
        ).first()
        if existing:
            skipped += 1
            continue
        sm = StudentModule(
            student_id=int(row['student_id']),
            module_id=int(row['module_id']),
            attendance_percentage=float(row['attendance_percentage']),
            internal_marks=float(row['internal_marks']),
            assignment_marks=float(row['assignment_marks']),
            quiz_marks=float(row['quiz_marks']),
            midterm_marks=float(row['midterm_marks']),
            final_exam_marks=float(row['final_exam_marks']),
            total_marks=float(row['total_marks']),
            grade=str(row['grade']),
            result=str(row['result']),
        )
        db.add(sm)
        inserted += 1
        # Commit in batches for performance
        if inserted % 500 == 0:
            db.commit()

    db.commit()
    print(f"  Student-Modules: {inserted} inserted, {skipped} skipped (duplicates)")


def seed_admin(db):
    """Create the initial admin user from .env values."""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@studentai.edu")
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin@123")
    admin_name = os.getenv("ADMIN_NAME", "System Administrator")

    existing = db.query(User).filter(User.email == admin_email).first()
    if existing:
        print(f"  Admin user already exists: {admin_email}")
        return

    UserRepository.create(db, admin_name, admin_email, admin_password, "Admin")
    print(f"  Admin user created: {admin_email}")


def main():
    print("=" * 60)
    print("  Seeding Student Success AI Database")
    print("=" * 60)

    # 1. Create tables
    print("\n📦 Creating tables...")
    init_db()
    print("  ✅ Tables created")

    db = SessionLocal()
    try:
        # 2. Seed admin
        print("\n👤 Creating admin user...")
        seed_admin(db)

        # 3. Seed students
        students_path = os.path.join(DATA_DIR, 'students.csv')
        if os.path.exists(students_path):
            print("\n👨‍🎓 Seeding students...")
            seed_students(db, students_path)
        else:
            print(f"\n⚠️  {students_path} not found. Run generate_dataset.py first.")

        # 4. Seed modules
        modules_path = os.path.join(DATA_DIR, 'modules.csv')
        if os.path.exists(modules_path):
            print("\n📚 Seeding modules...")
            seed_modules(db, modules_path)
        else:
            print(f"\n⚠️  {modules_path} not found. Run generate_dataset.py first.")

        # 5. Seed student-modules
        sm_path = os.path.join(DATA_DIR, 'student_modules.csv')
        if os.path.exists(sm_path):
            print("\n📝 Seeding student-module records...")
            seed_student_modules(db, sm_path)
        else:
            print(f"\n⚠️  {sm_path} not found. Run generate_dataset.py first.")

        print("\n" + "=" * 60)
        print("  ✅ Database seeding complete!")
        print("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    main()
