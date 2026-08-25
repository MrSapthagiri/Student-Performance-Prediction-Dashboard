"""
Feature engineering for the Student Success ML pipeline.
Creates derived features from raw student data.
"""

import pandas as pd
import numpy as np


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived features to the student dataframe."""
    df = df.copy()

    # Engagement index: composite of study hours, participation, online learning
    df['engagement_index'] = (
        df.get('study_hours_per_day', 0) * 0.3 +
        df.get('participation_score', 0) / 100 * 0.3 +
        df.get('online_learning_hours', 0) / 8 * 0.2 +
        df.get('assignment_completion_rate', 0) / 100 * 0.2
    )

    # Attendance risk flag
    if 'attendance_percentage' in df.columns:
        df['low_attendance_flag'] = (df['attendance_percentage'] < 75).astype(int)

    # GPA trend (simple proxy — difference between internal performance and previous GPA)
    if 'previous_gpa' in df.columns and 'internal_marks' in df.columns:
        current_proxy = df['internal_marks'] / 40 * 10  # Normalize to 10
        df['gpa_trend'] = current_proxy - df['previous_gpa']

    # Assignment-quiz consistency
    if 'assignment_score' in df.columns and 'quiz_score' in df.columns:
        df['assessment_consistency'] = 1 - abs(
            df['assignment_score'] / 25 - df['quiz_score'] / 20
        )

    # Study efficiency: performance relative to study hours
    if 'study_hours_per_day' in df.columns and 'internal_marks' in df.columns:
        df['study_efficiency'] = df['internal_marks'] / (df['study_hours_per_day'] + 0.5)

    return df


def get_risk_factors(student_data: dict) -> list:
    """Identify the main risk factors for a student."""
    factors = []

    att = student_data.get('attendance_percentage', 100)
    if att < 60:
        factors.append(("Very Low Attendance", f"{att:.1f}%", "critical"))
    elif att < 75:
        factors.append(("Low Attendance", f"{att:.1f}%", "warning"))

    study = student_data.get('study_hours_per_day', 5)
    if study < 1.5:
        factors.append(("Very Low Study Hours", f"{study:.1f} hrs/day", "critical"))
    elif study < 3:
        factors.append(("Low Study Hours", f"{study:.1f} hrs/day", "warning"))

    asgn = student_data.get('assignment_completion_rate', 80)
    if asgn < 40:
        factors.append(("Very Low Assignment Completion", f"{asgn:.1f}%", "critical"))
    elif asgn < 60:
        factors.append(("Low Assignment Completion", f"{asgn:.1f}%", "warning"))

    gpa = student_data.get('previous_gpa', 7)
    if gpa < 4.5:
        factors.append(("Low Previous GPA", f"{gpa:.2f}/10", "critical"))
    elif gpa < 6:
        factors.append(("Below Average GPA", f"{gpa:.2f}/10", "warning"))

    part = student_data.get('participation_score', 60)
    if part < 30:
        factors.append(("Very Low Participation", f"{part:.1f}%", "critical"))
    elif part < 50:
        factors.append(("Low Participation", f"{part:.1f}%", "warning"))

    internal = student_data.get('internal_marks', 25)
    if internal < 15:
        factors.append(("Low Internal Marks", f"{internal:.1f}/40", "critical"))
    elif internal < 22:
        factors.append(("Below Average Internal Marks", f"{internal:.1f}/40", "warning"))

    midterm = student_data.get('midterm_score', 30)
    if midterm < 18:
        factors.append(("Low Midterm Score", f"{midterm:.1f}/50", "critical"))
    elif midterm < 25:
        factors.append(("Below Average Midterm Score", f"{midterm:.1f}/50", "warning"))

    return factors


def generate_recommendations(student_data: dict, risk_factors: list) -> list:
    """Generate personalized recommendations based on student weaknesses."""
    recommendations = []

    for factor_name, value, severity in risk_factors:
        if "Attendance" in factor_name:
            recommendations.append({
                "area": "Attendance",
                "priority": "High" if severity == "critical" else "Medium",
                "recommendation": f"Current attendance is {value}. Attend all remaining classes to improve. Consider meeting with your academic advisor to discuss attendance barriers.",
                "icon": "📅"
            })
        elif "Study Hours" in factor_name:
            recommendations.append({
                "area": "Study Habits",
                "priority": "High" if severity == "critical" else "Medium",
                "recommendation": f"Current study time is {value}. Aim for at least 4-5 hours of focused study daily. Use the Pomodoro technique and create a structured study schedule.",
                "icon": "📖"
            })
        elif "Assignment" in factor_name:
            recommendations.append({
                "area": "Assignments",
                "priority": "High" if severity == "critical" else "Medium",
                "recommendation": f"Assignment completion rate is {value}. Complete all pending assignments immediately. Set reminders for due dates and break large tasks into smaller ones.",
                "icon": "✍️"
            })
        elif "GPA" in factor_name:
            recommendations.append({
                "area": "Academic Foundation",
                "priority": "Medium",
                "recommendation": f"Previous GPA is {value}. Review foundational concepts from previous semesters. Consider joining peer study groups or seeking tutoring support.",
                "icon": "🎓"
            })
        elif "Participation" in factor_name:
            recommendations.append({
                "area": "Class Participation",
                "priority": "Medium" if severity == "critical" else "Low",
                "recommendation": f"Participation score is {value}. Actively engage in class discussions, ask questions, and volunteer for presentations.",
                "icon": "🗣️"
            })
        elif "Internal Marks" in factor_name:
            recommendations.append({
                "area": "Internal Assessment",
                "priority": "High" if severity == "critical" else "Medium",
                "recommendation": f"Internal marks are {value}. Focus on improving test preparation strategies. Practice with past question papers and review weak topics.",
                "icon": "📝"
            })
        elif "Midterm" in factor_name:
            recommendations.append({
                "area": "Exam Preparation",
                "priority": "High" if severity == "critical" else "Medium",
                "recommendation": f"Midterm score is {value}. Intensify exam preparation — create summary notes, practice mock exams, and review incorrect answers.",
                "icon": "🧪"
            })

    # General recommendations for high-risk students
    if len(risk_factors) >= 3:
        recommendations.append({
            "area": "Mentorship",
            "priority": "High",
            "recommendation": "Multiple academic risk factors detected. Faculty/mentor intervention is strongly recommended. Schedule regular check-ins with your assigned mentor.",
            "icon": "🚨"
        })

    if not recommendations:
        recommendations.append({
            "area": "Maintain Performance",
            "priority": "Low",
            "recommendation": "Keep up the good work! Continue your current study habits and maintain regular attendance.",
            "icon": "⭐"
        })

    return recommendations
