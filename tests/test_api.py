"""Integration tests for the JSON API (``aceest.routes.api``)."""


# --------------------------------------------------------------------------- #
# System / reference data
# --------------------------------------------------------------------------- #
def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "service": "aceest-fitness"}


def test_programs(client):
    response = client.get("/api/programs")
    assert response.status_code == 200
    assert "Muscle Gain (MG) - PPL" in response.get_json()


# --------------------------------------------------------------------------- #
# Clients CRUD
# --------------------------------------------------------------------------- #
def test_create_client_computes_calories(client):
    response = client.post(
        "/api/clients",
        json={"name": "Arjun", "weight": 82, "program": "Muscle Gain (MG) - PPL"},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["calories"] == 2870
    assert body["id"] is not None


def test_create_client_requires_name(client):
    response = client.post("/api/clients", json={"weight": 80})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_list_and_get_client(client, sample_client):
    listing = client.get("/api/clients")
    assert listing.status_code == 200
    assert len(listing.get_json()) == 1

    fetched = client.get(f"/api/clients/{sample_client['id']}")
    assert fetched.status_code == 200
    assert fetched.get_json()["name"] == "Test Client"


def test_get_missing_client_returns_404(client):
    assert client.get("/api/clients/424242").status_code == 404


def test_update_client(client, sample_client):
    response = client.put(
        f"/api/clients/{sample_client['id']}",
        json={"name": "Test Client", "weight": 68, "program": "Beginner (BG)"},
    )
    assert response.status_code == 200
    assert response.get_json()["weight"] == 68.0


def test_update_missing_client_returns_404(client):
    response = client.put("/api/clients/9999", json={"name": "Ghost"})
    assert response.status_code == 404


def test_delete_client(client, sample_client):
    assert client.delete(f"/api/clients/{sample_client['id']}").status_code == 200
    assert client.get(f"/api/clients/{sample_client['id']}").status_code == 404


def test_delete_missing_client_returns_404(client):
    assert client.delete("/api/clients/9999").status_code == 404


# --------------------------------------------------------------------------- #
# Progress
# --------------------------------------------------------------------------- #
def test_progress_roundtrip(client, sample_client):
    created = client.post(
        f"/api/clients/{sample_client['id']}/progress",
        json={"week": "Week 05 - 2026", "adherence": 88},
    )
    assert created.status_code == 201
    assert created.get_json()["adherence"] == 88

    listing = client.get(f"/api/clients/{sample_client['id']}/progress")
    assert len(listing.get_json()) == 1


def test_progress_missing_client_returns_404(client):
    assert client.get("/api/clients/9999/progress").status_code == 404


# --------------------------------------------------------------------------- #
# Workouts
# --------------------------------------------------------------------------- #
def test_workout_roundtrip_with_exercise(client, sample_client):
    created = client.post(
        f"/api/clients/{sample_client['id']}/workouts",
        json={
            "workout_type": "Strength",
            "duration_min": 60,
            "exercise": {"name": "Bench Press", "sets": 5, "reps": 5, "weight": 80},
        },
    )
    assert created.status_code == 201

    workouts = client.get(f"/api/clients/{sample_client['id']}/workouts").get_json()
    assert workouts[0]["exercises"][0]["name"] == "Bench Press"


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def test_metrics_roundtrip(client, sample_client):
    created = client.post(
        f"/api/clients/{sample_client['id']}/metrics",
        json={"weight": 69.5, "waist": 80, "bodyfat": 17},
    )
    assert created.status_code == 201
    assert created.get_json()["weight"] == 69.5

    metrics = client.get(f"/api/clients/{sample_client['id']}/metrics").get_json()
    assert len(metrics) == 1


# --------------------------------------------------------------------------- #
# Calculators & generator
# --------------------------------------------------------------------------- #
def test_calculate_bmi(client):
    response = client.post("/api/calculate/bmi", json={"weight": 70, "height": 175})
    assert response.status_code == 200
    assert response.get_json()["category"] == "Normal"


def test_calculate_bmi_invalid(client):
    assert client.post("/api/calculate/bmi", json={"weight": 70}).status_code == 400


def test_calculate_calories(client):
    response = client.post(
        "/api/calculate/calories",
        json={"weight": 82, "program": "Muscle Gain (MG) - PPL"},
    )
    assert response.status_code == 200
    assert response.get_json()["calories"] == 2870


def test_calculate_calories_invalid(client):
    assert client.post("/api/calculate/calories", json={"weight": 0}).status_code == 400


def test_generate_program(client):
    response = client.post(
        "/api/generate-program",
        json={"program": "Fat Loss (FL) - 3 day", "experience": "intermediate"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["focus"] == "Conditioning"
    assert len(body["schedule"]) == 4


# --------------------------------------------------------------------------- #
# Additional edge cases
# --------------------------------------------------------------------------- #
def test_update_client_requires_name(client, sample_client):
    response = client.put(f"/api/clients/{sample_client['id']}", json={"weight": 70})
    assert response.status_code == 400


def test_add_workout_ignores_non_dict_exercise(client, sample_client):
    response = client.post(
        f"/api/clients/{sample_client['id']}/workouts",
        json={"workout_type": "Cardio", "exercise": "not-a-dict"},
    )
    assert response.status_code == 201
    workouts = client.get(f"/api/clients/{sample_client['id']}/workouts").get_json()
    assert workouts[0]["exercises"] == []


def test_progress_workout_metrics_missing_client_return_404(client):
    assert client.post("/api/clients/9999/progress", json={"adherence": 50}).status_code == 404
    assert client.get("/api/clients/9999/workouts").status_code == 404
    assert client.post("/api/clients/9999/workouts", json={}).status_code == 404
    assert client.get("/api/clients/9999/metrics").status_code == 404
    assert client.post("/api/clients/9999/metrics", json={}).status_code == 404
