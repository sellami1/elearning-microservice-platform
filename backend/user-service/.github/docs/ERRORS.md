---
# User Service — Errors

## Error Shape
```json
{ "status": 400, "message": "..." }
```
<!-- confirm --> Runtime `status` is a string in code (`Fail`/`Error`), while validation errors return `{ "errors": [...] }`.

## Error Reference
| Status | Code/Message | Trigger |
|--------|-------------|---------|
| 400 | Validation errors array | Missing/invalid request body, params, or format |
| 400 | "Verification token is invalid or expired" | Invalid/expired email verification token |
| 401 | "Incorrect email or password" | Login with wrong credentials |
| 401 | "Invalid token, please login again.." | JWT signature invalid |
| 401 | "Token expired, please login again.." | JWT expired |
| 403 | "Please verify your account to access this route." | Authenticated user not verified |
| 429 | "Too many authentication attempts. Please try again later" | Auth limiter exceeded |
| 429 | "Too many reset/verification requests. Please try again in an hour" | Forgot/reset limiter exceeded |
| 500 | "Email sending failed. Try again later!" | Email provider send error in forgot password flow |

## Frontend Handling Guide
| Status | What to do in UI |
|--------|-----------------|
| 400 | Show field validation errors; if no `errors` array, show returned message |
| 401 | Clear token and redirect to login |
| 403 | Show verification-required state or block protected action |
| 409 | <!-- confirm --> Not directly emitted by controllers; duplicate email may surface as 400 (validator) or DB duplicate mapped message |
| 500 | Show generic error notification and retry option |
---
