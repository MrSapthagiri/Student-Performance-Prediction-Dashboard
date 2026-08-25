"""
Generate realistic student academic dataset with 1000 students.
Creates: students.csv, modules.csv, student_modules.csv
"""

import os
import sys
import random
import numpy as np
import pandas as pd
from faker import Faker

fake = Faker('en_IN')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────

DEPARTMENTS = [
    "AI & Data Science",
    "Computer Science Engineering",
    "Information Technology",
    "Electronics & Communication Engineering",
    "Electrical & Electronics Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
]

DEPT_SHORT = {
    "AI & Data Science": "AIDS",
    "Computer Science Engineering": "CSE",
    "Information Technology": "IT",
    "Electronics & Communication Engineering": "ECE",
    "Electrical & Electronics Engineering": "EEE",
    "Mechanical Engineering": "ME",
    "Civil Engineering": "CE",
}

YEARS = [1, 2, 3, 4]
SECTIONS = ["A", "B", "C"]
ACADEMIC_YEARS = ["2024-2025", "2025-2026"]

GENDER_OPTIONS = ["Male", "Female"]

# Module definitions per department (shared + department-specific)
COMMON_MODULES = [
    ("MA101", "Engineering Mathematics I", 1, 4, 100, 40),
    ("MA201", "Engineering Mathematics II", 2, 4, 100, 40),
    ("PH101", "Engineering Physics", 1, 3, 100, 40),
    ("CH101", "Engineering Chemistry", 1, 3, 100, 40),
    ("EN101", "Technical English", 1, 2, 100, 40),
    ("EN201", "Professional Communication", 2, 2, 100, 40),
]

DEPT_MODULES = {
    "AI & Data Science": [
        ("ADS301", "Python Programming", 3, 4, 100, 40),
        ("ADS302", "Data Structures", 3, 4, 100, 40),
        ("ADS401", "Machine Learning", 4, 4, 100, 40),
        ("ADS402", "Deep Learning", 4, 4, 100, 40),
        ("ADS501", "Artificial Intelligence", 5, 4, 100, 40),
        ("ADS502", "Natural Language Processing", 5, 3, 100, 40),
        ("ADS601", "Computer Vision", 6, 3, 100, 40),
        ("ADS602", "Data Analytics", 6, 4, 100, 40),
        ("ADS701", "Cloud Computing", 7, 3, 100, 40),
        ("ADS702", "Statistics", 7, 4, 100, 40),
    ],
    "Computer Science Engineering": [
        ("CSE301", "Data Structures", 3, 4, 100, 40),
        ("CSE302", "Database Management Systems", 3, 4, 100, 40),
        ("CSE401", "Operating Systems", 4, 4, 100, 40),
        ("CSE402", "Computer Networks", 4, 4, 100, 40),
        ("CSE501", "Software Engineering", 5, 3, 100, 40),
        ("CSE502", "Web Technology", 5, 3, 100, 40),
        ("CSE601", "Machine Learning", 6, 4, 100, 40),
        ("CSE602", "Cloud Computing", 6, 3, 100, 40),
        ("CSE701", "Artificial Intelligence", 7, 3, 100, 40),
        ("CSE702", "Cyber Security", 7, 3, 100, 40),
    ],
    "Information Technology": [
        ("IT301", "Data Structures", 3, 4, 100, 40),
        ("IT302", "Database Management Systems", 3, 4, 100, 40),
        ("IT401", "Operating Systems", 4, 4, 100, 40),
        ("IT402", "Computer Networks", 4, 4, 100, 40),
        ("IT501", "Web Technology", 5, 3, 100, 40),
        ("IT502", "Software Engineering", 5, 3, 100, 40),
        ("IT601", "Data Analytics", 6, 4, 100, 40),
        ("IT602", "Cloud Computing", 6, 3, 100, 40),
        ("IT701", "Information Security", 7, 3, 100, 40),
        ("IT702", "Mobile Computing", 7, 3, 100, 40),
    ],
    "Electronics & Communication Engineering": [
        ("ECE301", "Electronic Circuits", 3, 4, 100, 40),
        ("ECE302", "Signals & Systems", 3, 4, 100, 40),
        ("ECE401", "Digital Signal Processing", 4, 4, 100, 40),
        ("ECE402", "Communication Systems", 4, 4, 100, 40),
        ("ECE501", "VLSI Design", 5, 4, 100, 40),
        ("ECE502", "Embedded Systems", 5, 3, 100, 40),
        ("ECE601", "Wireless Communication", 6, 3, 100, 40),
        ("ECE602", "Antenna Design", 6, 3, 100, 40),
        ("ECE701", "IoT Systems", 7, 3, 100, 40),
        ("ECE702", "Robotics", 7, 3, 100, 40),
    ],
    "Electrical & Electronics Engineering": [
        ("EEE301", "Circuit Theory", 3, 4, 100, 40),
        ("EEE302", "Electromagnetic Fields", 3, 4, 100, 40),
        ("EEE401", "Power Systems", 4, 4, 100, 40),
        ("EEE402", "Control Systems", 4, 4, 100, 40),
        ("EEE501", "Electrical Machines", 5, 4, 100, 40),
        ("EEE502", "Power Electronics", 5, 3, 100, 40),
        ("EEE601", "Renewable Energy", 6, 3, 100, 40),
        ("EEE602", "High Voltage Engineering", 6, 3, 100, 40),
        ("EEE701", "Smart Grid Technology", 7, 3, 100, 40),
        ("EEE702", "Electric Vehicles", 7, 3, 100, 40),
    ],
    "Mechanical Engineering": [
        ("ME301", "Thermodynamics", 3, 4, 100, 40),
        ("ME302", "Fluid Mechanics", 3, 4, 100, 40),
        ("ME401", "Manufacturing Technology", 4, 4, 100, 40),
        ("ME402", "Strength of Materials", 4, 4, 100, 40),
        ("ME501", "Heat Transfer", 5, 4, 100, 40),
        ("ME502", "Machine Design", 5, 3, 100, 40),
        ("ME601", "CAD/CAM", 6, 3, 100, 40),
        ("ME602", "Automobile Engineering", 6, 3, 100, 40),
        ("ME701", "Robotics", 7, 3, 100, 40),
        ("ME702", "Industrial Engineering", 7, 3, 100, 40),
    ],
    "Civil Engineering": [
        ("CE301", "Structural Analysis", 3, 4, 100, 40),
        ("CE302", "Surveying", 3, 4, 100, 40),
        ("CE401", "Geotechnical Engineering", 4, 4, 100, 40),
        ("CE402", "Hydraulics", 4, 4, 100, 40),
        ("CE501", "Concrete Technology", 5, 4, 100, 40),
        ("CE502", "Transportation Engineering", 5, 3, 100, 40),
        ("CE601", "Environmental Engineering", 6, 3, 100, 40),
        ("CE602", "Estimation & Costing", 6, 3, 100, 40),
        ("CE701", "Construction Management", 7, 3, 100, 40),
        ("CE702", "Earthquake Engineering", 7, 3, 100, 40),
    ],
}


def generate_modules():
    """Generate modules.csv with all modules across departments."""
    rows = []
    mod_id = 1
    for dept in DEPARTMENTS:
        # Common modules (semesters 1-2) assigned to every dept
        for code, name, sem, credits, max_m, pass_m in COMMON_MODULES:
            dept_code = DEPT_SHORT[dept]
            rows.append({
                "module_id": mod_id,
                "module_code": f"{dept_code}_{code}",
                "module_name": name,
                "department": dept,
                "semester": sem,
                "credits": credits,
                "max_marks": max_m,
                "pass_marks": pass_m,
            })
            mod_id += 1
        # Department-specific modules
        for code, name, sem, credits, max_m, pass_m in DEPT_MODULES[dept]:
            rows.append({
                "module_id": mod_id,
                "module_code": code,
                "module_name": name,
                "department": dept,
                "semester": sem,
                "credits": credits,
                "max_marks": max_m,
                "pass_marks": pass_m,
            })
            mod_id += 1
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUTPUT_DIR, 'modules.csv'), index=False)
    print(f"✅ Generated {len(df)} modules → data/modules.csv")
    return df


def _latent_ability(prev_gpa):
    """Create a latent 'ability' score from previous GPA (0-10 scale) with noise."""
    base = prev_gpa / 10.0  # 0-1
    noise = np.random.normal(0, 0.08)
    return np.clip(base + noise, 0.05, 1.0)


def generate_students(n=1000):
    """Generate students.csv with 1000 realistic students."""
    rows = []
    used_emails = set()
    used_phones = set()
    used_reg = set()

    for i in range(1, n + 1):
        dept = random.choice(DEPARTMENTS)
        year = random.choice(YEARS)
        semester = random.choice([(year * 2) - 1, year * 2])
        section = random.choice(SECTIONS)
        academic_year = random.choice(ACADEMIC_YEARS)
        gender = random.choices(GENDER_OPTIONS, weights=[55, 45])[0]

        # Name generation
        if gender == "Male":
            first = fake.first_name_male()
        else:
            first = fake.first_name_female()
        last = fake.last_name()
        name = f"{first} {last}"

        # Unique email
        email_base = f"{first.lower()}.{last.lower()}{random.randint(1,99)}@college.edu"
        while email_base in used_emails:
            email_base = f"{first.lower()}.{last.lower()}{random.randint(100,999)}@college.edu"
        used_emails.add(email_base)

        # Unique phone
        phone = f"+91-{random.randint(7000000000, 9999999999)}"
        while phone in used_phones:
            phone = f"+91-{random.randint(7000000000, 9999999999)}"
        used_phones.add(phone)

        # Unique register number
        dept_code = DEPT_SHORT[dept]
        reg = f"{dept_code}{academic_year[:4]}{str(i).zfill(4)}"
        while reg in used_reg:
            reg = f"{dept_code}{academic_year[:4]}{str(i).zfill(4)}{random.randint(0,9)}"
        used_reg.add(reg)

        # ── Academic profile ──────────────────────────
        # Latent "student quality" drives everything
        quality = np.random.beta(5, 3)  # slightly right-skewed

        prev_gpa = np.clip(np.random.normal(quality * 8.5 + 1.5, 0.7), 2.0, 10.0)
        prev_percentage = np.clip(prev_gpa * 10 + np.random.normal(0, 3), 20, 100)

        ability = _latent_ability(prev_gpa)

        # Attendance (correlated with quality)
        classes_held = random.randint(60, 90)
        attend_pct = np.clip(
            np.random.normal(ability * 85 + 10, 10), 30, 100
        )
        classes_attended = int(np.clip(
            round(classes_held * attend_pct / 100), 0, classes_held
        ))
        attendance_percentage = round(classes_attended / classes_held * 100, 2)

        # Study habits (correlated with ability)
        study_hours = np.clip(np.random.normal(ability * 6 + 1, 1.2), 0.5, 12)
        assignment_completion = np.clip(np.random.normal(ability * 90 + 5, 10), 20, 100)
        online_learning = np.clip(np.random.normal(ability * 3 + 0.5, 0.8), 0, 8)
        library_usage = random.choices(
            [0, 1, 2, 3, 4, 5],
            weights=[10, 15, 25, 25, 15, 10] if ability > 0.5 else [30, 25, 20, 15, 7, 3]
        )[0]
        participation = np.clip(np.random.normal(ability * 80 + 10, 12), 10, 100)

        # Marks (driven by ability + attendance + study habits)
        combined = 0.4 * ability + 0.2 * (attendance_percentage / 100) + \
                   0.2 * (study_hours / 10) + 0.2 * (assignment_completion / 100)

        internal = np.clip(np.random.normal(combined * 35 + 5, 4), 5, 40)
        assignment_score = np.clip(np.random.normal(combined * 22 + 3, 3), 2, 25)
        quiz_score = np.clip(np.random.normal(combined * 18 + 2, 3), 2, 20)
        midterm_score = np.clip(np.random.normal(combined * 40 + 8, 6), 5, 50)
        final_exam = np.clip(np.random.normal(combined * 55 + 15, 8), 10, 75)

        # Normalize each component to percentage of its max, then weight
        final_score = round(
            (internal / 40) * 20 + (assignment_score / 25) * 10 + (quiz_score / 20) * 10 +
            (midterm_score / 50) * 25 + (final_exam / 75) * 35, 2
        )
        final_score = np.clip(final_score, 5, 100)

        # Grade and pass/fail
        if final_score >= 90:
            grade = "O"
        elif final_score >= 80:
            grade = "A+"
        elif final_score >= 70:
            grade = "A"
        elif final_score >= 60:
            grade = "B+"
        elif final_score >= 50:
            grade = "B"
        elif final_score >= 40:
            grade = "C"
        else:
            grade = "F"

        pass_fail = "Pass" if final_score >= 40 else "Fail"

        # Risk level (composite heuristic, NOT target leakage)
        risk_score = 0
        if attendance_percentage < 60:
            risk_score += 3
        elif attendance_percentage < 75:
            risk_score += 1.5
        if study_hours < 2:
            risk_score += 2
        elif study_hours < 3:
            risk_score += 1
        if assignment_completion < 50:
            risk_score += 2
        elif assignment_completion < 70:
            risk_score += 1
        if prev_gpa < 5:
            risk_score += 2
        elif prev_gpa < 6.5:
            risk_score += 1
        if participation < 40:
            risk_score += 1.5

        if risk_score >= 6:
            risk_level = "High"
        elif risk_score >= 3:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        rows.append({
            "student_id": i,
            "register_number": reg,
            "student_name": name,
            "email": email_base,
            "phone": phone,
            "gender": gender,
            "department": dept,
            "course": f"B.E. {dept}" if dept not in ["AI & Data Science"] else f"B.Tech. {dept}",
            "year": year,
            "semester": semester,
            "section": section,
            "academic_year": academic_year,
            "previous_gpa": round(prev_gpa, 2),
            "previous_percentage": round(prev_percentage, 2),
            "internal_marks": round(internal, 2),
            "assignment_score": round(assignment_score, 2),
            "quiz_score": round(quiz_score, 2),
            "midterm_score": round(midterm_score, 2),
            "final_exam_score": round(final_exam, 2),
            "classes_held": classes_held,
            "classes_attended": classes_attended,
            "attendance_percentage": round(attendance_percentage, 2),
            "study_hours_per_day": round(study_hours, 2),
            "assignment_completion_rate": round(assignment_completion, 2),
            "online_learning_hours": round(online_learning, 2),
            "library_usage": library_usage,
            "participation_score": round(participation, 2),
            "final_score": round(final_score, 2),
            "grade": grade,
            "pass_fail": pass_fail,
            "risk_level": risk_level,
        })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUTPUT_DIR, 'students.csv'), index=False)
    print(f"✅ Generated {len(df)} students → data/students.csv")
    print(f"   Risk distribution: {df['risk_level'].value_counts().to_dict()}")
    print(f"   Pass/Fail: {df['pass_fail'].value_counts().to_dict()}")
    print(f"   Dept distribution: {df['department'].value_counts().to_dict()}")
    return df


def generate_student_modules(students_df, modules_df):
    """Generate student_modules.csv linking students to their department modules."""
    rows = []
    sm_id = 1

    for _, student in students_df.iterrows():
        dept = student['department']
        sem = student['semester']
        ability = _latent_ability(student['previous_gpa'])

        # Get modules for this student's department and current/past semesters
        dept_mods = modules_df[
            (modules_df['department'] == dept) & (modules_df['semester'] <= sem)
        ]

        # Pick 4-6 modules for the student (realistic course load)
        n_mods = min(len(dept_mods), random.randint(4, 6))
        if n_mods == 0:
            continue
        selected = dept_mods.sample(n=n_mods, replace=False)

        for _, mod in selected.iterrows():
            combined = 0.4 * ability + \
                       0.25 * (student['attendance_percentage'] / 100) + \
                       0.2 * (student['study_hours_per_day'] / 10) + \
                       0.15 * (student['assignment_completion_rate'] / 100)

            # Add per-module noise
            mod_noise = np.random.normal(0, 0.08)
            mod_ability = np.clip(combined + mod_noise, 0.05, 1.0)

            att_pct = np.clip(
                np.random.normal(student['attendance_percentage'], 5),
                30, 100
            )
            internal = np.clip(np.random.normal(mod_ability * 35 + 5, 4), 3, 40)
            assignment = np.clip(np.random.normal(mod_ability * 22 + 3, 3), 2, 25)
            quiz = np.clip(np.random.normal(mod_ability * 18 + 2, 3), 2, 20)
            midterm = np.clip(np.random.normal(mod_ability * 40 + 8, 5), 5, 50)
            final_exam = np.clip(np.random.normal(mod_ability * 55 + 15, 7), 8, 75)

            total = round(
                (internal / 40) * 20 + (assignment / 25) * 10 + (quiz / 20) * 10 +
                (midterm / 50) * 25 + (final_exam / 75) * 35, 2
            )
            total = np.clip(total, 5, 100)

            if total >= 90: grade = "O"
            elif total >= 80: grade = "A+"
            elif total >= 70: grade = "A"
            elif total >= 60: grade = "B+"
            elif total >= 50: grade = "B"
            elif total >= 40: grade = "C"
            else: grade = "F"

            result = "Pass" if total >= 40 else "Fail"

            rows.append({
                "id": sm_id,
                "student_id": student['student_id'],
                "module_id": mod['module_id'],
                "attendance_percentage": round(att_pct, 2),
                "internal_marks": round(internal, 2),
                "assignment_marks": round(assignment, 2),
                "quiz_marks": round(quiz, 2),
                "midterm_marks": round(midterm, 2),
                "final_exam_marks": round(final_exam, 2),
                "total_marks": round(total, 2),
                "grade": grade,
                "result": result,
            })
            sm_id += 1

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUTPUT_DIR, 'student_modules.csv'), index=False)
    print(f"✅ Generated {len(df)} student-module records → data/student_modules.csv")
    return df


if __name__ == "__main__":
    print("=" * 60)
    print("  Generating Student Success AI Dataset")
    print("=" * 60)

    modules_df = generate_modules()
    students_df = generate_students(1000)
    sm_df = generate_student_modules(students_df, modules_df)

    print("\n" + "=" * 60)
    print("  Dataset generation complete!")
    print("=" * 60)
