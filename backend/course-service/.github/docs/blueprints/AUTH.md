For context, inspect: auth middleware files, user/auth controller files, and token utility functions files.

Generate AUTH.md at ".github/docs/AUTH.md" using EXACTLY this format:

---
# User Service — Auth

## Strategy
- Token type: JWT / Session / ...
- Access token expiry: ...
- Refresh token: Yes/No — expiry: ...
- Storage expected by client: ...

## Roles
| Role | Description |
|------|-------------|
| student | ... |
| instructor | ... |

## Middleware
**File:** `src/middleware/auth.ts`
- What it checks: ...
- Attaches to req: ... (e.g. req.user = { id, role, email })
- On failure: returns { status, message }

## Token Flow
1. Login → returns { accessToken, refreshToken? }
2. Client sends: Authorization: Bearer <accessToken>
3. On expiry: ...
---

Mark anything uncertain with <!-- confirm -->.