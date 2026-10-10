# Testing Guide — ACEest Fitness & Gym (Phase 3)

This document describes the **Pytest** unit-testing and validation framework
added in Phase 3 of the assignment. The suite validates the Flask application's
internal logic and HTTP surface before code ever reaches the build stage.

---

## 1. Overview

| Item | Value |
| --- | --- |
| Framework | **pytest** |
| Coverage tool | **pytest-cov** |
| Test location | `tests/` |
| Config file | `pytest.ini` |
| Tests | 88 |
| Line coverage | **100%** of the `aceest` package |
| Isolation | Each test runs against a fresh temporary SQLite database |

The suite is organised into layers so each concern can be verified in
isolation:

| File | Layer under test | Type |
| --- | --- | --- |
| `tests/test_services.py` | `aceest.services` (calories, BMI, generator) | Pure unit tests |
| `tests/test_utils.py` | `aceest.utils` (parsing helpers) | Pure unit tests |
| `tests/test_db.py` | `aceest.db` (schema + seeding) | Unit |
| `tests/test_repository.py` | `aceest.repository` (CRUD) | Integration (DB) |
| `tests/test_api.py` | `aceest.routes.api` (JSON endpoints) | Integration (HTTP) |
| `tests/test_views.py` | `aceest.routes.views` (HTML pages) | Integration (HTTP) |
| `tests/conftest.py` | Shared fixtures (`app`, `client`, `sample_client`) | — |

---

## 2. Installing the test dependencies

The runtime dependencies are in `requirements.txt`; the test-only dependencies
are declared separately in `requirements-dev.txt`:

```bash
# From the project root, with the virtual environment activated
pip install -r requirements-dev.txt
```

`requirements-dev.txt` pulls in `pytest` and `pytest-cov` via `-r requirements.txt`.

---

## 3. Running the tests

Run the whole suite from the project root:

```bash
pytest
```

Because `pytest.ini` already sets `testpaths = tests` and the coverage options,
`pytest` alone produces the full result and coverage report.

Useful variations:

```bash
pytest -v                          # verbose, one line per test
pytest tests/test_services.py      # a single file
pytest tests/test_api.py::test_health   # a single test
pytest -k "bmi or calorie"         # tests matching a keyword
pytest -x                          # stop at the first failure
```

Example (abridged) output:

```
collected 88 items

tests/test_api.py ......................               [ 25%]
tests/test_db.py ...                                   [ 28%]
tests/test_repository.py .............                 [ 43%]
tests/test_services.py ..............................  [ 77%]
tests/test_utils.py .....                              [ 82%]
tests/test_views.py ...............                    [100%]

TOTAL                         377      0   100%
============================== 88 passed in 6.18s ===============================
```

---

## 4. Coverage

Coverage is configured in `pytest.ini` and printed on every run:

```
addopts = -ra --strict-markers --cov=aceest --cov-report=term-missing
```

To produce a browsable HTML report:

```bash
pytest --cov=aceest --cov-report=html
# then open htmlcov/index.html
```

To enforce a quality gate (fail if coverage drops below the threshold):

```bash
pytest --cov=aceest --cov-fail-under=90
```

These artefacts (`.coverage`, `htmlcov/`) are git-ignored.

---

## 5. Test isolation strategy

Tests must never depend on each other or on a real database. This is achieved
with the **`TestingConfig`** class in `config.py`:

- It points `DATABASE` at a **unique temporary file per process**, created with
  `tempfile.mkstemp` and removed automatically at exit.
- The `app` fixture in `tests/conftest.py` **deletes every table row** before
  each test, guaranteeing a clean slate.

```python
# tests/conftest.py (excerpt)
@pytest.fixture()
def app():
    application = create_app("config.TestingConfig")
    with application.app_context():
        db = get_db()
        db.executescript("".join(f"DELETE FROM {t};" for t in _TABLES))
        db.commit()
    yield application
```

### Fixtures

| Fixture | Provides |
| --- | --- |
| `app` | A Flask app on `TestingConfig` with an empty database. |
| `client` | A Flask test client (no network required). |
| `sample_client` | A pre-inserted client row for tests that need existing data. |

### Determinism

The program generator uses randomness. Tests inject a seeded `random.Random`
instance so results are reproducible:

```python
services.generate_program("Fat Loss (FL) - 3 day", "beginner", random.Random(42))
```

---

## 6. What is validated

- **Business logic:** calorie estimation for every program, BMI classification
  bands and risk notes, and the AI-style program generator (day counts, focus
  mapping, exercise bounds, determinism).
- **Parsing helpers:** valid/invalid inputs and default fallbacks.
- **Data layer:** create/update/delete clients, cascade deletion, progress
  summaries, nested workouts/exercises, metrics, dashboard aggregates.
- **API:** status codes (`200/201/400/404`), payload shapes, computed values
  and error handling for every endpoint.
- **HTML routes:** page rendering, form submissions, redirects, flashing and
  `404` behaviour.

---

## 7. Adding a new test

1. Create or open a file matching `tests/test_*.py`.
2. Use the `client` fixture for HTTP tests, or `with app.app_context():` for
   direct repository/database tests.
3. Follow the `test_<behaviour>_<condition>` naming convention.
4. Run `pytest` and confirm coverage stays at 100%.

Example:

```python
def test_calculate_calories(client):
    response = client.post(
        "/api/calculate/calories",
        json={"weight": 82, "program": "Muscle Gain (MG) - PPL"},
    )
    assert response.status_code == 200
    assert response.get_json()["calories"] == 2870
```

---

## 8. Continuous Integration

The same command used locally is used by the pipeline (Phase 6):

```bash
pip install -r requirements-dev.txt
pytest --cov=aceest --cov-fail-under=90
```

A failing test or a coverage drop below the threshold fails the build, acting
as the automated **quality gate** for the project.

---

*ACEest Fitness & Gym — Introduction to DevOps, Assignment 1, Phase 3.*
