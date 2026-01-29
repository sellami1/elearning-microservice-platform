import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Build path to .env in root: Projet d'intégration/.env
# Loading environment variables from the project root directory
# Project structure: Projet d'intégration / backend / analytics-service / app / database.py
# .parent.parent.parent.parent takes us back to "Projet d'intégration"
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Retrieve the PostgreSQL connection string from root .env
POSTGRES_URL = os.getenv("POSTGRES_URL")

if not POSTGRES_URL:
    raise ValueError("POSTGRES_URL not found in environment. Please check the root .env file.")

# Initialize SQLAlchemy engine and session factory
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
