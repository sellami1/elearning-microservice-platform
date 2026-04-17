---
# User Service — Auth

## Strategy
- Token type: JWT (Bearer)
- Access token expiry: Not set in this service (validated from token claims only) <!-- confirm -->
- Refresh token: No — expiry: N/A
- Storage expected by client: `Authorization: Bearer <token>` header

## Roles
| Role | Description |
|------|-------------|
| learner | Role value accepted from decoded JWT and stored with analytics events. |
| instructor | Role value accepted from decoded JWT and stored with analytics events. |

## Middleware
**File:** `app/auth.py`
- What it checks: Decodes JWT using `JWT_SECRET_KEY` and `JWT_ALGORITHM`; rejects expired/invalid tokens.
- Attaches to req: Dependency returns `{ user_id, role }` from token payload (`userId` -> `user_id`).
- On failure: returns `{ status: 401, message: "Token expired" }` or `{ status: 401, message: "Invalid token" }`.

## Token Flow
1. Login: Not implemented in this service; token is expected from upstream auth service. <!-- confirm -->
2. Client sends: Authorization: Bearer <accessToken>
3. On expiry: API returns 401 with `Token expired`; client must obtain a new token from auth service. <!-- confirm -->
---