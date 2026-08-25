`
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
