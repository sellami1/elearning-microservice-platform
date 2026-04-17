For context, inspect: Entry point file, package.json, and environment variables file.

Generate a OVERVIEW.md at ".github/docs/OVERVIEW.md" using EXACTLY this format, be brief, no filler sentences:

---
# User Service — Overview
**Port:** ...
**Base path:** ...
**Responsibility:** one sentence max

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Runtime | ... |
| Framework | ... |
| Database | ... |
| Auth | ... |

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| ... | Yes/No | ... |

## Entry Point
Describe in max 3 bullet points what app.ts sets up (middleware, routes, DB connection).
---

Only include what's actually in the files. Mark anything uncertain with <!-- confirm -->.