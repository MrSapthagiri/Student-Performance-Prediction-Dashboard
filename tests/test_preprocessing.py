import unittest
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.preprocessing import validate_and_clean_dataset, build_preprocessor


class PreprocessingTests(unittest.TestCase):
    def test_validate_and_clean_dataset(self):
        df = pd.DataFrame(
            {
                "Student_ID": [1, 2, 2],
                "Gender": ["Male", "Female", "Female"],
                "Age": [18, 19, None],
                "Class": [10, 11, 10],
                "Attendance": [92, 87, 91],
                "Study_Hours": [5, 7, None],
                "Assignments_Completed": [8, 7, 8],
                "Quiz_Score": [88, 76, 90],
                "Midterm_Marks": [78, 82, 80],
                "Final_Exam_Marks": [85, 79, 88],
                "Internet_Access": ["Yes", "No", "Yes"],
                "Parental_Education": ["Bachelor", "High School", "Bachelor"],
                "Extra_Curricular": ["Yes", "No", "Yes"],
                "Sleep_Hours": [7, 6, 8],
                "Previous_Grade": ["A", "B", "A"],
                "Performance": ["Good", "Average", "Excellent"],
            }
        )

        cleaned = validate_and_clean_dataset(df)
        self.assertFalse(cleaned.empty)
        self.assertEqual(cleaned["Age"].isna().sum(), 0)
        self.assertEqual(cleaned["Study_Hours"].isna().sum(), 0)
        self.assertEqual(cleaned["Performance"].isin(["Excellent", "Good", "Average", "Poor"]).all(), True)

    def test_build_preprocessor(self):
        df = pd.DataFrame(
            {
                "Gender": ["Male", "Female"],
                "Attendance": [90, 80],
                "Study_Hours": [4, 6],
                "Assignments_Completed": [7, 8],
                "Quiz_Score": [85, 78],
                "Midterm_Marks": [88, 79],
                "Final_Exam_Marks": [89, 81],
                "Internet_Access": ["Yes", "No"],
                "Sleep_Hours": [8, 6],
                "Previous_Grade": ["A", "B"],
                "Performance": ["Good", "Average"],
            }
        )
        cleaned = validate_and_clean_dataset(df)
        preprocessor = build_preprocessor(cleaned)
        self.assertIn("Gender", preprocessor["feature_columns"])
        self.assertEqual(preprocessor["feature_columns"][0], "Gender")


if __name__ == "__main__":
    unittest.main()
