# ACEest Fitness & Gym — Flask CI/CD Project

![CI](https://github.com/iamprakashmishra0/aceest-fitnes/actions/workflows/main.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Tests](https://img.shields.io/badge/tests-88%20passed-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Docker](https://img.shields.io/badge/docker-ready-blue)

A modular **Flask web application** for fitness and gym management, built for
**Introduction to DevOps — Assignment 1 (CSIZG514/SEZG514)**.

The repository implements all six assignment phases:

1. **Application Development & Modularization** — layered Flask app with an HTML UI and a JSON API.
2. **Version Control** — Git Flow, Conventional Commits and release tags.
3. **Unit Testing** — Pytest suite (88 tests, 100% coverage).
4. **Containerization** — multi-stage, slim, non-root Docker image.
5. **Jenkins BUILD** — declarative pipeline and a Dockerised controller.
6. **GitHub Actions** — Build & Lint → Docker Assembly → containerised tests.

---

## 1. Features

| Area | Description |
| --- | --- |
| **Client management** | Create, update, list and delete gym clients (name, age, height, weight, program, goals, membership). |
| **Program catalogue** | Fat Loss (3/5-day), Muscle Gain (PPL) and Beginner programs, each with a calorie factor. |
| **Calorie estimation** | `daily calories = weight × program factor`. |
| **BMI + risk** | BMI with underweight/normal/overweight/obese classification and a risk note. |
| **Progress tracking** | Weekly adherence logging with rolling summary (weeks logged + average). |
| **Workout logging** | Log workouts (type, duration, notes) with optional nested exercises (sets/reps/weight). |
| **Body metrics** | Track weight, waist and body-fat over time. |
| **AI-style generator** | Generates a weekly workout split based on the client's program and experience level. |
| **JSON API** | A machine-readable API for every core operation (used later by CI/CD smoke tests). |

---

## 2. Technologies

- **Python 3.10+** (developed and verified on Python 3.12)
- **Flask 3.x** — web framework / application factory
- **SQLite** — zero-configuration embedded database (`sqlite3` stdlib)
- **Jinja2 + HTML/CSS** — server-rendered UI

No other third-party runtime dependencies are required, which keeps the later
Docker image small and the pipeline fast.

---

## 3. Project Structure

```
aceest-fitness/
├── app.py                     # Entry point — creates and runs the app
├── config.py                  # Dev / Test / Prod configuration classes
├── requirements.txt           # Runtime dependencies
├── README.md                  # This document
├── .gitignore
│
├── aceest/                    # Application package
│   ├── __init__.py            # create_app() application factory
│   ├── db.py                  # SQLite connection handling + schema + seed data
│   ├── repository.py          # Data-access layer (all SQL lives here)
│   ├── services.py            # Pure business logic (calories, BMI, generator)
│   ├── utils.py               # Small parsing/type-coercion helpers
│   └── routes/
│       ├── __init__.py
│       ├── views.py           # HTML routes (Blueprint "views")
│       └── api.py             # JSON API routes (Blueprint "api")
│
├── templates/                 # Jinja2 templates
│   ├── base.html
│   ├── index.html             # Dashboard
│   ├── clients.html           # Client directory + registration form
│   ├── client_detail.html     # Profile, progress, workouts, metrics, generator
│   └── programs.html          # Program catalogue
│
├── static/
│   └── css/style.css          # Dark + gold theme
│
├── tests/                     # Pytest suite (Phase 3)
│   ├── conftest.py            # Shared fixtures (app, client, sample_client)
│   ├── test_services.py       # Business-logic unit tests
│   ├── test_utils.py          # Parsing-helper unit tests
│   ├── test_db.py             # Schema + seeding tests
│   ├── test_repository.py     # Data-access integration tests
│   ├── test_api.py            # JSON API integration tests
│   └── test_views.py          # HTML route integration tests
│
├── docs/
│   ├── git-workflow.md        # VCS strategy (Phase 2)
│   ├── testing.md             # Testing guide (Phase 3)
│   ├── docker.md              # Docker guide (Phase 4)
│   ├── jenkins.md             # Jenkins install + setup guide (Phase 5)
│   └── github-actions.md      # GitHub Actions CI guide (Phase 6)
│
├── .github/
│   └── workflows/
│       └── main.yml           # GitHub Actions CI pipeline (Phase 6)
│
├── jenkins/                   # Jenkins controller (Phase 5)
│   ├── Dockerfile             # Jenkins LTS + Python + Docker CLI + plugins
│   ├── plugins.txt            # Required Jenkins plugins
│   ├── docker-compose.yml     # One-command local Jenkins
│   └── casc/jenkins.yaml      # Configuration as Code (admin + job)
│
├── Dockerfile                 # Multi-stage container build (Phase 4)
├── .dockerignore              # Build-context exclusions
├── .flake8                    # Lint configuration (Phase 6)
├── Jenkinsfile                # Declarative CI pipeline (Phase 5)
├── pytest.ini                 # Pytest + coverage configuration
├── requirements-dev.txt       # Test + lint dependencies
└── requirements.txt           # Runtime dependencies
```

---

## 4. Local Setup

### 4.1 Prerequisites

- Python 3.10 or newer
- `pip` and `venv` (bundled with Python)
- Git (optional, for version control)
- Docker Engine 20.10+ (optional, for the containerized workflow — Phase 4)

Verify your Python version:

```bash
python3 --version
```

### 4.2 Create a virtual environment

```bash
# from the project root (the folder containing app.py)
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows (PowerShell / cmd)
```

### 4.3 Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Running the Application

Start the development server:

```bash
python app.py
```

You should see output similar to:

```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

Open a browser and navigate to **http://localhost:5000**.

Alternatively, run it directly with the Flask CLI:

```bash
flask --app app run --debug
```

To bind to a specific host/port:

```bash
flask --app app run --host 0.0.0.0 --port 8080
```

The SQLite database (`aceest_fitness.db`) is created automatically on first
run and is pre-seeded with one demo client so the dashboard is not empty. This
file is git-ignored.

### Environment variables (optional)

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Flask session/flash secret | `aceest-dev-secret-change-me` |
| `ACEEST_DATABASE` | Path to the SQLite database file | `./aceest_fitness.db` |
| `FLASK_CONFIG` | Config class to load | `config.DevelopmentConfig` |

Example:

```bash
ACEEST_DATABASE=/tmp/aceest.db python app.py
```

---

## 6. Using the Web UI

1. Open **http://localhost:5000** — the dashboard shows total clients, workouts
   logged, average adherence and the number of programs.
2. Go to **Clients → Register / Update Client** and fill in the form. Selecting
   a program and entering a weight automatically computes the daily calories.
3. Open a client to see their **profile, weekly adherence, workout history,
   body metrics** and to **generate an AI-style weekly plan**.
4. The **Programs** page lists all training programs with their calorie factors.

---

## 7. JSON API Reference

Base URL: `http://localhost:5000/api`

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness probe (`{"status": "ok"}`). |
| `GET` | `/programs` | Program catalogue. |
| `GET` | `/clients` | List all clients. |
| `POST` | `/clients` | Create/update a client. |
| `GET` | `/clients/<id>` | Get one client. |
| `PUT` | `/clients/<id>` | Update a client. |
| `DELETE` | `/clients/<id>` | Delete a client. |
| `GET` | `/clients/<id>/progress` | Weekly adherence history. |
| `POST` | `/clients/<id>/progress` | Log adherence. |
| `GET` | `/clients/<id>/workouts` | Workout history (with exercises). |
| `POST` | `/clients/<id>/workouts` | Log a workout. |
| `GET` | `/clients/<id>/metrics` | Body-metrics history. |
| `POST` | `/clients/<id>/metrics` | Log body metrics. |
| `POST` | `/calculate/bmi` | BMI from `weight` + `height`. |
| `POST` | `/calculate/calories` | Calories from `weight` + `program`. |
| `POST` | `/generate-program` | Generate a weekly plan. |

### Example API calls

Health check:

```bash
curl http://localhost:5000/api/health
```

Create a client:

```bash
curl -X POST http://localhost:5000/api/clients \
  -H "Content-Type: application/json" \
  -d '{"name":"Arjun","age":32,"height":178,"weight":82,"program":"Muscle Gain (MG) - PPL"}'
```

Estimate calories:

```bash
curl -X POST http://localhost:5000/api/calculate/calories \
  -H "Content-Type: application/json" \
  -d '{"weight":82,"program":"Muscle Gain (MG) - PPL"}'
# => {"calories": 2870}
```

Calculate BMI:

```bash
curl -X POST http://localhost:5000/api/calculate/bmi \
  -H "Content-Type: application/json" \
  -d '{"weight":82,"height":178}'
```

Generate a program:

```bash
curl -X POST http://localhost:5000/api/generate-program \
  -H "Content-Type: application/json" \
  -d '{"program":"Fat Loss (FL) - 3 day","experience":"intermediate"}'
```

---

## 8. Modularization — Design Rationale

The application follows a **layered architecture** so that each concern can be
tested, replaced or containerised independently:

| Layer | File(s) | Responsibility |
| --- | --- | --- |
| **Application factory** | `aceest/__init__.py` | Builds the app and wires blueprints; supports per-environment config (critical for CI/CD). |
| **Configuration** | `config.py` | Dev/Test/Prod settings; test config uses an isolated temporary SQLite file. |
| **Persistence** | `aceest/db.py` | Single place for connections + schema. |
| **Repository** | `aceest/repository.py` | All SQL queries behind plain functions returning dicts. |
| **Domain logic** | `aceest/services.py` | Pure, framework-free functions (calories, BMI, generator). |
| **Transport (web)** | `aceest/routes/views.py` | HTML pages. |
| **Transport (API)** | `aceest/routes/api.py` | JSON endpoints. |
| **Presentation** | `templates/`, `static/` | Jinja2 templates and CSS. |

Because the business logic in `services.py` has **no database or Flask
dependency**, it can be unit-tested with Pytest in isolation (Phase 3) and the
test config uses an isolated temporary database (`TestingConfig`) so test runs
never touch real data.

---

## 9. Version Control Strategy (Phase 2)

The repository follows a lightweight **Git Flow** model with **Conventional
Commits**. Full details live in [`docs/git-workflow.md`](docs/git-workflow.md).

| Branch | Purpose | Lifetime |
| --- | --- | --- |
| `main` | Production-ready, tagged releases. | Permanent |
| `develop` | Integration branch for completed work. | Permanent |
| `feature/*` | New capabilities. | Temporary |
| `bugfix/*` | Defect fixes. | Temporary |
| `infra/*` | Tooling, configuration, documentation. | Temporary |

Commit types: `feat`, `fix`, `docs`, `test`, `refactor`, `infra`, `ci`. Feature
branches are merged into `develop` with `--no-ff` so the history is preserved,
and `develop` is promoted to `main` and tagged `v1.0.0` at each milestone.

To synchronise the local repository with GitHub:

```bash
git remote add origin https://github.com/<your-username>/aceest-fitness.git
git push -u origin main
git push -u origin develop
git push origin --tags
```

Or, with the GitHub CLI:

```bash
gh auth login
gh repo create aceest-fitness --public --source=. --remote=origin --push
```

---

## 10. Testing (Phase 3)

The project uses **Pytest** with **pytest-cov** for unit and integration testing.
The full guide lives in [`docs/testing.md`](docs/testing.md); the essentials are
below.

### 10.1 Install test dependencies

```bash
pip install -r requirements-dev.txt
```

### 10.2 Run the tests manually

From the project root:

```bash
pytest
```

`pytest.ini` configures the test path and the coverage report, so no extra flags
are needed. Useful variations:

```bash
pytest -v                              # verbose output
pytest tests/test_services.py          # a single file
pytest tests/test_api.py::test_health  # a single test
pytest -k "bmi or calorie"             # keyword filter
```

Expected result: **88 tests passing with 100% coverage** of the `aceest` package.

```
TOTAL                         377      0   100%
============================== 88 passed in 6.18s ===============================
```

### 10.3 Coverage reports

```bash
pytest --cov=aceest --cov-report=html     # browsable htmlcov/index.html
pytest --cov=aceest --cov-fail-under=90   # enforce a coverage gate (CI)
```

### 10.4 Test layout

| File | Validates |
| --- | --- |
| `tests/test_services.py` | Calories, BMI, program generator (pure logic). |
| `tests/test_utils.py` | Parsing/type-coercion helpers. |
| `tests/test_db.py` | Schema creation and idempotent seeding. |
| `tests/test_repository.py` | Client/progress/workout/metrics CRUD and cascades. |
| `tests/test_api.py` | JSON endpoints, status codes and error handling. |
| `tests/test_views.py` | HTML pages, forms, redirects and `404`s. |

Tests are fully isolated: `config.TestingConfig` points at a unique temporary
SQLite file, and the `app` fixture empties every table before each test.

---

## 11. Docker (Phase 4)

The application ships as a portable Docker image built from a **multi-stage
`Dockerfile`**. The full guide lives in [`docs/docker.md`](docs/docker.md).

### 11.1 What the image provides

- `python:3.12-slim-bookworm` base, pinned for reproducible builds.
- Multi-stage build (`builder` → `test`, `runtime`) so build/test tooling never
  reaches the final image.
- **Gunicorn** as the production WSGI server (never the Flask dev server).
- Runs as the unprivileged **`app`** user (non-root).
- `HEALTHCHECK` against `/api/health` and SQLite data persisted in `/data`.
- Production image size ≈ **224 MB**.

### 11.2 Build

```bash
docker build -t aceest-fitness:latest .              # production image
docker build --target test -t aceest-fitness:test .  # test image (app + tooling)
```

### 11.3 Run

```bash
docker run -d --name aceest -p 5000:5000 \
  -v aceest-data:/data \
  -e SECRET_KEY="replace-with-a-strong-secret" \
  aceest-fitness:latest
```

Then open <http://localhost:5000/> or check `curl http://localhost:5000/api/health`.

### 11.4 Run the test suite inside the container

```bash
docker build --target test -t aceest-fitness:test .
docker run --rm aceest-fitness:test python -m pytest -q   # 88 passed, 100% coverage
```

---

## 12. Jenkins BUILD (Phase 5)

Jenkins owns the primary **BUILD** phase: it pulls the latest code from GitHub
and performs a clean build of the environment in a controlled sandbox. The full
install and setup guide is in [`docs/jenkins.md`](docs/jenkins.md).

### 12.1 Pipeline stages

The declarative [`Jenkinsfile`](Jenkinsfile) runs:

| Stage | Purpose |
| --- | --- |
| Checkout | Pull the latest revision from `origin/main`. |
| Build | Clean virtualenv, install dependencies, byte-compile, `pip check`. |
| Test | Pytest with a **90% coverage gate**; publishes JUnit + coverage. |
| Docker Build | Build `aceest-fitness:<build-number>`. |
| Smoke Test | Run the image and probe `/api/health`. |

### 12.2 Install & run Jenkins (Docker, recommended)

```bash
# from the repository root
docker-compose -f jenkins/docker-compose.yml up -d --build
# open http://localhost:8080  (admin / admin)
```

The image bundles Python, the Docker CLI and the required plugins, and
Configuration-as-Code automatically creates the `aceest-fitness` pipeline job.

A native Ubuntu/Debian installation (Java 17 + the Jenkins apt repository) and
manual job setup are documented in [`docs/jenkins.md`](docs/jenkins.md).

### 12.3 Trigger a build

- **Build Now** in the UI, or
- **Poll SCM** (`H/5 * * * *`), or
- a **GitHub webhook** to `http://<jenkins-host>:8080/github-webhook/`.

---

## 13. GitHub Actions (Phase 6)

A fully automated CI pipeline lives in
[`.github/workflows/main.yml`](.github/workflows/main.yml) and runs on every
push and pull request. The detailed guide is
[`docs/github-actions.md`](docs/github-actions.md).

### 13.1 Pipeline stages

| Job | Purpose |
| --- | --- |
| **Build & Lint** | Install deps, `compileall` syntax check, `flake8` lint. |
| **Docker Image Assembly** | Build the production image (BuildKit + GHA cache) and smoke-test `/api/health`. |
| **Automated Testing (container)** | Run Pytest **inside** the test image, enforce 90% coverage, upload reports. |

```
build-and-lint ──┬──► docker-image
                 └──► test-in-container
```

### 13.2 Triggers

- every `push` to `main` / `develop`,
- every `pull_request` targeting `main` / `develop`,
- manual runs via **Actions → CI → Run workflow**.

No secrets are required. Test/coverage reports are published as the
`test-reports` workflow artefact.

### 13.3 Jenkins + GitHub Actions integration

The two systems are complementary and share the same artefacts
(`Dockerfile`, `requirements*.txt`, `pytest.ini`, `.flake8`), so they enforce an
identical quality gate (`pytest --cov-fail-under=90`):

- **GitHub Actions** gives fast, per-commit and pull-request feedback entirely
  on GitHub's infrastructure.
- **Jenkins** performs the authoritative clean **BUILD** on a controlled
  self-hosted server once work reaches `main`.

A commit therefore passes the same build, lint and containerised test checks in
both environments — guaranteeing consistency from local development to release.

---

## 14. Troubleshooting

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'flask'` | Activate the venv and run `pip install -r requirements.txt`. |
| `pytest: command not found` | Install the test extras: `pip install -r requirements-dev.txt`. |
| `flake8` reports errors | Fix the reported lines; tuning lives in `.flake8`. |
| `Address already in use` on port 5000 | Run on another port: `flask --app app run --port 8080` (or `-p 8080:5000` with Docker). |
| `docker: command not found` | Install Docker Engine and ensure the daemon is running. |
| Image builds but the app is unhealthy | Check `docker logs aceest`; ensure port `5000` is free and `/data` is writable. |
| Jenkins job can't find the `Jenkinsfile` | Set Script Path to `Jenkinsfile` and branch spec to `*/main`. |
| Jenkins can't use Docker in a build | Mount `/var/run/docker.sock` and grant the user Docker access (see `docs/jenkins.md`). |
| GitHub Actions workflow missing | Ensure `.github/workflows/main.yml` is on the default branch. |
| Database looks out of date | Delete `aceest_fitness.db` and restart to recreate/seed it. |
| Templates not found | Run the app from the project root containing `templates/`. |

---

*ACEest Fitness & Gym — Introduction to DevOps, Assignment 1, Phases 1–6.*
