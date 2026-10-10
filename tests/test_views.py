"""Tests for the server-rendered HTML routes (``aceest.routes.views``)."""


def _client_form(name="UI Client", program="Beginner (BG)"):
    return {
        "name": name,
        "age": 25,
        "height": 170,
        "weight": 65,
        "program": program,
        "target_weight": 60,
        "target_adherence": 75,
        "membership_status": "Active",
        "membership_end": "2026-09-30",
    }


# --------------------------------------------------------------------------- #
# Static pages
# --------------------------------------------------------------------------- #
def test_dashboard(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Client Roster" in response.data


def test_clients_page(client):
    assert client.get("/clients").status_code == 200


def test_programs_page(client):
    response = client.get("/programs")
    assert response.status_code == 200
    assert b"Fat Loss (FL) - 3 day" in response.data


# --------------------------------------------------------------------------- #
# Client create / update / delete
# --------------------------------------------------------------------------- #
def test_create_client_via_form(client):
    response = client.post("/clients", data=_client_form(), follow_redirects=True)
    assert response.status_code == 200
    assert b"UI Client" in response.data


def test_create_client_requires_name(client):
    response = client.post("/clients", data={"name": ""}, follow_redirects=True)
    assert response.status_code == 200
    assert b"required" in response.data


def test_client_detail(client, sample_client):
    response = client.get(f"/clients/{sample_client['id']}")
    assert response.status_code == 200
    assert b"Test Client" in response.data


def test_client_detail_missing_returns_404(client):
    assert client.get("/clients/9999").status_code == 404


def test_update_client_via_form(client, sample_client):
    form = _client_form(name="Test Client")
    form["weight"] = 66
    response = client.post(
        f"/clients/{sample_client['id']}/update", data=form, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"updated" in response.data


def test_delete_client_via_form(client, sample_client):
    response = client.post(
        f"/clients/{sample_client['id']}/delete", follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Test Client" not in response.data


# --------------------------------------------------------------------------- #
# Progress / workouts / metrics forms
# --------------------------------------------------------------------------- #
def test_log_progress_via_form(client, sample_client):
    response = client.post(
        f"/clients/{sample_client['id']}/progress",
        data={"week": "Week 09 - 2026", "adherence": 95},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Week 09 - 2026" in response.data


def test_log_workout_via_form(client, sample_client):
    response = client.post(
        f"/clients/{sample_client['id']}/workouts",
        data={
            "date": "2026-04-01",
            "workout_type": "Strength",
            "duration_min": 45,
            "notes": "Good",
            "exercise_name": "Deadlift",
            "sets": 4,
            "reps": 6,
            "exercise_weight": 120,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Deadlift" in response.data


def test_log_metrics_via_form(client, sample_client):
    response = client.post(
        f"/clients/{sample_client['id']}/metrics",
        data={"date": "2026-04-02", "weight": 64.5, "waist": 78, "bodyfat": 16},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"64.5" in response.data


# --------------------------------------------------------------------------- #
# Program generator
# --------------------------------------------------------------------------- #
def test_generate_program_view(client, sample_client):
    response = client.post(
        f"/clients/{sample_client['id']}/generate",
        data={"experience": "beginner"},
    )
    assert response.status_code == 200
    assert b"Conditioning" in response.data


# --------------------------------------------------------------------------- #
# Edge cases / missing clients
# --------------------------------------------------------------------------- #
def test_update_client_blank_name_keeps_existing(client, sample_client):
    response = client.post(
        f"/clients/{sample_client['id']}/update",
        data={"name": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Test Client" in response.data


def test_missing_client_views_return_404(client):
    assert client.post("/clients/9999/update", data={"name": "x"}).status_code == 404
    assert client.post("/clients/9999/progress", data={}).status_code == 404
    assert client.post("/clients/9999/workouts", data={}).status_code == 404
    assert client.post("/clients/9999/metrics", data={}).status_code == 404
    assert client.post("/clients/9999/generate", data={}).status_code == 404
