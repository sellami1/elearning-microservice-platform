#!/bin/bash
# Docker entrypoint script for initializing databases and starting the API

set -e

echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h postgres -U user -d elearning_db 2>/dev/null; do
  sleep 1
done
echo "PostgreSQL is ready!"

echo "Waiting for MinIO to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
  if curl -f http://minio:9000/minio/health/live 2>/dev/null; then
    echo "MinIO is ready!"
    break
  fi
  attempt=$((attempt + 1))
  sleep 1
done

echo "Initializing databases and storage..."
python init_db.py

echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
