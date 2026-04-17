---
# User Service — Endpoints

Base URL: `http://localhost:8000`

## Auth Routes `/auth`
| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| — | — | — | — | No `/auth` routes are implemented in analytics-service. |

---
## User Routes `/users`
| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| POST | /events/view | Yes | Any authenticated role | Records a `course_view` event and updates daily metrics for a course. |
| POST | /events/enroll | Yes | Any authenticated role | Records a `course_enroll` event and updates daily metrics for a course. |
| GET | /metrics/course/{course_id} | Yes | Any authenticated role | Returns daily metrics history for a course (cached by Redis). |
| GET | /metrics/top-courses | Yes | Any authenticated role | Returns top courses by total views with enrollments totals (cached by Redis). |
| GET | /health | No | Any | Returns service health status. |
| GET | / | Yes | Any authenticated role | Returns welcome message and decoded token payload. |
---