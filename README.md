`

```



## 🏗️ Architecture

```
Streamlit UI → Service Layer → Repository Layer → PostgreSQL
                    ↕
              ML Pipeline (Scikit-Learn, XGBoost, SHAP)
```

## 📋 Features

- **1000 realistic students** with correlated academic data
- **Full CRUD** for Students, Modules, Academic Records, Attendance
- **Role-based access** (Admin, Faculty, Student)
- **AI Prediction** (Risk, Score, Pass/Fail)
- **SHAP Explainable AI** for every prediction
- **Early Intervention** tracking system
- **Interactive Analytics** with Plotly
- **Data Import** (CSV/Excel)
- **Professional dark-theme UI**

## 🧪 ML Models

| Task | Models Used | Best Selected By |
|------|------------|-----------------|
| Risk Classification | Logistic Regression, Decision Tree, Random Forest, XGBoost | F1 Score |
| Score Prediction | Random Forest Regressor, XGBoost Regressor | R² |
| Pass/Fail | Logistic Regression, Random Forest, XGBoost | F1 Score |

## 📁 Project Structure

```
student-success-ai/
├── app.py                    # Main Streamlit app
├── pages/                    # All UI pages
├── database/                 # ORM, repositories, services
├── ml/                       # ML pipeline
├── data/                     # CSV datasets
├── models/                   # Trained model files
├── scripts/                  # Setup scripts
├── utils/                    # Shared helpers
├── .env                      # Environment config
├── docker-compose.yml        # PostgreSQL setup
└── requirements.txt          # Dependencies
```
# AI-Powered Student Academic Success Prediction System

This is a comprehensive AI/ML Student Academic Success Prediction System featuring authentication, student management, predictive analytics, and personalized recommendations.

## Project Structure

The project is divided into a robust FastAPI backend and an interactive Streamlit frontend.

```
student-success-ai/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI entry point
│   │   ├── database.py    # Database connection setup
│   │   ├── models/        # SQLAlchemy database models
│   │   ├── schemas/       # Pydantic validation schemas
│   │   ├── routes/        # API route definitions
│   │   └── services/      # Business logic (e.g., authentication)
│   └── requirements.txt   # Backend dependencies
│
├── frontend/
│   ├── app.py             # Streamlit entry point
│   ├── pages/             # Streamlit UI pages (Excel Import, etc.)
│   └── requirements.txt   # Frontend dependencies
│
└── run.bat                # Automated startup script for Windows
```

## Prerequisites

Make sure you have Python installed (Python 3.9+ recommended). 

## How to Run the Application

The easiest way to start both the backend and frontend simultaneously on a Windows machine is to use the provided `run.bat` script.

### Method 1: Using the provided `run.bat` script
Simply double-click the `run.bat` file in the root directory, or run it from your command prompt/powershell:
```bash
.\run.bat
```
This will automatically open two command prompts, one for the FastAPI backend and one for the Streamlit frontend. 
- The Streamlit interface will be available at: **http://localhost:8501**
- The FastAPI documentation will be available at: **http://localhost:8000/docs**

### Method 2: Manual Startup

If you prefer to start them manually, follow these steps:

**1. Create and Activate a Virtual Environment (Recommended)**
Open your terminal in the root project directory and run:
```bash
python -m venv .venv
```
Then, activate the virtual environment:
- On Windows:
```bash
.venv\Scripts\activate

```
### 1. Install Dependencies
```bash
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Generate Dataset
```bash
.\.venv\Scripts\python.exe scripts/generate_dataset.py
```

### 3. Seed Database
```bash
.\.venv\Scripts\python.exe scripts/seed_database.py
```

### 4. Train ML Models
```bash
.\.venv\Scripts\python.exe scripts/train_model.py
```

### 5. Run the Application
```bash
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### 6. Login
```
Email: admin@studentai.edu
Password: Admin@123
```

## First Steps

Once the application is running:
1. Open your browser to **http://localhost:8501**
2. Navigate to the **Excel Data Import** tab on the left sidebar.
3. Upload your existing student records Excel file. 
4. The system will automatically parse the data, map the columns, and populate the database to fuel the ML predictions!

## Generating Sample Data

If you need a sample dataset for testing, you can generate one using the provided script. Run the following command from the root directory:
```bash
python generate_high_impact_data.py
```
This will create a `high_impact_students.csv` file with 1000 realistic records, including features like study hours, extracurricular activities, and stress levels to better test the Machine Learning predictions!
