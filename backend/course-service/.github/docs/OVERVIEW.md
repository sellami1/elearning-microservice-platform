---
# User Service — Overview
**Port:** 8000
**Base path:** `/api/v1`
**Responsibility:** Manages courses, lessons, and enrollments with role-based access and media-backed content uploads.

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.11 |
| Framework | FastAPI |
| Database | PostgreSQL via SQLAlchemy |
| Auth | JWT Bearer token validation (`python-jose`) |

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| APP_NAME | No | API/service name (default: `Course Service`). |
| APP_VERSION | No | API version string (default: `1.0.0`). |
| DEBUG | No | Enables debug mode and SQLAlchemy echo when true. |
| POSTGRES_URL | Yes | Database connection URL used by SQLAlchemy engine. |
| JWT_SECRET_KEY | Yes | JWT signing secret used for token verification. |
| JWT_ALGORITHM | No | JWT algorithm (default: `HS256`). |
| ACCESS_TOKEN_EXPIRE_MINUTES | No | Token expiry minutes setting in config (default: `30`) <!-- confirm --> |
| MINIO_ENDPOINT | Yes | MinIO server endpoint for file storage. |
| MINIO_ACCESS_KEY | Yes | MinIO access key. |
| MINIO_SECRET_KEY | Yes | MinIO secret key. |
| MINIO_BUCKET_NAME | No | MinIO bucket name (default: `courses-media`). |
| MINIO_SECURE | No | Enables HTTPS for MinIO when true (default: `False`). |
| ANALYTICS_URL | No | Analytics service base URL used to record view and enrollment events. |
| ANALYTICS_REQUEST_TIMEOUT_SECONDS | No | Timeout in seconds for analytics event calls (default: `2.0`). |

## Entry Point
- Initializes FastAPI app with lifespan startup/shutdown that creates DB tables and disposes engine on shutdown.
- Adds CORS middleware and mounts routers for `/api/v1/courses`, `/api/v1/lessons`, and `/api/v1/enrollments`.
- Defines `/health` and `/` routes and a global exception handler returning `500` with `{"detail":"Internal server error"}`.
---