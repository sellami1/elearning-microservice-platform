# Course Service REST API Contract

## Service Metadata
- Service: Course Service
- Framework: FastAPI
- API docs: `/api/v1/docs`
- OpenAPI JSON: `/api/v1/openapi.json`

## Authentication Contract
- Header: `Authorization: Bearer <jwt>`
- JWT claims consumed by the service:
  - `userId` -> mapped to `user_id`
  - `role`
- Roles used by route guards:
  - `instructor`
  - `learner`
- Auth error responses:
  - `401 {"detail":"Token expired"}`
  - `401 {"detail":"Invalid token"}`
  - `403 {"detail":"Role <role> not authorized. Requires one of: [...]"}`

## Content Types
- JSON endpoints: `application/json`
- File upload endpoints: `multipart/form-data`

## Interactive API Summary

Use this section to quickly scan endpoints by area, method, auth, and role, then jump to full details below.

### Quick Jump
- [Base Utility Endpoints](#base-utility-endpoints)
- [Courses API](#courses-api)
- [Lessons API](#lessons-api)
- [Enrollments API](#enrollments-api)
- [Common Error Contract](#common-error-contract)

### Endpoint Matrix

| Area | Method | Path | Auth | Role | Request Type | Success |
|---|---|---|---|---|---|---|
| Utility | GET | `/health` | Public | Any | JSON | `200` |
| Utility | GET | `/` | Public | Any | JSON | `200` |
| Courses | GET | `/api/v1/courses/` | Optional | Any | Query params | `200` |
| Courses | GET | `/api/v1/courses/{course_id}` | Optional | Any | Path param | `200` |
| Courses | POST | `/api/v1/courses/` | Required | `instructor` | `multipart/form-data` | `201` |
| Courses | PUT | `/api/v1/courses/{course_id}` | Required | `instructor` | `multipart/form-data` | `200` |
| Courses | DELETE | `/api/v1/courses/{course_id}` | Required | `instructor` | Path param | `204` |
| Courses | GET | `/api/v1/courses/instructor/mine` | Required | `instructor` | Query params | `200` |
| Lessons | GET | `/api/v1/lessons/course/{course_id}` | Optional | Any | Path + query params | `200` |
| Lessons | POST | `/api/v1/lessons/` | Required | `instructor` | `multipart/form-data` | `201` |
| Lessons | GET | `/api/v1/lessons/{lesson_id}` | Optional | Any | Path param | `200` |
| Lessons | PUT | `/api/v1/lessons/{lesson_id}` | Required | `instructor` | `multipart/form-data` | `200` |
| Lessons | DELETE | `/api/v1/lessons/{lesson_id}` | Required | `instructor` | Path param | `204` |
| Enrollments | POST | `/api/v1/enrollments/` | Required | `learner` | JSON body | `201` |
| Enrollments | GET | `/api/v1/enrollments/me` | Required | `learner` | Query params | `200` |
| Enrollments | GET | `/api/v1/enrollments/course/{course_id}/enrollments` | Required | `instructor` | Path + query params | `200` |
| Enrollments | GET | `/api/v1/enrollments/instructor` | Required | `instructor` | Query params | `200` |

### Role Filters

<details>
<summary>Instructor endpoints</summary>

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/courses/` | Create course |
| PUT | `/api/v1/courses/{course_id}` | Update owned course |
| DELETE | `/api/v1/courses/{course_id}` | Delete owned course |
| GET | `/api/v1/courses/instructor/mine` | List own courses |
| POST | `/api/v1/lessons/` | Create lesson in owned course |
| PUT | `/api/v1/lessons/{lesson_id}` | Update lesson in owned course |
| DELETE | `/api/v1/lessons/{lesson_id}` | Delete lesson in owned course |
| GET | `/api/v1/enrollments/course/{course_id}/enrollments` | View enrollments for one course |
| GET | `/api/v1/enrollments/instructor` | View enrollments across instructor courses |

</details>

<details>
<summary>Learner endpoints</summary>

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/enrollments/` | Enroll in a published course |
| GET | `/api/v1/enrollments/me` | View own enrollments and stats |

</details>

<details>
<summary>Public or optional-auth endpoints</summary>

| Method | Path | Visibility |
|---|---|---|
| GET | `/health` | Public |
| GET | `/` | Public |
| GET | `/api/v1/courses/` | Public list, with optional Bearer behavior |
| GET | `/api/v1/courses/{course_id}` | Public/optional-auth |
| GET | `/api/v1/lessons/course/{course_id}` | Public/optional-auth (visibility rules apply) |
| GET | `/api/v1/lessons/{lesson_id}` | Public/optional-auth (visibility rules apply) |

</details>

## Base Utility Endpoints

### GET /health
- Auth: Public
- Response 200:
```json
{
  "status": "healthy",
  "service": "Course Service",
  "version": "string"
}
```

### GET /
- Auth: Public
- Response 200:
```json
{
  "message": "Welcome to Course Service",
  "version": "string",
  "docs": "/api/v1/docs",
  "health": "/health"
}
```

## Courses API
Base path: `/api/v1/courses`

### GET /api/v1/courses/
- Auth: Optional (`Bearer` can change visibility rules)
- Query params:
  - `skip` int >= 0 (default `0`)
  - `limit` int 1..100 (default `100`)
  - `published` bool (optional)
  - `category` string (optional)
  - `level` `beginner|intermediate|advanced` (optional)
  - `is_featured` bool (optional)
  - `search` string (optional)
  - `instructor_id` string (optional)
- Response 200:
```json
{
  "items": [
    {
      "id": "uuid",
      "instructor_id": "string",
      "title": "string",
      "description": "string|null",
      "short_description": "string|null",
      "price": 0,
      "category": "string|null",
      "subcategory": "string|null",
      "level": "beginner",
      "duration_hours": 0,
      "thumbnail_url": "string|null",
      "published": false,
      "is_featured": false,
      "rating": 0,
      "total_ratings": 0,
      "total_enrollments": 0,
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": 0,
  "page": 1,
  "size": 100,
  "pages": 0
}
```

### GET /api/v1/courses/{course_id}
- Auth: Optional
- Path params:
  - `course_id` UUID
- Response 200: `CourseResponse` shape (same as item above)
- Errors:
  - `404 {"detail":"Course not found"}`

### POST /api/v1/courses/
- Auth: Required role `instructor`
- Content-Type: `multipart/form-data`
- Form fields:
  - `title` string (required)
  - `description` string (optional)
  - `short_description` string max 500 (optional)
  - `price` float >= 0 (optional, default `0.0`)
  - `category` string (optional)
  - `subcategory` string (optional)
  - `level` `beginner|intermediate|advanced` (optional, default `beginner`)
  - `duration_hours` int >= 0 (optional)
  - `published` bool (optional, default `false`)
  - `is_featured` bool (optional, default `false`)
  - `thumbnail_file` file (optional)
- Response 201: `CourseResponse`
- Errors:
  - `422` validation/value errors
  - `500 {"detail":"Course creation failed: ..."}`

### PUT /api/v1/courses/{course_id}
- Auth: Required role `instructor`
- Content-Type: `multipart/form-data`
- Form fields: same set as create, all optional
- Additional response field: `thumbnail_updated` boolean
- Response 200:
```json
{
  "id": "uuid",
  "instructor_id": "string",
  "title": "string",
  "description": "string|null",
  "short_description": "string|null",
  "price": 0,
  "category": "string|null",
  "subcategory": "string|null",
  "level": "beginner",
  "duration_hours": 0,
  "thumbnail_url": "string|null",
  "published": false,
  "is_featured": false,
  "rating": 0,
  "total_ratings": 0,
  "total_enrollments": 0,
  "created_at": "datetime",
  "updated_at": "datetime",
  "thumbnail_updated": true
}
```
- Errors:
  - `403 {"detail":"Not authorized to update this course"}`
  - `404 {"detail":"Course not found"}`
  - `422` validation/value errors

### DELETE /api/v1/courses/{course_id}
- Auth: Required role `instructor`
- Response 204: no body
- Errors:
  - `403 {"detail":"Not authorized to delete this course"}`
  - `404 {"detail":"Course not found"}`

### GET /api/v1/courses/instructor/mine
- Auth: Required role `instructor`
- Query params:
  - `published` bool (optional)
- Response 200:
```json
[
  {
    "id": "uuid",
    "instructor_id": "string",
    "title": "string",
    "description": "string|null",
    "short_description": "string|null",
    "price": 0,
    "category": "string|null",
    "subcategory": "string|null",
    "level": "beginner",
    "duration_hours": 0,
    "thumbnail_url": "string|null",
    "published": false,
    "is_featured": false,
    "rating": 0,
    "total_ratings": 0,
    "total_enrollments": 0,
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

## Lessons API
Base path: `/api/v1/lessons`

### GET /api/v1/lessons/course/{course_id}
- Auth: Optional
- Query params: `skip`, `limit`
- Response 200:
```json
{
  "items": [
    {
      "id": "uuid",
      "course_id": "uuid",
      "title": "string",
      "description": "string|null",
      "content_type": "video|text|pdf|quiz|audio|image",
      "duration_minutes": 0,
      "order_index": 0,
      "is_preview": false,
      "is_published": true,
      "content_url": "string|null",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": 0,
  "page": 1,
  "size": 100,
  "pages": 0
}
```
- Errors:
  - `404` course not found / not visible

### POST /api/v1/lessons/
- Auth: Required role `instructor`
- Content-Type: `multipart/form-data`
- Required form fields:
  - `title`, `content_type`, `course_id`
- Optional form fields:
  - `description`, `duration_minutes`, `order_index`, `is_preview`, `is_published`, `content_url`, `content_file`
- Response 201: `LessonResponse`
- Errors:
  - `400` missing content file/url for binary content types
  - `403` not owner/admin
  - `404` course not found
  - `422` validation/value errors

### GET /api/v1/lessons/{lesson_id}
- Auth: Optional
- Response 200: `LessonResponse`
- Errors:
  - `404` lesson not found / not visible

### PUT /api/v1/lessons/{lesson_id}
- Auth: Required role `instructor`
- Content-Type: `multipart/form-data`
- Form fields: all optional (`title`, `description`, `content_type`, `content_url`, `duration_minutes`, `order_index`, `is_preview`, `is_published`, `content_file`)
- Response 200: `LessonResponse`
- Errors:
  - `403` not owner/admin
  - `404` lesson not found

### DELETE /api/v1/lessons/{lesson_id}
- Auth: Required role `instructor`
- Response 204: no body
- Errors:
  - `403` not owner/admin
  - `404` lesson not found

## Enrollments API
Base path: `/api/v1/enrollments`

### POST /api/v1/enrollments/
- Auth: Required role `learner`
- Request body:
```json
{
  "course_id": "uuid"
}
```
- Response 201 (or existing enrollment object):
```json
{
  "id": "uuid",
  "course_id": "uuid",
  "user_id": "24-char-mongo-id",
  "completed": false,
  "progress_percentage": 0,
  "enrolled_at": "datetime",
  "last_accessed_at": "datetime",
  "completed_at": "datetime|null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
- Errors:
  - `403 {"detail":"Course is not published"}`
  - `404 {"detail":"Course not found"}`

### GET /api/v1/enrollments/me
- Auth: Required role `learner`
- Query params: `skip`, `limit`, `completed`, `search`
- Response 200:
```json
{
  "items": [
    {
      "id": "uuid",
      "course_id": "uuid",
      "user_id": "24-char-mongo-id",
      "completed": false,
      "progress_percentage": 0,
      "enrolled_at": "datetime",
      "last_accessed_at": "datetime",
      "completed_at": "datetime|null",
      "created_at": "datetime",
      "updated_at": "datetime",
      "course_title": "string",
      "course_thumbnail": "string|null",
      "course_instructor": "string",
      "total_lessons": 0,
      "completed_lessons": 0
    }
  ],
  "total": 0,
  "page": 1,
  "size": 100,
  "pages": 0,
  "stats": {
    "total_enrollments": 0,
    "active_enrollments": 0,
    "completed_enrollments": 0,
    "average_progress": 0,
    "total_courses_enrolled": 0
  }
}
```

### GET /api/v1/enrollments/course/{course_id}/enrollments
- Auth: Required role `instructor`
- Query params: `skip`, `limit`
- Response 200:
```json
{
  "course_id": "uuid",
  "course_title": "string",
  "items": [
    {
      "enrollment_id": "uuid",
      "user_id": "24-char-mongo-id",
      "enrolled_at": "datetime",
      "progress_percentage": 0,
      "completed": false,
      "total_time_spent_minutes": 0,
      "last_accessed_at": "datetime",
      "last_lesson_id": "uuid|null"
    }
  ],
  "total": 0,
  "page": 1,
  "size": 100,
  "pages": 0
}
```

### GET /api/v1/enrollments/instructor
- Auth: Required role `instructor`
- Query params: `skip`, `limit`
- Response 200:
```json
{
  "enrolls": [
    {
      "course_id": "uuid",
      "course_title": "string",
      "items": [
        {
          "enrollment_id": "uuid",
          "user_id": "24-char-mongo-id",
          "enrolled_at": "datetime",
          "progress_percentage": 0,
          "completed": false,
          "total_time_spent_minutes": 0,
          "last_accessed_at": "datetime",
          "last_lesson_id": "uuid|null"
        }
      ]
    }
  ],
  "total": 0,
  "page": 1,
  "size": 100,
  "pages": 0
}
```

## Common Error Contract
- `401` invalid/expired token
- `403` role or ownership violation
- `404` resource not found
- `422` validation errors from FastAPI/Pydantic
- `500 {"detail":"Internal server error"}` for uncaught errors
