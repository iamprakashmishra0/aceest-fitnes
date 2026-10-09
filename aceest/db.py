"""SQLite connection handling and schema definition for ACEest.

The application uses a lightweight SQLite backend so that the whole stack stays
portable and easy to containerise. Connections are stored on Flask's ``g``
object and closed automatically at the end of each request.
"""

import sqlite3

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    name               TEXT UNIQUE NOT NULL,
    age                INTEGER,
    height             REAL,
    weight             REAL,
    program            TEXT,
    calories           INTEGER,
    target_weight      REAL,
    target_adherence   INTEGER,
    membership_status  TEXT DEFAULT 'Active',
    membership_end     TEXT,
    created_at         TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS progress (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id   INTEGER NOT NULL,
    week        TEXT,
    adherence   INTEGER,
    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS workouts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id     INTEGER NOT NULL,
    date          TEXT,
    workout_type  TEXT,
    duration_min  INTEGER,
    notes         TEXT,
    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exercises (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id  INTEGER NOT NULL,
    name        TEXT,
    sets        INTEGER,
    reps        INTEGER,
    weight      REAL,
    FOREIGN KEY (workout_id) REFERENCES workouts (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS metrics (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id   INTEGER NOT NULL,
    date        TEXT,
    weight      REAL,
    waist       REAL,
    bodyfat     REAL,
    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
);
"""


def get_db() -> sqlite3.Connection:
    """Return the request-scoped SQLite connection, creating it if needed."""

    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exc=None) -> None:
    """Close the request-scoped connection at teardown."""

    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Create the schema and seed a demo client on an empty database."""

    db = get_db()
    db.executescript(SCHEMA)
    db.commit()
    _seed(db)


def _seed(db: sqlite3.Connection) -> None:
    """Insert a single demo client the first time the database is created."""

    count = db.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    if count:
        return

    db.execute(
        """
        INSERT INTO clients
            (name, age, height, weight, program, calories,
             target_weight, target_adherence, membership_status, membership_end)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Demo Client",
            29,
            175.0,
            78.0,
            "Fat Loss (FL) - 3 day",
            1716,
            72.0,
            80,
            "Active",
            "2026-12-31",
        ),
    )
    db.execute(
        "INSERT INTO progress (client_id, week, adherence) VALUES "
        "(1, 'Week 01 - 2026', 70), (1, 'Week 02 - 2026', 85)"
    )
    db.commit()


def init_app(app) -> None:
    """Register database teardown with the application."""

    app.teardown_appcontext(close_db)
