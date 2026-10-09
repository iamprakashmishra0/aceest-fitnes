"""Data-access layer (repository) for ACEest Fitness & Gym.

All SQL lives here so that the route handlers stay thin and the persistence
concerns are isolated from the HTTP concerns. Every function returns plain
dictionaries, never sqlite3 rows, which keeps the API layer JSON-friendly.
"""

from .db import get_db

_CLIENT_COLUMNS = (
    "name",
    "age",
    "height",
    "weight",
    "program",
    "calories",
    "target_weight",
    "target_adherence",
    "membership_status",
    "membership_end",
)


# --------------------------------------------------------------------------- #
# Clients
# --------------------------------------------------------------------------- #
def list_clients() -> list[dict]:
    """Return every client ordered by name."""

    rows = get_db().execute("SELECT * FROM clients ORDER BY name").fetchall()
    return [dict(row) for row in rows]


def get_client(client_id: int) -> dict | None:
    """Return a single client by primary key."""

    row = get_db().execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    return dict(row) if row else None


def upsert_client(data: dict) -> dict:
    """Insert a new client or update the existing one sharing the same name."""

    db = get_db()
    values = tuple(data.get(column) for column in _CLIENT_COLUMNS)
    db.execute(
        """
        INSERT INTO clients
            (name, age, height, weight, program, calories,
             target_weight, target_adherence, membership_status, membership_end)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            age               = excluded.age,
            height            = excluded.height,
            weight            = excluded.weight,
            program           = excluded.program,
            calories          = excluded.calories,
            target_weight     = excluded.target_weight,
            target_adherence  = excluded.target_adherence,
            membership_status = excluded.membership_status,
            membership_end    = excluded.membership_end
        """,
        values,
    )
    db.commit()
    row = db.execute("SELECT * FROM clients WHERE name = ?", (data.get("name"),)).fetchone()
    return dict(row)


def delete_client(client_id: int) -> bool:
    """Delete a client (cascading to child rows). Returns ``True`` if removed."""

    db = get_db()
    cur = db.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    db.commit()
    return cur.rowcount > 0


# --------------------------------------------------------------------------- #
# Progress
# --------------------------------------------------------------------------- #
def add_progress(client_id: int, week: str, adherence: int) -> dict:
    """Record a weekly adherence entry."""

    db = get_db()
    cur = db.execute(
        "INSERT INTO progress (client_id, week, adherence) VALUES (?, ?, ?)",
        (client_id, week, adherence),
    )
    db.commit()
    row = db.execute("SELECT * FROM progress WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


def list_progress(client_id: int) -> list[dict]:
    """Return all weekly adherence entries for a client."""

    rows = get_db().execute(
        "SELECT * FROM progress WHERE client_id = ? ORDER BY id", (client_id,)
    ).fetchall()
    return [dict(row) for row in rows]


def progress_summary(client_id: int) -> dict:
    """Return the number of logged weeks and the average adherence."""

    row = get_db().execute(
        "SELECT COUNT(*), AVG(adherence) FROM progress WHERE client_id = ?",
        (client_id,),
    ).fetchone()
    weeks, average = row[0], row[1]
    return {
        "weeks": weeks or 0,
        "avg_adherence": round(average, 1) if average is not None else 0,
    }


# --------------------------------------------------------------------------- #
# Workouts & exercises
# --------------------------------------------------------------------------- #
def add_workout(
    client_id: int,
    date: str,
    workout_type: str,
    duration_min: int | None = None,
    notes: str | None = None,
    exercise: dict | None = None,
) -> int:
    """Log a workout, optionally with a single exercise entry."""

    db = get_db()
    cur = db.execute(
        """
        INSERT INTO workouts (client_id, date, workout_type, duration_min, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (client_id, date, workout_type, duration_min, notes),
    )
    workout_id = cur.lastrowid

    if exercise and exercise.get("name"):
        db.execute(
            """
            INSERT INTO exercises (workout_id, name, sets, reps, weight)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                workout_id,
                exercise.get("name"),
                exercise.get("sets"),
                exercise.get("reps"),
                exercise.get("weight"),
            ),
        )

    db.commit()
    return workout_id


def list_workouts(client_id: int) -> list[dict]:
    """Return a client's workouts with their nested exercises."""

    db = get_db()
    rows = db.execute(
        "SELECT * FROM workouts WHERE client_id = ? ORDER BY date DESC, id DESC",
        (client_id,),
    ).fetchall()

    workouts = []
    for row in rows:
        workout = dict(row)
        exercise_rows = db.execute(
            "SELECT name, sets, reps, weight FROM exercises WHERE workout_id = ? ORDER BY id",
            (workout["id"],),
        ).fetchall()
        workout["exercises"] = [dict(exercise) for exercise in exercise_rows]
        workouts.append(workout)
    return workouts


# --------------------------------------------------------------------------- #
# Body metrics
# --------------------------------------------------------------------------- #
def add_metrics(
    client_id: int,
    date: str,
    weight: float | None = None,
    waist: float | None = None,
    bodyfat: float | None = None,
) -> dict:
    """Record a body-metrics measurement."""

    db = get_db()
    cur = db.execute(
        """
        INSERT INTO metrics (client_id, date, weight, waist, bodyfat)
        VALUES (?, ?, ?, ?, ?)
        """,
        (client_id, date, weight, waist, bodyfat),
    )
    db.commit()
    row = db.execute("SELECT * FROM metrics WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


def list_metrics(client_id: int) -> list[dict]:
    """Return all body-metrics records for a client, newest first."""

    rows = get_db().execute(
        "SELECT * FROM metrics WHERE client_id = ? ORDER BY date DESC, id DESC",
        (client_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def latest_metrics(client_id: int) -> dict | None:
    """Return the most recent body-metrics record for a client."""

    row = get_db().execute(
        "SELECT * FROM metrics WHERE client_id = ? ORDER BY date DESC, id DESC LIMIT 1",
        (client_id,),
    ).fetchone()
    return dict(row) if row else None


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #
def dashboard_stats() -> dict:
    """Return aggregate counters used by the dashboard."""

    db = get_db()
    clients = db.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    workouts = db.execute("SELECT COUNT(*) FROM workouts").fetchone()[0]
    average = db.execute("SELECT AVG(adherence) FROM progress").fetchone()[0]
    return {
        "clients": clients or 0,
        "workouts": workouts or 0,
        "avg_adherence": round(average, 1) if average is not None else 0,
    }
