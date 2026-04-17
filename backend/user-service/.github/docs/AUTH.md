# User Service — Auth

## Strategy
- Token type: JWT
- Access token expiry: `process.env.JWT_EXPIRE_TIME` (`expiresIn` in `createJWT`) <!-- confirm -->
- Refresh token: No — expiry: N/A
- Storage expected by client: Send access token in `Authorization: Bearer <token>` header

## Roles
| Role | Description |
|------|-------------|
| learner | Default user role for learning accounts |
| instructor | User role for instructor accounts |

## Middleware
**File:** `src/middleware/authMiddleware.js` <!-- confirm -->
- What it checks: Bearer token presence, JWT validity (`JWT_SECRET_KEY`), user existence, email verification, and password change time vs token `iat`
- Attaches to req: `req.user = currentUser` (full user document)
- On failure: returns `{ status, message }` via error middleware, commonly 401/403

## Token Flow
1. Login → returns `{ token, data }` (no refresh token)
2. Client sends: `Authorization: Bearer <accessToken>` <!-- confirm -->
3. On expiry: JWT verify fails (`TokenExpiredError`) and API responds 401 with token-expired message