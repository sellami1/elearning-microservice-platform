---
# User Service — Overview
**Port:** 8000
**Base path:** `/`
**Responsibility:** Records course view/enrollment events and exposes aggregated course metrics.

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.11 (Docker base image) |
| Framework | FastAPI |
| Database | PostgreSQL (via SQLAlchemy) |
| Auth | JWT bearer token (`python-jose`) |

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| APP_NAME | No | Application name setting (default: `Analytics Service`). |
| LOG_LEVEL | No | Logging level (default: `INFO`). |
| POSTGRES_URL | Yes | SQLAlchemy database connection URL. |
| JWT_SECRET_KEY | Yes | Secret used to verify JWT signatures. |
| JWT_ALGORITHM | No | JWT algorithm (default: `HS256`). |
| REDIS_HOST | No | Redis host for metrics caching (default: `localhost`). |
| REDIS_PORT | No | Redis port (default: `6379`). |
| REDIS_TTL_SECONDS | No | Cache TTL in seconds (default: `60`). |

## Entry Point
- Initializes logging, ensures schema exists, and creates SQLAlchemy tables.
- Registers granular CORS middleware and includes `/events` and `/metrics` routers.
- Exposes `/health` (public) and `/` (JWT-protected) endpoints.
---