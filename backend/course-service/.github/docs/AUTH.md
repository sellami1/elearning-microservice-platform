---
# User Service — Auth

## Strategy
- Token type: JWT (Bearer)
- Access token expiry: Config value `ACCESS_TOKEN_EXPIRE_MINUTES` (default 30) exists, but this service only validates incoming token claims <!-- confirm -->
- Refresh token: No — expiry: N/A
- Storage expected by client: `Authorization: Bearer <accessToken>` header

## Roles
| Role | Description |
|------|-------------|
| student | Represented as `learner` in JWT `role`; required for student-only enrollment endpoints. <!-- confirm --> |
| instructor | Required for instructor-only create/update/delete and instructor enrollment views. |

## Middleware
**File:** `app/core/auth.py`
- What it checks: Validates HTTP Bearer auth, decodes JWT with `JWT_SECRET_KEY` and `JWT_ALGORITHM`, and enforces roles through `require_role`.
- Attaches to req: Dependency returns `{ user_id, role }` from JWT payload (`userId` mapped to `user_id`).
- On failure: returns `{ status: 401, message: "Token expired|Invalid token" }` or `{ status: 403, message: "Role ... not authorized" }`.

## Token Flow
1. Login → returns { accessToken, refreshToken? } : Not implemented in this service; token is expected from an upstream auth service. <!-- confirm -->
2. Client sends: Authorization: Bearer <accessToken>
3. On expiry: API returns `401` with `Token expired`; client must re-authenticate upstream. <!-- confirm -->
---