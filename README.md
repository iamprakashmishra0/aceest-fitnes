# ACEest Fitness & Gym — Flask Application (Phase 1)

A modular **Flask web application** for fitness and gym management, built for
**Introduction to DevOps — Assignment 1 (CSIZG514/SEZG514)**.

This repository contains the **Phase 1** deliverable only:
**Application Development & Modularization**. The original ACEest desktop logic
(Tkinter baseline scripts) has been refactored into a clean, layered, web-ready
Flask application with an HTML UI and a JSON API. The remaining assignment
phases (version control, Pytest, Docker, Jenkins, GitHub Actions) build on top
of this foundation.

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
│   └── testing.md             # Testing guide (Phase 3)
│
├── pytest.ini                 # Pytest + coverage configuration
├── requirements-dev.txt       # Test-only dependencies
└── requirements.txt           # Runtime dependencies
```

---

## 4. Local Setup

### 4.1 Prerequisites

- Python 3.10 or newer
- `pip` and `venv` (bundled with Python)
- Git (optional, for version control)

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

## 11. How this supports the next phases

- **Phase 2 — Version Control:** ✅ completed — repository initialised, branched
  and documented (see section 9).
- **Phase 3 — Pytest:** ✅ completed — 88 tests, 100% coverage, runnable with a
  single `pytest` command (see section 10 and `docs/testing.md`).
- **Phase 4 — Docker:** the single lightweight dependency (Flask) makes the
  image small; `app.py` can be served by a WSGI server such as Gunicorn.
- **Phase 5 — Jenkins BUILD:** Jenkins can `pip install -r requirements-dev.txt`
  and run the app/test suite on a clean checkout.
- **Phase 6 — GitHub Actions:** the `/api/health` endpoint and the factory-based
  app make automated build/test/container stages straightforward.

---

## 12. Troubleshooting

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'flask'` | Activate the venv and run `pip install -r requirements.txt`. |
| `pytest: command not found` | Install the test extras: `pip install -r requirements-dev.txt`. |
| `Address already in use` on port 5000 | Run on another port: `flask --app app run --port 8080`. |
| Database looks out of date | Delete `aceest_fitness.db` and restart to recreate/seed it. |
| Templates not found | Run the app from the project root containing `templates/`. |

---

*ACEest Fitness & Gym — Introduction to DevOps, Assignment 1, Phases 1–3.*
