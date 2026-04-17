# Deployment Guide

This repository ships three services and the supporting data stores needed to run them together with Docker Compose.

## Services

- user-service: Node.js API on [http://localhost:8002](http://localhost:8002)
- course-service: FastAPI API on [http://localhost:8001](http://localhost:8001)
- analytics-service: FastAPI API on [http://localhost:8003](http://localhost:8003)
- MongoDB: [localhost:27017](http://localhost:27017)
- MailHog SMTP: `localhost:1025`, Web UI: [http://localhost:8025](http://localhost:8025)
- Course PostgreSQL: `localhost:5433`
- Analytics PostgreSQL: `localhost:5434`
- MinIO API: [http://localhost:9000](http://localhost:9000), console: [http://localhost:9001](http://localhost:9001)
- Redis: `localhost:6379`

## Prerequisites

- Docker Engine with Docker Compose v2
- Enough free ports for the services above

## Run The Stack

1. Build and start everything from the repository root.

```bash
docker compose up -d --build
```

2. Watch the logs if you want to confirm startup order and database initialization.

```bash
docker compose logs -f user-service course-service analytics-service
```

3. Verify container health status.

```bash
docker compose ps
```

4. Verify the API endpoints.

```bash
# user-service has no public /health endpoint; / returns 400 by design
curl -i http://localhost:8002/
curl http://localhost:8001/health
curl http://localhost:8003/health
```

## What The Compose File Starts

- MongoDB for the user service
- MailHog for SMTP testing
- One PostgreSQL database for course-service
- One PostgreSQL database for analytics-service
- MinIO for course media storage
- Redis for analytics caching
- All three application services

## Configuration Notes

- The user service uses `MONGODB_URI=mongodb://mongodb:27017/user_service_db` inside Docker.
- The course service uses `POSTGRES_URL=postgresql://course_user:course_password@course-postgres:5432/course_db`.
- The analytics service uses `POSTGRES_URL=postgresql://analytics_user:analytics_password@analytics-postgres:5432/analytics_db`.
- If you need different secrets or ports, edit `docker-compose.yml` before starting the stack.

## Stop And Clean Up

```bash
docker compose down
```

To remove persistent data as well:

```bash
docker compose down -v
```

## Notes

- MinIO will create its data volume automatically, but the course service still needs a reachable MinIO container at startup.
- The course database init script is mounted from `backend/course-service/app/init.sql`.
- The course-service standalone `.env.example` now uses `POSTGRES_URL`, which matches the application code.