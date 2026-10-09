"""JSON API endpoints for ACEest Fitness & Gym.

These endpoints form the machine-readable surface that CI/CD smoke tests and
future clients (mobile apps, dashboards) can consume. They accept either JSON
bodies or form-encoded data.
"""

from datetime import date, datetime

from flask import Blueprint, jsonify, request

from .. import repository as repo
from .. import services
from ..utils import parse_float, parse_int, parse_str

api_bp = Blueprint("api", __name__)


def _payload() -> dict:
    """Return the request body as a dictionary (JSON or form data)."""

    return request.get_json(silent=True) or request.form.to_dict()


def _client_from_payload(payload: dict) -> dict:
    """Map an API payload to a client record."""

    program = parse_str(payload.get("program"))
    weight = parse_float(payload.get("weight"))
    return {
        "name": parse_str(payload.get("name")),
        "age": parse_int(payload.get("age")),
        "height": parse_float(payload.get("height")),
        "weight": weight,
        "program": program,
        "calories": services.estimate_calories(weight, program),
        "target_weight": parse_float(payload.get("target_weight")),
        "target_adherence": parse_int(payload.get("target_adherence")),
        "membership_status": parse_str(payload.get("membership_status"), "Active"),
        "membership_end": parse_str(payload.get("membership_end")) or None,
    }


# --------------------------------------------------------------------------- #
# System / reference data
# --------------------------------------------------------------------------- #
@api_bp.get("/health")
def health():
    """Liveness probe used by the pipeline."""

    return jsonify({"status": "ok", "service": "aceest-fitness"})


@api_bp.get("/programs")
def programs():
    """Return the program catalogue."""

    return jsonify(services.get_programs())


# --------------------------------------------------------------------------- #
# Clients
# --------------------------------------------------------------------------- #
@api_bp.get("/clients")
def list_clients():
    """Return all clients."""

    return jsonify(repo.list_clients())


@api_bp.post("/clients")
def create_client():
    """Create or update a client."""

    data = _client_from_payload(_payload())
    if not data["name"]:
        return jsonify({"error": "name is required"}), 400
    return jsonify(repo.upsert_client(data)), 201


@api_bp.get("/clients/<int:client_id>")
def get_client(client_id: int):
    """Return one client."""

    client = repo.get_client(client_id)
    if not client:
        return jsonify({"error": "client not found"}), 404
    return jsonify(client)


@api_bp.put("/clients/<int:client_id>")
def update_client(client_id: int):
    """Update an existing client."""

    if not repo.get_client(client_id):
        return jsonify({"error": "client not found"}), 404

    data = _client_from_payload(_payload())
    if not data["name"]:
        return jsonify({"error": "name is required"}), 400
    return jsonify(repo.upsert_client(data))


@api_bp.delete("/clients/<int:client_id>")
def delete_client(client_id: int):
    """Delete a client."""

    if not repo.delete_client(client_id):
        return jsonify({"error": "client not found"}), 404
    return jsonify({"deleted": client_id})


# --------------------------------------------------------------------------- #
# Progress
# --------------------------------------------------------------------------- #
@api_bp.get("/clients/<int:client_id>/progress")
def list_progress(client_id: int):
    """Return a client's weekly adherence history."""

    if not repo.get_client(client_id):
        return jsonify({"error": "client not found"}), 404
    return jsonify(repo.list_progress(client_id))


@api_bp.post("/clients/<int:client_id>/progress")
def add_progress(client_id: int):
    """Log a weekly adherence entry."""

    if not repo.get_client(client_id):
        return jsonify({"error": "client not found"}), 404

    payload = _payload()
    week = parse_str(payload.get("week")) or datetime.now().strftime("Week %U - %Y")
    adherence = parse_int(payload.get("adherence"), 0)
    return jsonify(repo.add_progress(client_id, week, adherence)), 201


# --------------------------------------------------------------------------- #
# Workouts
# --------------------------------------------------------------------------- #
@api_bp.get("/clients/<int:client_id>/workouts")
def list_workouts(client_id: int):
    """Return a client's workouts with nested exercises."""

    if not repo.get_client(client_id):
        return jsonify({"error": "client not found"}), 404
    return jsonify(repo.list_workouts(client_id))


@api_bp.post("/clients/<int:client_id>/workouts")
def add_workout(client_id: int):
    """Log a workout."""

    if not repo.get_client(client_id):
        return jsonify({"error": "client not found"}), 404

    payload = _payload()
    exercise = payload.get("exercise")
    if not isinstance(exercise, dict):
        exercise = None

    workout_id = repo.add_workout(
        client_id=client_id,
        date=parse_str(payload.get("date"), date.today().isoformat()),
        workout_type=parse_str(payload.get("workout_type"), "Strength"),
        duration_min=parse_int(payload.get("duration_min")),
        notes=parse_str(payload.get("notes")) or None,
        exercise=exercise,
    )
    return jsonify({"id": workout_id}), 201


# --------------------------------------------------------------------------- #
# Body metrics
# --------------------------------------------------------------------------- #
@api_bp.get("/clients/<int:client_id>/metrics")
def list_metrics(client_id: int):
    """Return a client's body-metrics history."""

    if not repo.get_client(client_id):
        return jsonify({"error": "client not found"}), 404
    return jsonify(repo.list_metrics(client_id))


@api_bp.post("/clients/<int:client_id>/metrics")
def add_metrics(client_id: int):
    """Log body metrics."""

    if not repo.get_client(client_id):
        return jsonify({"error": "client not found"}), 404

    payload = _payload()
    return (
        jsonify(
            repo.add_metrics(
                client_id=client_id,
                date=parse_str(payload.get("date"), date.today().isoformat()),
                weight=parse_float(payload.get("weight")),
                waist=parse_float(payload.get("waist")),
                bodyfat=parse_float(payload.get("bodyfat")),
            )
        ),
        201,
    )


# --------------------------------------------------------------------------- #
# Calculators & generator
# --------------------------------------------------------------------------- #
@api_bp.post("/calculate/bmi")
def calculate_bmi():
    """Calculate BMI from weight (kg) and height (cm)."""

    payload = _payload()
    result = services.calculate_bmi(
        parse_float(payload.get("weight")), parse_float(payload.get("height"))
    )
    if not result:
        return jsonify({"error": "valid weight and height are required"}), 400
    return jsonify(result)


@api_bp.post("/calculate/calories")
def calculate_calories():
    """Estimate daily calories from weight (kg) and program name."""

    payload = _payload()
    calories = services.estimate_calories(
        parse_float(payload.get("weight")), parse_str(payload.get("program"))
    )
    if calories is None:
        return jsonify({"error": "valid weight and program are required"}), 400
    return jsonify({"calories": calories})


@api_bp.post("/generate-program")
def generate_program():
    """Generate an AI-style weekly workout plan."""

    payload = _payload()
    experience = parse_str(payload.get("experience"), "beginner").lower()
    return jsonify(
        services.generate_program(parse_str(payload.get("program")), experience)
    )
