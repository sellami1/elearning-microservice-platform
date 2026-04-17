For conext, inspect: user/auth routes and controller files.

Generate ENDPOINTS.md at ".github/docs/ENDPOINTS.md" using EXACTLY this format:

---
# User Service — Endpoints

Base URL: `http://localhost:<port>`

## Auth Routes `/auth`
| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| POST | /auth/register | No | Any | ... |
| ... |

### POST /auth/register
**Body:**
\```json
{ "email": "", "password": "", "role": "student|instructor", "fullName": "" }
\```
**Response 201:**
\```json
{ "accessToken": "", "user": { "id": "", "email": "", "role": "" } }
\```
**Errors:** 400, 409

---
## User Routes `/users`
(same pattern per route)
---

Only document what's actually implemented. Mark anything uncertain with <!-- confirm -->.