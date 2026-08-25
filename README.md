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
python -m venv venv
```
Then, activate the virtual environment:
- On Windows:
```bash
venv\Scripts\activate
```
- On Mac/Linux:
```bash
source venv/bin/activate
```

**2. Install Dependencies**
With the virtual environment activated, install the required packages:
```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

**3. Start the FastAPI Backend**
Open a terminal, navigate to the `backend` folder, and start the Uvicorn server:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**4. Start the Streamlit Frontend**
Open a *second* terminal, navigate to the `frontend` folder, and start Streamlit:
```bash
cd frontend
streamlit run app.py --server.port 8501
```

## First Steps

Once the application is running:
1. Open your browser to **http://localhost:8501**
2. Navigate to the **Excel Data Import** tab on the left sidebar.
3. Upload your existing student records Excel file. 
4. The system will automatically parse the data, map the columns, and populate the database to fuel the ML predictions!
