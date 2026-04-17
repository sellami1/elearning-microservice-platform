# Analytics Service REST API Contract

## Service Metadata
- Service: Analytics Service
- App version: 1.0.0
- Framework: FastAPI
- Auth: Bearer JWT required on all endpoints except health

## Authentication Contract
- Header: `Authorization: Bearer <jwt>`
- JWT claims consumed by the service:
  - `userId` -> mapped to `user_id`
  - `role`
- Auth error responses:
  - `401 {"detail":"Token expired"}`
  - `401 {"detail":"Invalid token"}`

## Content Type
- Request: `application/json`
- Response: `application/json`

## Endpoints

### GET /health
- Auth: Public
- Response 200:
```json
{
  "status": "healthy",
  "service": "analytics-service"
}
```

### GET /
- Auth: Required
- Response 200:
```json
{
  "message": "Welcome to the Analytics Service",
  "decoded_token": {
    "user_id": "string",
    "role": "learner|instructor"
  }
}
```

### POST /events/view
- Auth: Required
- Description: Record a course view analytics event.
- Request body:
```json
{
  "course_id": "uuid"
}
```
- Response 201:
```json
{
  "id": "uuid",
  "event_type": "course_view",
  "user_id": "string",
  "course_id": "uuid",
  "user_role": "learner|instructor",
  "created_at": "datetime"
}
```

### POST /events/enroll
- Auth: Required
- Description: Record a course enrollment analytics event.
- Request body:
```json
{
  "course_id": "uuid"
}
```
- Response 201:
```json
{
  "id": "uuid",
  "event_type": "course_enroll",
  "user_id": "string",
  "course_id": "uuid",
  "user_role": "learner|instructor",
  "created_at": "datetime"
}
```

### GET /metrics/course/{course_id}
- Auth: Required
- Path params:
  - `course_id` (UUID)
- Response 200:
```json
[
  {
    "course_id": "uuid",
    "metric_date": "YYYY-MM-DD",
    "views_count": 0,
    "enrollments_count": 0
  }
]
```

### GET /metrics/top-courses?limit=10
- Auth: Required
- Query params:
  - `limit` (int, default `10`)
- Response 200:
```json
[
  {
    "course_id": "uuid",
    "total_views": 0,
    "total_enrollments": 0
  }
]
```

## Common Error Contract
- `401 Unauthorized`: invalid, missing, or expired JWT
- `422 Unprocessable Entity`: request validation errors (FastAPI default)
