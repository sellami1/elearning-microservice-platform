from fastapi import FastAPI, Depends
from sqlalchemy import text
from .routes import events, metrics
from .database import engine, Base
from .auth import get_current_user
from .models.analytics import SCHEMA_NAME

# --- DATABASE INITIALIZATION ---
# Ensure the custom 'analytics_schema' exists in PostgreSQL before creating tables.
with engine.connect() as connection:
    connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
    connection.commit()

# Create all tables defined in models inside the 'analytics_schema'
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Analytics Service",
    description="Microservice for tracking course views and enrollments",
    version="1.0.0"
)

app.include_router(events.router)
app.include_router(metrics.router)

@app.get("/")
def read_root(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Welcome to the Analytics Service",
        "decoded_token": current_user
    }
