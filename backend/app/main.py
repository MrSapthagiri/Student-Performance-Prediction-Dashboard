from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, excel

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Student Success Platform API",
    description="API for the AI-Powered Student Academic Success Prediction System",
    version="1.0.0",
)

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:8501", # Streamlit default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(excel.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Student Success Platform API"}
