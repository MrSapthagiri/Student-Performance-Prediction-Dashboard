from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
import pandas as pd
import io
import math
from app.models.students import Student

router = APIRouter(prefix="/api/v1/excel", tags=["excel"])

def clean_column_name(col_name: str) -> str:
    """Normalizes column names to standard format for mapping."""
    return str(col_name).strip().lower().replace(' ', '_').replace('.', '').replace('-', '_')

# Example dynamic mapping logic based on requested typical columns
COLUMN_MAP = {
    'student_id': ['student_id', 'register_no', 'register_number', 'reg_no', 'roll_number'],
    'name': ['name', 'student_name', 'full_name'],
    'department': ['department', 'dept', 'branch'],
    'year': ['year', 'academic_year_level'],
    'semester': ['semester', 'sem'],
    'attendance_percentage': ['attendance', 'attendance_percentage', 'attendance_%'],
    'internal_marks': ['internal_marks', 'internals', 'internal_score'],
    'assignment_score': ['assignment', 'assignment_marks', 'assignment_score', 'assignments'],
    'previous_gpa': ['previous_gpa', 'cgpa', 'gpa']
}

def map_columns(df_columns):
    mapping = {}
    cleaned_cols = {col: clean_column_name(col) for col in df_columns}
    
    for original_col, cleaned_col in cleaned_cols.items():
        matched = False
        for standard_name, variations in COLUMN_MAP.items():
            if cleaned_col in variations or any(var in cleaned_col for var in variations):
                mapping[original_col] = standard_name
                matched = True
                break
        if not matched:
            mapping[original_col] = cleaned_col # Keep as is if no match
            
    return mapping

@router.post("/upload")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file.")
    
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # 1. Map columns
        mapping = map_columns(df.columns)
        df.rename(columns=mapping, inplace=True)
        
        # 2. Insert into DB
        # We will only insert basic student info for now until we inspect full schema
        records_added = 0
        records_updated = 0
        
        for index, row in df.iterrows():
            if 'student_id' not in row or pd.isna(row['student_id']):
                continue # Skip rows without ID
                
            student_id = str(row['student_id']).strip()
            
            # Extract common fields safely
            name = str(row.get('name', 'Unknown'))
            dept = str(row.get('department', 'Unknown'))
            
            # Helper to handle NaN
            def get_val(key, default=None):
                val = row.get(key)
                if pd.isna(val) or (isinstance(val, float) and math.isnan(val)):
                    return default
                return val
            
            year = get_val('year', 1)
            try:
                year = int(year)
            except:
                year = 1
                
            semester = get_val('semester', 1)
            try:
                semester = int(semester)
            except:
                semester = 1
                
            # Check if student exists
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                student = Student(student_id=student_id)
                db.add(student)
                records_added += 1
            else:
                records_updated += 1
            
            # Update fields
            student.name = name
            student.department = dept
            student.year = year
            student.semester = semester
            student.previous_gpa = get_val('previous_gpa')
            student.attendance_percentage = get_val('attendance_percentage')
            student.internal_marks = get_val('internal_marks')
            student.assignment_score = get_val('assignment_score')
            
        db.commit()
        
        return {
            "message": "Upload successful",
            "columns_mapped": mapping,
            "records_added": records_added,
            "records_updated": records_updated,
            "total_rows_processed": len(df)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
