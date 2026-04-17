---
# User Service — Errors

## Error Shape
```json
{ "detail": "..." }
```

## Error Reference
| Status | Code/Message | Trigger |
|--------|-------------|---------|
| 400 | "Content file or URL is required for ... lessons" | Missing lesson content input for required content types |
| 401 | "Token expired" / "Invalid token" | Expired or invalid JWT in bearer auth |
| 403 | "Role ... not authorized" / "Not authorized ..." | Role not allowed or non-owner access to instructor resources |
| 404 | "Course not found" / "Lesson not found" | Resource does not exist or is hidden by access rules |
| 422 | "Unprocessable Entity" | FastAPI/Pydantic request validation or explicit `422` from handlers |
| 500 | "Internal server error" / "... failed: ..." | Unhandled exception or wrapped internal operation failure |

## Frontend Handling Guide
| Status | What to do in UI |
|--------|-----------------|
| 400 | Show actionable input error and let user correct request data. |
| 401 | Prompt login/token renewal via upstream auth provider. |
| 403 | Show authorization message and navigate away from restricted actions. |
| 404 | Show not-found state for hidden or missing resources. |
| 422 | Display field-level validation feedback. |
| 500 | Show generic error toast and allow retry. |
---