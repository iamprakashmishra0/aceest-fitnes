"""Tests for the data-access layer (``aceest.repository``)."""

from aceest import repository as repo
from aceest.db import get_db


def _new_client(name="Repo Client", **overrides):
    data = {
        "name": name,
        "age": 28,
        "height": 180.0,
        "weight": 75.0,
        "program": "Muscle Gain (MG) - PPL",
        "calories": 2625,
        "target_weight": 80.0,
        "target_adherence": 90,
        "membership_status": "Active",
        "membership_end": "2026-06-30",
    }
    data.update(overrides)
    return data


# --------------------------------------------------------------------------- #
# Clients
# --------------------------------------------------------------------------- #
def test_upsert_creates_client(app):
    with app.app_context():
        created = repo.upsert_client(_new_client())
        assert created["id"] is not None
        assert created["name"] == "Repo Client"
        assert repo.get_client(created["id"])["weight"] == 75.0


def test_upsert_updates_existing_client_by_name(app):
    with app.app_context():
        created = repo.upsert_client(_new_client())
        updated = repo.upsert_client(_new_client(weight=78.0))
        assert updated["id"] == created["id"]
        assert updated["weight"] == 78.0
        assert len(repo.list_clients()) == 1


def test_get_client_missing_returns_none(app):
    with app.app_context():
        assert repo.get_client(99999) is None


def test_list_clients_is_sorted_by_name(app):
    with app.app_context():
        repo.upsert_client(_new_client(name="Zara"))
        repo.upsert_client(_new_client(name="Amit"))
        assert [c["name"] for c in repo.list_clients()] == ["Amit", "Zara"]


def test_delete_client_returns_false_for_missing(app):
    with app.app_context():
        assert repo.delete_client(12345) is False


def test_delete_client_cascades_to_children(app):
    with app.app_context():
        client = repo.upsert_client(_new_client())
        repo.add_progress(client["id"], "Week 01 - 2026", 50)
        repo.add_metrics(client["id"], "2026-01-10", weight=75.0)

        assert repo.delete_client(client["id"]) is True
        assert repo.get_client(client["id"]) is None

        db = get_db()
        assert db.execute("SELECT COUNT(*) FROM progress").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM metrics").fetchone()[0] == 0


# --------------------------------------------------------------------------- #
# Progress
# --------------------------------------------------------------------------- #
def test_progress_summary_average_and_count(app):
    with app.app_context():
        client = repo.upsert_client(_new_client())
        repo.add_progress(client["id"], "Week 01 - 2026", 80)
        repo.add_progress(client["id"], "Week 02 - 2026", 90)

        entries = repo.list_progress(client["id"])
        assert len(entries) == 2

        summary = repo.progress_summary(client["id"])
        assert summary["weeks"] == 2
        assert summary["avg_adherence"] == 85.0


def test_progress_summary_empty(app):
    with app.app_context():
        client = repo.upsert_client(_new_client())
        assert repo.progress_summary(client["id"]) == {"weeks": 0, "avg_adherence": 0}


# --------------------------------------------------------------------------- #
# Workouts & exercises
# --------------------------------------------------------------------------- #
def test_add_workout_with_exercise(app):
    with app.app_context():
        client = repo.upsert_client(_new_client())
        repo.add_workout(
            client["id"],
            date="2026-02-01",
            workout_type="Strength",
            duration_min=60,
            notes="Solid session",
            exercise={"name": "Squat", "sets": 5, "reps": 5, "weight": 100.0},
        )

        workouts = repo.list_workouts(client["id"])
        assert len(workouts) == 1
        assert workouts[0]["workout_type"] == "Strength"
        assert workouts[0]["exercises"] == [
            {"name": "Squat", "sets": 5, "reps": 5, "weight": 100.0}
        ]


def test_add_workout_without_exercise(app):
    with app.app_context():
        client = repo.upsert_client(_new_client())
        repo.add_workout(client["id"], date="2026-02-02", workout_type="Cardio")
        assert repo.list_workouts(client["id"])[0]["exercises"] == []


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def test_add_and_latest_metrics(app):
    with app.app_context():
        client = repo.upsert_client(_new_client())
        repo.add_metrics(client["id"], "2026-01-01", weight=76.0, waist=85.0, bodyfat=20.0)
        repo.add_metrics(client["id"], "2026-02-01", weight=74.0, waist=83.0, bodyfat=18.0)

        latest = repo.latest_metrics(client["id"])
        assert latest["weight"] == 74.0
        assert len(repo.list_metrics(client["id"])) == 2


def test_latest_metrics_empty(app):
    with app.app_context():
        client = repo.upsert_client(_new_client())
        assert repo.latest_metrics(client["id"]) is None


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #
def test_dashboard_stats(app):
    with app.app_context():
        client = repo.upsert_client(_new_client())
        repo.add_progress(client["id"], "Week 01 - 2026", 60)
        repo.add_workout(client["id"], date="2026-03-01", workout_type="Strength")

        stats = repo.dashboard_stats()
        assert stats == {"clients": 1, "workouts": 1, "avg_adherence": 60.0}
