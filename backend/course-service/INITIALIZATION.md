# Database & Storage Initialization Guide

## Overview

The e-learning platform uses:
- **PostgreSQL** for relational data (courses, modules, lessons, enrollments)
- **MinIO** for object storage (videos, attachments, course materials)

Both databases are automatically initialized on application startup.

## Initialization Methods

### 1. Docker Compose (Recommended for Development)

```bash
# Build and start all services
docker-compose up -d

# The entrypoint script will:
# - Wait for PostgreSQL to be ready
# - Wait for MinIO to be ready
# - Run init_db.py to create tables and buckets
# - Start the FastAPI server
```

**Logs:**
```bash
docker-compose logs -f api
```

### 2. Manual Initialization (Local Development)

Before starting the API, ensure PostgreSQL and MinIO are running:

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize databases
python init_db.py

# Start the API
uvicorn app.main:app --reload
```

### 3. Automatic Initialization on Startup

When the FastAPI application starts, it automatically:

1. **Checks PostgreSQL connection**
2. **Creates all tables** using SQLAlchemy models
3. **Checks MinIO connection**
4. **Creates default bucket** (elearning)

This happens in the `@app.on_event("startup")` handler in `app/main.py`

## Database Schema

The application creates the following PostgreSQL tables:

### Courses Table
```sql
CREATE TABLE courses (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  instructor_id INTEGER NOT NULL,
  thumbnail_url VARCHAR(255),
  is_published BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Modules Table
```sql
CREATE TABLE modules (
  id SERIAL PRIMARY KEY,
  course_id INTEGER NOT NULL REFERENCES courses(id),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  order INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Lessons Table
```sql
CREATE TABLE lessons (
  id SERIAL PRIMARY KEY,
  module_id INTEGER NOT NULL REFERENCES modules(id),
  title VARCHAR(255) NOT NULL,
  content TEXT,
  video_url VARCHAR(255),
  attachment_url VARCHAR(255),
  order INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Enrollments Table
```sql
CREATE TABLE enrollments (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL REFERENCES courses(id),
  enrolled_at TIMESTAMP DEFAULT NOW(),
  progress INTEGER DEFAULT 0
);
```

## MinIO Storage Structure

The application creates and uses the following MinIO bucket:

**Bucket Name:** `elearning`

### Recommended Storage Organization

```
elearning/
├── courses/
│   ├── {course_id}/
│   │   ├── thumbnails/
│   │   ├── materials/
│   │   └── videos/
├── lessons/
│   ├── {lesson_id}/
│   │   ├── attachments/
│   │   └── videos/
└── uploads/
    ├── temp/
    └── archive/
```

## Health Check Endpoint

Check the status of both databases:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "storage": "connected"
}
```

## Troubleshooting

### PostgreSQL Connection Issues

**Error:** `psycopg2.OperationalError: could not connect to server`

**Solutions:**
- Ensure PostgreSQL is running: `docker-compose ps postgres`
- Verify DATABASE_URL in .env file
- Check PostgreSQL is accepting connections: `pg_isready -h localhost`

### MinIO Connection Issues

**Error:** `minio.error.S3Error: Unable to connect`

**Solutions:**
- Ensure MinIO is running: `docker-compose ps minio`
- Verify MINIO_URL in .env file
- Check MinIO health: `curl http://localhost:9000/minio/health/live`

### Database Already Exists

If you encounter duplicate key errors, tables already exist:

```bash
# Option 1: Use existing tables (safest)
# Just restart the API

# Option 2: Reset everything (CAUTION - DATA LOSS)
docker-compose down -v
docker-compose up -d
```

## Migration Management

Using Alembic for database schema migrations:

### Create a New Migration

```bash
# Auto-generate migration based on model changes
alembic revision --autogenerate -m "Add new field to courses"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade 001
```

### Revert Migrations

```bash
# Downgrade one step
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade 001
```

### View Migration History

```bash
alembic current
alembic history
```

## Environment Variables

Required environment variables for initialization:

```env
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/elearning_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# MinIO
MINIO_URL=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=elearning
MINIO_SECURE=False

# Debug
DEBUG=True
```

## Files Related to Initialization

```
elearning-platform/
├── init_db.py                          # Standalone initialization script
├── entrypoint.sh                       # Docker entrypoint script
├── app/
│   ├── db/
│   │   ├── session.py                 # Database session setup
│   │   ├── init/
│   │   │   ├── __init__.py
│   │   │   ├── database.py            # PostgreSQL initialization
│   │   │   └── minio.py               # MinIO initialization
│   │   └── ...
│   ├── main.py                        # FastAPI app with startup events
│   └── ...
├── migrations/
│   ├── env.py                         # Alembic configuration
│   ├── versions/
│   │   └── 001_initial_migration.py   # Initial schema
│   └── script.py.mako                 # Migration template
└── alembic.ini                        # Alembic settings
```

## Best Practices

1. **Development:** Use Docker Compose for consistency
2. **Testing:** Initialize fresh database for each test run
3. **Production:** Run migrations separately before API deployment
4. **Backup:** Always backup PostgreSQL data before major migrations
5. **Monitoring:** Use health check endpoint to monitor database status
