# Docker Compose Deploy and Redeploy Guide

This guide explains the most useful Docker Compose deploy/redeploy commands, their flags, when to use each, and example use cases.

Scope assumptions:
- Monorepo root contains docker-compose.yml
- Target service example: user-service
- Typical command location: repository root

## Quick Decision Matrix

- I changed only app code for one service: `docker compose up -d --build --no-deps user-service`
- I changed dependencies or Dockerfile and cache may hide changes: `docker compose build --no-cache user-service && docker compose up -d --no-deps user-service`
- I changed only environment variables or compose config: `docker compose up -d --force-recreate --no-deps user-service`
- I want to start full stack from scratch (keep volumes): `docker compose down && docker compose up -d --build`
- I want to reset everything including databases: `docker compose down -v && docker compose up -d --build`

## Container Lifecycle Clarification

`docker compose up` does not always create new containers.

- If the service container already exists and nothing important changed, Compose reuses it (starts it if stopped).
- Compose recreates a container only when needed (for example image/config changed), or when explicitly forced.

`docker compose down` always stops and removes the project containers and default networks.

- After `down`, the next `up` must create containers again.
- Volumes are preserved unless `-v` is used.

Practical rule:
- Prefer `stop/start` for routine pause/resume.
- Use `down/up` for clean stack resets.

## Core Commands and Flags

## 1) `docker compose up`

Starts (or updates) services.

Common flags:
- `-d`: detached/background mode
- `--build`: build images before starting containers
- `--no-deps`: do not start/restart dependent services
- `--force-recreate`: recreate containers even if config/image did not change
- `--remove-orphans`: remove containers not defined in current compose file

Example:
```bash
docker compose up -d --build --no-deps user-service
```

Use case:
- Redeploy only `user-service` after code changes, without touching MongoDB or other services.

## 2) `docker compose build`

Builds images without starting containers.

Common flags:
- `--no-cache`: rebuild all layers from scratch
- `--pull`: always try to pull newer base images

Example:
```bash
docker compose build --no-cache --pull user-service
```

Use case:
- You updated dependencies and suspect stale cache layers.

Then start/recreate container:
```bash
docker compose up -d --no-deps user-service
```

## 3) `docker compose down`

Stops and removes containers, networks created by compose.

Common flags:
- `-v`: also remove named and anonymous volumes
- `--remove-orphans`: remove containers from older compose definitions

Examples:
```bash
docker compose down
```
Use case:
- Clean restart of stack while preserving DB volumes.

```bash
docker compose down -v
```
Use case:
- Full reset including PostgreSQL/Mongo data (destructive).

## 4) `docker compose restart`

Restarts existing containers without rebuilding images.

Example:
```bash
docker compose restart user-service
```

Use case:
- Quick restart after temporary runtime issue when image/config has not changed.

## 5) `docker compose stop` and `docker compose start`

- `stop`: stop running containers
- `start`: start previously created containers

Example:
```bash
docker compose stop user-service && docker compose start user-service
```

Use case:
- Pause/resume service quickly without recreating containers.

## 6) `docker compose ps` and `docker compose logs`

- `ps`: container status
- `logs -f`: live logs

Examples:
```bash
docker compose ps
```
```bash
docker compose logs -f --tail=200 user-service
```

Use case:
- Verify successful redeploy and inspect startup errors.

## Recommended Redeploy Patterns

## Pattern A: Fast redeploy of one service (most common)
```bash
docker compose up -d --build --no-deps user-service
```
When:
- App code changed in `backend/user-service`
- No need to bounce DB or sibling services

## Pattern B: Clean image rebuild for one service
```bash
docker compose build --no-cache --pull user-service && docker compose up -d --no-deps user-service
```
When:
- Dependency changes
- Dockerfile layer behavior is uncertain
- You want deterministic rebuild

## Pattern C: Recreate one service container even without image change
```bash
docker compose up -d --force-recreate --no-deps user-service
```
When:
- Environment variable values changed
- Container got into bad runtime state

## Pattern D: Full stack refresh (keep data)
```bash
docker compose down && docker compose up -d --build
```
When:
- Multiple services changed
- Need clean service-to-service reconnection

## Pattern E: Full stack reset (drop data)
```bash
docker compose down -v && docker compose up -d --build
```
When:
- Local DB state is corrupted or tests require fresh data
- You explicitly accept data loss

## Day-to-Day Optimization Workflow

Use this flow to reduce startup time and avoid unnecessary container recreation.

1. First run of a project
```bash
docker compose up -d
```

2. Daily pause/resume
```bash
docker compose stop
docker compose start
```

3. Rebuild only when code/image changed
```bash
docker compose up -d --build --no-deps user-service
```

4. Recreate only when config/env changed
```bash
docker compose up -d --force-recreate --no-deps user-service
```

5. Use full teardown only when truly needed
```bash
docker compose down
```
or destructive reset:
```bash
docker compose down -v
```

## Safety Notes

- `down -v` is destructive for databases.
- `--no-deps` is great for speed, but do not use it when dependency containers also need updates.
- `restart` does not rebuild images. If code changed inside image, use `up --build`.
- If an env var changed in compose, use `up -d --force-recreate` for that service.

## Practical Examples for This Repository

- Redeploy Swagger changes in user service only:
```bash
docker compose up -d --build --no-deps user-service
```

- Check service and logs after redeploy:
```bash
docker compose ps && docker compose logs -f --tail=100 user-service
```

- Redeploy all backend services after shared JWT env changes:
```bash
docker compose up -d --build user-service course-service analytics-service
```

## Troubleshooting Checklist

- Service not reachable:
  - Check port mapping with `docker compose ps`
  - Check health endpoint/logs
- Old code still running:
  - Use `build --no-cache` then `up -d`
- Env changes not applied:
  - Use `up -d --force-recreate`
- Broken local DB state:
  - Use `down -v` only if you can lose data
