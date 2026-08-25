@echo off
start cmd /k "cd backend && uvicorn app.main:app --reload --port 8000"
start cmd /k "cd frontend && streamlit run app.py --server.port 8501"
echo Backend started on port 8000
echo Frontend started on port 8501
