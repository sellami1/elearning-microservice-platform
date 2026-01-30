from fastapi import FastAPI, Depends
from sqlalchemy import text
from .routes import events, metrics
from .database import engine, Base
from .auth import get_current_user
from .models.analytics import SCHEMA_NAME
from fastapi.middleware.cors import CORSMiddleware
from .cors import GranularCORSMiddleware

# --- DATABASE INITIALIZATION ---
with engine.connect() as connection:
    connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
    connection.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Analytics Service",
    description="Microservice for tracking course views and enrollments",
    version="1.0.0"
)

# --- CORS MIDDLEWARES ---
app.add_middleware(GranularCORSMiddleware)

app.include_router(events.router)
app.include_router(metrics.router)

@app.get("/health")
def health_check():
    """Service health probe for Docker/K8s"""
    return {"status": "healthy", "service": "analytics-service"}

@app.get("/")
def read_root(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Welcome to the Analytics Service",
        "decoded_token": current_user
    }
