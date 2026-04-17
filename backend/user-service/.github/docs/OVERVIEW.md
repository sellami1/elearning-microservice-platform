# User Service — Overview
**Port:** `process.env.USER_BACKEND_PORT` (default `8002`)
**Base path:** `/api/v1/users` (routes mounted under `/api`) <!-- confirm -->
**Responsibility:** Handles user registration, authentication, account verification, profile updates, and password/email management.

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Runtime | Node.js |
| Framework | Express |
| Database | MongoDB via Mongoose |
| Auth | JWT (`jsonwebtoken`) with Bearer token middleware |

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| USER_BACKEND_PORT | No | HTTP server port (defaults to 8002) |
| USER_BACKEND_ENV | No | Enables dev logging branch when `development` |
| NODE_ENV | No | Controls error response detail in error middleware |
| MONGODB_URI | Yes | MongoDB connection string |
| JWT_SECRET_KEY | Yes | Secret key used to sign/verify JWT |
| JWT_EXPIRE_TIME | Yes | JWT expiry string used in `expiresIn` |
| PUBLIC_FRONTEND_URL | Yes | Base URL for verification/reset links in emails |
| USER_BACKEND_URL | No | Base URL prepended to non-absolute avatar path |
| EMAIL_SECURE | No | SMTP secure transport flag |
| EMAIL_HOST | Yes | SMTP host |
| EMAIL_PORT | Yes | SMTP port |
| EMAIL_USER | No | SMTP username (optional for local SMTP) |
| EMAIL_PASSWORD | No | SMTP password (optional for local SMTP) |
| EMAIL_FROM | No | Override sender address |
| APP_NAME | No | App name used in email templates/from header |

## Entry Point
- Loads env, opens MongoDB connection, and starts Express HTTP server.
- Applies security and parsing middleware (CORS, compression, JSON body limit, sanitize/xss, rate limit, static media).
- Mounts routes, registers 404 forwarding to `ApiError`, then global error middleware.
