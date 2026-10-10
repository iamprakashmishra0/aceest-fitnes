"""Shared Pytest fixtures for the ACEest test suite.

Every test runs against an isolated SQLite database provided by
``config.TestingConfig`` (a fresh temporary file per process). The ``app``
fixture additionally wipes all tables before each test so that tests never
depend on each other's data.
"""

import pytest

from aceest import create_app
from aceest import repository as repo
from aceest.db import get_db

_TABLES = ("exercises", "workouts", "metrics", "progress", "clients")


@pytest.fixture()
def app():
    """Create a Flask app configured for testing with an empty database."""

    application = create_app("config.TestingConfig")
    with application.app_context():
        db = get_db()
        db.executescript("".join(f"DELETE FROM {table};" for table in _TABLES))
        db.commit()
    yield application


@pytest.fixture()
def client(app):
    """Return a Flask test client bound to the test app."""

    return app.test_client()


@pytest.fixture()
def sample_client(app):
    """Insert and return a single client for tests that need existing data."""

    with app.app_context():
        return repo.upsert_client(
            {
                "name": "Test Client",
                "age": 30,
                "height": 175.0,
                "weight": 70.0,
                "program": "Fat Loss (FL) - 3 day",
                "calories": 1540,
                "target_weight": 68.0,
                "target_adherence": 80,
                "membership_status": "Active",
                "membership_end": "2026-12-31",
            }
        )
