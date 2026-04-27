---
# User Service — Endpoints

Base URL: `http://localhost:8000`

## Auth Routes `/auth`
| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| — | — | — | — | No `/auth` routes are implemented in course-service. |

---
## User Routes `/users`
| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| GET | /api/v1/courses | Optional | Any | Lists courses with role-aware visibility and filters. |
| GET | /api/v1/courses/{course_id} | Optional | Any | Gets one course; unpublished courses are hidden from non-owners and authenticated views are forwarded to analytics. |
| POST | /api/v1/courses | Yes | instructor | Creates a course (multipart form, optional thumbnail upload). |
| PUT | /api/v1/courses/{course_id} | Yes | instructor | Updates owned course (multipart form, optional thumbnail upload). |
| DELETE | /api/v1/courses/{course_id} | Yes | instructor | Deletes owned course and associated media files. |
| GET | /api/v1/courses/instructor/mine | Yes | instructor | Lists current instructor courses. |
| GET | /api/v1/lessons/course/{course_id} | Optional | Any | Lists lessons for a course with owner/public visibility rules. |
| POST | /api/v1/lessons | Yes | instructor | Creates a lesson (multipart form, optional content upload/url). |
| GET | /api/v1/lessons/{lesson_id} | Optional | Any | Gets lesson details with publish/access restrictions. |
| PUT | /api/v1/lessons/{lesson_id} | Yes | instructor | Updates lesson and optionally replaces content file/url. |
| DELETE | /api/v1/lessons/{lesson_id} | Yes | instructor | Deletes lesson and its stored content. |
| POST | /api/v1/enrollments | Yes | learner | Enrolls current learner in a course and records an analytics enroll event. |
| GET | /api/v1/enrollments/me | Yes | learner | Lists current learner enrollments with stats. |
| GET | /api/v1/enrollments/course/{course_id}/enrollments | Yes | instructor | Lists enrollments for one owned course. |
| GET | /api/v1/enrollments/instructor | Yes | instructor | Lists enrollments across instructor-owned courses. |
| GET | /health | No | Any | Service health probe. |
| GET | / | No | Any | Root metadata endpoint. |
---