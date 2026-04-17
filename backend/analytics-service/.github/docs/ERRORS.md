---
# User Service — Errors

## Error Shape
```json
{ "status": 400, "message": "..." }
```

## Error Reference
| Status | Code/Message | Trigger |
|--------|-------------|---------|
| 401 | "Token expired" | JWT `exp` is expired in `Authorization` bearer token |
| 401 | "Invalid token" | JWT decode/signature/format validation fails |
| 403 | "Not authenticated" <!-- confirm --> | Missing/invalid auth header (HTTPBearer behavior) <!-- confirm --> |
| 422 | "Validation Error" | Request body/path/query fails FastAPI/Pydantic validation |
| 500 | "Internal Server Error" <!-- confirm --> | Unhandled exception in request processing |

## Frontend Handling Guide
| Status | What to do in UI |
|--------|-----------------|
| 401 | Prompt re-authentication or token renewal via auth service. |
| 403 | Prompt login and retry request with bearer token. <!-- confirm --> |
| 422 | Show validation feedback for request fields/parameters. |
| 500 | Show generic error message and allow retry. |
---