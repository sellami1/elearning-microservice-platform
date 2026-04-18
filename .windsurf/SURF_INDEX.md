# Backend Services Surf Index

3 microservices: user-service (Node/Express), course-service (Python/FastAPI), analytics-service (Python/FastAPI).

## Service Overview

| Service | Stack | Port | DB | Key Role |
|---------|-------|------|-----|----------|
| **user-service** | Node + Express + MongoDB | 5000 | MongoDB | Auth, users, JWT |
| **course-service** | Python + FastAPI + PostgreSQL | 5001 | Postgres + MinIO | Courses, lessons, enrollments |
| **analytics-service** | Python + FastAPI + PostgreSQL | 5002 | Postgres | Events, metrics tracking |

All expose `/api/v1/*` + `/health` endpoints.

---

## User Service (@backend/user-service)

```
src/
├── server.js              # Entry: Express app, Swagger, middleware chain
├── config/
│   └── db.js              # MongoDB connection
├── controllers/
│   └── userController.js  # Route handlers (auth, profile, admin)
├── middleware/
│   ├── authMiddleware.js      # JWT verify + role guard
│   ├── errorMiddleware.js     # Global error handler
│   └── validatorMiddleware.js # express-validator wrapper
├── models/
│   └── userModel.js       # Mongoose schema (User, Profile, Address)
├── routes/
│   ├── index.js           # Route mount point
│   └── userRoute.js       # All /api/v1/users/* routes
└── utils/
    ├── apiError.js        # Custom error class
    ├── createJWT.js       # Token generation
    ├── logger.js          # Winston logger
    ├── rateLimiter.js     # express-rate-limit
    └── validators/userValidator.js  # express-validator rules
```

### Key Patterns

- **Routes**: All in `userRoute.js` grouped by feature (auth, profile, admin)
- **Auth**: JWT Bearer via `authMiddleware.verifyToken`
- **Validation**: `express-validator` chains in `validators/userValidator.js`, validated via `validatorMiddleware`
- **Errors**: `ApiError` → caught by `errorMiddleware` → consistent JSON response
- **Security**: `mongo-sanitize`, `xss-sanitizer`, `helmet` (compression)
- **Logging**: Winston with dev/prod split
- **API Docs**: Swagger UI at `/api-docs` (auto-gen from JSDoc in routes)

### Conventions

- [ ] `express-async-handler` wraps all async controllers
- [ ] `next(new ApiError(msg, status))` for expected errors
- [ ] `logger.info/error` for operational logs (never console.log)
- [ ] Routes use `/api/v1/users` prefix mounted in `index.js`
- [ ] Mongoose subdocuments: `profile`, `address` nested in User schema

---

## Course Service (@backend/course-service)

```
app/
├── main.py                # FastAPI entry: lifespan, CORS, router mount
├── database.py            # SQLAlchemy engine + create_tables()
├── core/
│   ├── config.py          # Pydantic Settings (env vars)
│   └── logging_config.py  # Structured logging setup
├── api/
│   ├── dependencies.py    # FastAPI deps (DB session)
│   └── v1/
│       ├── courses.py     # /api/v1/courses routes
│       ├── lessons.py     # /api/v1/lessons routes
│       └── enrollments.py # /api/v1/enrollments routes
├── crud/
│   ├── course_crud.py
│   ├── lesson_crud.py
│   └── enrollment_crud.py
├── models/
│   ├── course.py          # SQLAlchemy table definitions
│   ├── lesson.py
│   └── enrollment.py
└── schemas/
    ├── course_schema.py   # Pydantic request/response models
    ├── lesson_schema.py
    └── enrollment_schema.py
```

### Key Patterns

- **App**: FastAPI with `@asynccontextmanager` lifespan (startup table create)
- **Routes**: Separate routers per domain, prefix `/api/v1/{domain}` in `main.py`
- **CRUD**: Business logic isolated in `crud/` layer, not in routes
- **DB**: SQLAlchemy ORM + PostgreSQL, SQLAlchemy 2.0 style
- **Deps**: `get_database()` yields SessionLocal for dependency injection
- **Schemas**: Pydantic v2 models separate request (create) vs response (read)

### Conventions

- [ ] Routes thin: validation → call CRUD → return schema
- [ ] CRUD functions accept `db: Session` param explicitly
- [ ] Schemas named `{Model}Create`, `{Model}Response`, `{Model}Update`
- [ ] Use `response_model=` in router decorators for type safety
- [ ] Async SQLAlchemy: `await db.execute()` + `await db.commit()`

---

## Analytics Service (@backend/analytics-service)

```
app/
├── main.py                # FastAPI entry: CORS, router mount
├── database.py            # SQLAlchemy init + schema creation
├── auth.py                # JWT verify dependency (shared logic)
├── cors.py                # GranularCORSMiddleware (custom)
├── core/
│   ├── config.py          # Pydantic settings
│   └── logging_config.py  # Logging setup
├── models/
│   └── analytics.py       # SQLAlchemy Event, Metric models + SCHEMA_NAME
├── routes/
│   ├── events.py          # POST /events (track views)
│   └── metrics.py         # GET /metrics/* (aggregations)
└── schemas/
    ├── event_schema.py    # Pydantic event payloads
    └── metric_schema.py   # Pydantic metric responses
```

### Key Patterns

- **Auth**: `get_current_user` dependency decodes JWT, used in protected routes
- **CORS**: Custom `GranularCORSMiddleware` for fine-grained origin control
- **Schema**: Postgres schema `analytics` auto-created at boot
- **Events**: Fire-and-forget POST for tracking (course views, etc)
- **Metrics**: Computed aggregations over event data

### Conventions

- [ ] Use `auth.get_current_user` for protected routes
- [ ] Events async-safe: no heavy processing in request path
- [ ] Schema isolation: all tables in `analytics` schema
- [ ] Health check at `/health` (no auth required)

---

## Cross-Service Conventions

| Concern | Pattern |
|---------|---------|
| **Health** | All services expose `GET /health` → `{status: healthy}` |
| **API Prefix** | `/api/v1/{resource}` |
| **Auth** | JWT Bearer (`Authorization: Bearer <token>`) |
| **CORS** | Configured per-service origins via env vars |
| **Logging** | Structured JSON in prod, readable in dev |
| **Errors** | Consistent shape: `{statusCode, message, fieldErrors?}` |
| **DB** | user=Mongo, course/analytics=Postgres |

## Docker/Dev

```yaml
# docker-compose.yml at repo root spins up:
- user-service:5000
- course-service:5001
- analytics-service:5002
- postgres:5432
- mongo:27017
- minio:9000 (course files)
```

## Quick Snippets

### New User Service Route

```js
// src/routes/userRoute.js
router.post("/action", validatorMiddleware, asyncHandler(userController.action));

// src/controllers/userController.js
exports.action = async (req, res, next) => {
  try {
    // ... logic
    res.status(200).json({ status: "success", data: result });
  } catch (err) {
    next(new ApiError(err.message, 400));
  }
};
```

### New Course Service Endpoint

```python
# app/api/v1/new_feature.py
from fastapi import APIRouter, Depends
from app.api.dependencies import get_database
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/", response_model=FeatureResponse)
def create_feature(
    payload: FeatureCreate,
    db: Session = Depends(get_database)
):
    return crud.create(db, payload)
```

### New Analytics Event

```python
# app/routes/events.py
@router.post("/events")
def track_event(
    payload: EventSchema,
    db: Session = Depends(get_database),
    user: dict = Depends(get_current_user)  # optional
):
    # persist event
    return {"status": "recorded"}
```
