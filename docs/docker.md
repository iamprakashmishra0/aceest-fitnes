# Docker Guide — ACEest Fitness & Gym (Phase 4)

Phase 4 encapsulates the Flask application, its Python dependencies and its
runtime into a portable **Docker image**, eliminating "it works on my machine"
inconsistencies between development, testing and the Jenkins build environment.

---

## 1. Overview

| Item | Value |
| --- | --- |
| Base image | `python:3.12-slim-bookworm` (pinned) |
| Build strategy | Multi-stage (`builder` → `test`, `runtime`) |
| WSGI server | Gunicorn 23 (no Flask dev server in production) |
| Runtime user | `app` (unprivileged, non-root) |
| Exposed port | `5000` |
| Data location | `/data` (SQLite database, mount a volume) |
| Production image size | ~224 MB |

---

## 2. The Dockerfile at a glance

The `Dockerfile` uses three stages so that build tooling and test tooling never
leak into the final image:

| Stage | Purpose | Contains |
| --- | --- | --- |
| `builder` | Install runtime deps into an isolated virtualenv (`/opt/venv`) | Flask, Gunicorn |
| `test` | Add test tooling and **run the Pytest suite at build time** (CI) | builder + pytest, coverage |
| `runtime` | Final, slim, non-root production image | venv + app code only |

Because dependencies are installed in a dedicated virtualenv in the `builder`
stage, the `runtime` stage copies **only** `/opt/venv` — no compilers, caches or
pip metadata end up in the shipped image.

---

## 3. Prerequisites

- Docker Engine 20.10+ (`docker --version`)
- Docker Compose is **not** required.

---

## 4. Building the image

From the project root (the folder containing the `Dockerfile`):

```bash
# Production image (default target)
docker build -t aceest-fitness:latest .

# CI/test image (runs the Pytest suite during the build)
docker build --target test -t aceest-fitness:test .
```

A failed test makes `--target test` fail with a non-zero exit code, which is
exactly what the CI pipeline relies on as a quality gate.

---

## 5. Running the container

```bash
docker run -d \
  --name aceest \
  -p 5000:5000 \
  -v aceest-data:/data \
  -e SECRET_KEY="replace-with-a-strong-secret" \
  aceest-fitness:latest
```

| Flag | Why |
| --- | --- |
| `-p 5000:5000` | Publish the app on `http://localhost:5000`. |
| `-v aceest-data:/data` | Persist the SQLite database across restarts. |
| `-e SECRET_KEY=...` | Override the development secret (see Security below). |

Verify it is healthy:

```bash
curl http://localhost:5000/api/health
# {"service":"aceest-fitness","status":"ok"}

docker inspect --format '{{.State.Health.Status}}' aceest
# healthy
```

Open the dashboard at <http://localhost:5000/>.

Useful commands:

```bash
docker logs -f aceest        # follow Gunicorn logs
docker exec aceest whoami    # -> app   (confirms non-root)
docker stop aceest && docker rm aceest
```

---

## 6. Running the tests inside the container

The assignment requires the Pytest suite to execute **inside the containerized
environment**:

```bash
# Option A — tests run during the image build
docker build --target test -t aceest-fitness:test .

# Option B — run the suite on demand
docker run --rm aceest-fitness:test pytest -q
# 88 passed  (100% coverage)
```

---

## 7. Size & security measures

**Size**
- `python:3.12-slim-bookworm` instead of the full base image.
- Multi-stage build: only the virtualenv is copied into the runtime stage.
- `--no-cache-dir` and `PIP_NO_CACHE_DIR=1` — no pip wheel cache in the image.
- `.dockerignore` excludes `.git/`, `.venv/`, caches, coverage data and local
  databases from the build context.
- The runtime stage copies only `app.py`, `config.py`, `aceest/`, `templates/`
  and `static/` — not the tests or docs.

**Security**
- Runs as the unprivileged **`app`** user, never as `root`.
- Gunicorn (production WSGI server) instead of the Flask development server.
- No `apt-get` packages installed; the SQLite driver ships with Python.
- Pinned base image and pinned Gunicorn version for reproducible builds.
- `HEALTHCHECK` wired to `/api/health` so orchestrators can detect failures.
- All dependencies come from `requirements.txt`, keeping the attack surface
  minimal (Flask + Gunicorn only).

> **Secret key:** set `SECRET_KEY` (and optionally `ACEEST_DATABASE`) through
> the environment at run time. Never bake a real secret into the image.

---

## 8. Configuration reference

| Variable | Default | Description |
| --- | --- | --- |
| `FLASK_CONFIG` | `config.ProductionConfig` | Configuration class to load. |
| `ACEEST_DATABASE` | `/data/aceest_fitness.db` | SQLite database path. |
| `SECRET_KEY` | dev fallback | Flask session/signing secret. |

---

## 9. Cleaning up

```bash
docker rm -f aceest
docker rmi aceest-fitness:latest aceest-fitness:test
docker volume rm aceest-data
```

---

*ACEest Fitness & Gym — Introduction to DevOps, Assignment 1, Phase 4.*
