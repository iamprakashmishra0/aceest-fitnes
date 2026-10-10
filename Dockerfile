# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# ACEest Fitness & Gym — production Docker image (Phase 4)
#
# Multi-stage build:
#   builder  -> installs runtime dependencies into an isolated virtualenv
#   test     -> adds test tooling and runs the Pytest suite (used by CI)
#   runtime  -> slim, non-root image containing only what the app needs
#
# Build the production image (default target):
#   docker build -t aceest-fitness:latest .
# Run the Pytest suite inside the container (CI):
#   docker build --target test -t aceest-fitness:test .
# ---------------------------------------------------------------------------

# ---- Stage 1: builder -----------------------------------------------------
FROM python:3.12-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore

# An isolated virtualenv makes it trivial to copy only the dependencies into
# the runtime stage (and keeps site-packages clean).
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt gunicorn==23.0.0


# ---- Stage 2: test image (CI runs the suite inside this) ------------------
FROM builder AS test

COPY requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

COPY . .

# No test execution here: this stage produces a reproducible image that the
# CI pipeline runs on demand, e.g.
#   docker run --rm aceest-fitness:test python -m pytest


# ---- Stage 3: runtime ------------------------------------------------------
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_CONFIG=config.ProductionConfig \
    ACEEST_DATABASE=/data/aceest_fitness.db

# Create an unprivileged user so the container never runs as root.
RUN groupadd --system app && \
    useradd --system --gid app --home-dir /app --shell /usr/sbin/nologin app

WORKDIR /app

# Bring in the pre-built dependencies, then only the files the app needs.
COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app app.py config.py ./
COPY --chown=app:app aceest/ ./aceest/
COPY --chown=app:app templates/ ./templates/
COPY --chown=app:app static/ ./static/

# Writable location for the SQLite database (mount a volume here).
RUN mkdir -p /data && chown -R app:app /data

USER app

EXPOSE 5000

# Liveness probe against the application's health endpoint.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/api/health').status == 200 else 1)"

# Serve with Gunicorn (production WSGI server), never the dev server.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", \
     "--timeout", "30", "--graceful-timeout", "30", "--access-logfile", "-", \
     "app:app"]
