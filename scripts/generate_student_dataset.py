import random
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "dataset" / "student_performance.csv"

random.seed(42)

existing = pd.read_csv(DATASET_PATH)

rows = []
for idx in range(1, 100001):
    if idx <= len(existing):
        row = existing.iloc[idx - 1].to_dict()
        rows.append(row)
        continue

    age = random.randint(15, 22)
    gender = random.choice(["Male", "Female", "Other"])
    class_name = str(random.choice(["9", "10", "11", "12"]))
    attendance = round(random.uniform(55, 100), 1)
    study_hours = round(random.uniform(1, 12), 1)
    assignments_completed = round(random.uniform(0, 15), 1)
    quiz_score = round(random.uniform(40, 100), 1)
    midterm_marks = round(random.uniform(40, 100), 1)
    final_exam_marks = round(random.uniform(40, 100), 1)
    internet_access = random.choice(["Yes", "No"])
    parental_education = random.choice(["High School", "Secondary", "Bachelor", "Master"])
    extra_curricular = random.choice(["Yes", "No"])
    sleep_hours = round(random.uniform(4, 10), 1)
    previous_grade = random.choice(["A", "B", "C", "D"])

    composite_score = (
        attendance * 0.35
        + study_hours * 3.8
        + assignments_completed * 2.5
        + quiz_score * 0.35
        + midterm_marks * 0.35
        + final_exam_marks * 0.35
    )

    if composite_score >= 820:
        performance = "Excellent"
    elif composite_score >= 700:
        performance = "Good"
    elif composite_score >= 590:
        performance = "Average"
    else:
        performance = "Poor"

    rows.append(
        {
            "Student_ID": idx,
            "Gender": gender,
            "Age": age,
            "Class": class_name,
            "Attendance": attendance,
            "Study_Hours": study_hours,
            "Assignments_Completed": assignments_completed,
            "Quiz_Score": quiz_score,
            "Midterm_Marks": midterm_marks,
            "Final_Exam_Marks": final_exam_marks,
            "Internet_Access": internet_access,
            "Parental_Education": parental_education,
            "Extra_Curricular": extra_curricular,
            "Sleep_Hours": sleep_hours,
            "Previous_Grade": previous_grade,
            "Performance": performance,
        }
    )

output_df = pd.DataFrame(rows)
output_df.to_csv(DATASET_PATH, index=False)
print(f"Generated {len(output_df)} student records")
