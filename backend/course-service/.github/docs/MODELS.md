---
# User Service — Data Models

## User
**Collection:** PostgreSQL tables: `courses`, `lessons`, `enrollments`, `lesson_progress` <!-- confirm -->

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | UUID | Yes | `uuid4` | Base primary key for all models. |
| created_at | DateTime | Yes | `datetime.utcnow` | Base timestamp on create. |
| updated_at | DateTime | Yes | `datetime.utcnow` + update | Base timestamp on update. |
| title | String(255) | Yes | — | Course and Lesson title fields. |
| instructor_id | String(255) | Yes | — | Owner id on courses. |
| course_id | UUID | Yes | — | FK on lessons/enrollments/lesson_progress. |
| user_id | String(24) | Yes | — | Learner id on enrollments. |
| content_type | String(50) | Yes | — | Lesson type (video/text/pdf/quiz/audio/image via schema enum). |
| published | Boolean | No | `False` | Course publish status. |
| is_published | Boolean | No | `True` | Lesson publish status. |
| progress_percentage | Float | No | `0.0` | Enrollment progress. |

## Rules
- Pre-save hooks: None defined.
- Virtual fields: None defined.
- Indexes: Multiple column indexes via `index=True`; unique constraints on (`user_id`,`course_id`) in enrollments and (`enrollment_id`,`lesson_id`) in lesson_progress.

## Exposed vs Internal Fields
**Never expose:** Not globally enforced by middleware; responses are controlled by Pydantic response schemas.
**Always expose:** Typical responses include ids, ownership/course relation ids, status/progress fields, and timestamps per endpoint schema.
---