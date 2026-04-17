For context, inspect: models files, user schema files, and any related files.

Generate MODELS.md at ".github/docs/MODELS.md" using EXACTLY this format:

---
# User Service — Data Models

## User
**Collection:** `users`

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| email | String | Yes | — | unique, lowercase |
| ... |

## Rules
- List any pre-save hooks (e.g. password hashing)
- List any virtual fields
- List indexes

## Exposed vs Internal Fields
**Never expose:** password, __v, ...
**Always expose:** id, email, role, fullName, createdAt
---