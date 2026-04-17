---
# User Service — Data Models

## User
**Collection:** `public.analytics_events` and `public.course_daily_metrics` <!-- confirm -->

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | UUID | Yes | `uuid4` | Primary key on both tables. |
| event_type | Enum(`course_view`,`course_enroll`) | Yes | — | In `analytics_events`. |
| user_id | String(24) | No | — | In `analytics_events`; sourced from JWT claim `userId`. |
| course_id | UUID | Yes | — | Present in both tables. |
| user_role | Enum(`learner`,`instructor`) | Yes | — | In `analytics_events`. |
| metric_date | Date | Yes | — | In `course_daily_metrics`; unique with `course_id`. |
| views_count | Integer | No | `0` | In `course_daily_metrics`. |
| enrollments_count | Integer | No | `0` | In `course_daily_metrics`. |
| created_at | DateTime (tz) | No | `now()` | Server-generated timestamp. |
| updated_at | DateTime (tz) | No | `now()` + on update | Auto-updated timestamp. |

## Rules
- Pre-save hooks: None explicitly defined.
- Virtual fields: None defined.
- Indexes: Unique constraint `uix_course_metric_date` on (`course_id`, `metric_date`).

## Exposed vs Internal Fields
**Never expose:** Not explicitly restricted in code; all response schemas intentionally omit `updated_at` and internal SQL metadata.
**Always expose:** Event responses expose `id`, `event_type`, `user_id`, `course_id`, `user_role`, `created_at`; metric responses expose `course_id`, counts, and date.
---