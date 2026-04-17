I need to refresh the user-service docs after recent changes.

Using these files:
- #file:user-service/src/app.ts
- #file:user-service/src/routes/auth.ts
- #file:user-service/src/routes/users.ts
- #file:user-service/src/controllers/auth.controller.ts
- #file:user-service/src/controllers/user.controller.ts
- #file:user-service/src/models/User.ts
- #file:user-service/src/middleware/auth.ts
- #file:user-service/src/middleware/errorHandler.ts

Regenerate only the sections that have changed in:
- docs/OVERVIEW.md
- docs/AUTH.md
- docs/ENDPOINTS.md
- docs/MODELS.md
- docs/ERRORS.md

For each file, output only the diff — show [UNCHANGED] for sections with no changes.
Mark anything you're unsure about with <!-- confirm -->.