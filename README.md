# Student Performance Prediction Dashboard

A high-impact student performance prediction system built with Flask, Streamlit, SQLite, Plotly, and a Decision Tree classifier, now powered by a 100,000-record student dataset for richer analytics and stronger demonstrations.

## Highlights
- Upload and validate CSV datasets
- Clean and preprocess data automatically
- Train and save a decision tree classifier
- Expose prediction endpoints through Flask
- Visualize student analytics through Streamlit and Plotly
- Store prediction history in SQLite
- Work with a 100,000-record student dataset for high-volume analysis
- Deliver a polished, enterprise-style dashboard experience

## Project Structure
- dataset/: sample and uploaded student datasets
- model/: trained model artifacts and metrics
- training/: model training script
- backend/: Flask REST API
- dashboard/: Streamlit dashboard pages
- database/: SQLAlchemy models and SQLite database
- utils/: preprocessing and chart helpers
- tests/: regression tests for the preprocessing pipeline

## Installation
```bash
cd student-dashboard
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

## Train the Model
```bash
python training/train_model.py
```

## Start the Backend
```bash
python backend/app.py
```

## Start the Dashboard
```bash
streamlit run dashboard/streamlit_app.py
```

## Start Both Together
```bash
python run_app.py
```

## Verification
The project has been verified with:
- model training via training/train_model.py
- Flask health and prediction endpoint checks
- preprocessing regression tests via pytest
