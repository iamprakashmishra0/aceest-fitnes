"""Tests for database initialisation and seeding (``aceest.db``)."""

from aceest import db as db_module
from aceest.db import get_db

_EXPECTED_TABLES = {"clients", "progress", "workouts", "exercises", "metrics"}


def test_init_db_creates_all_tables(app):
    with app.app_context():
        rows = get_db().execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
        assert _EXPECTED_TABLES.issubset({row[0] for row in rows})


def test_seed_creates_demo_client_when_empty(app):
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM clients")
        db.commit()

        db_module.init_db()

        demo = db.execute("SELECT * FROM clients WHERE name = 'Demo Client'").fetchone()
        assert demo is not None

        linked = db.execute(
            "SELECT COUNT(*) FROM progress WHERE client_id = ?", (demo["id"],)
        ).fetchone()[0]
        assert linked == 2


def test_seed_is_idempotent(app):
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM clients")
        db.commit()

        db_module.init_db()
        db_module.init_db()

        count = db.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        assert count == 1
