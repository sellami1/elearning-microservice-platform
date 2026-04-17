For conext, inspect: error handling middleware files, controller error handling patterns, and any custom error classes.

Generate ERRORS.md at ".github/docs/ERRORS.md" using EXACTLY this format:

---
# User Service — Errors

## Error Shape
\```json
{ "status": 400, "message": "..." }
\```

## Error Reference
| Status | Code/Message | Trigger |
|--------|-------------|---------|
| 400 | "Validation failed" | Missing/invalid body fields |
| 401 | "Invalid token" | Missing or expired JWT |
| 403 | "Forbidden" | Wrong role for route |
| 404 | "User not found" | Non-existent user id |
| 409 | "Email already exists" | Duplicate registration |
| 500 | "Internal server error" | Unhandled exception |

## Frontend Handling Guide
| Status | What to do in UI |
|--------|-----------------|
| 400 | Show field validation errors |
| 401 | Attempt token refresh → redirect to /login |
| 403 | Redirect to /unauthorized |
| 409 | Show "Email already in use" inline |
| 500 | Show generic error toast |
---