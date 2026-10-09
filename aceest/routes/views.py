"""Server-rendered (HTML) routes for the ACEest web UI."""

from datetime import date, datetime

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from .. import repository as repo
from .. import services
from ..utils import parse_float, parse_int, parse_str

views_bp = Blueprint("views", __name__)


def _client_form_data(form) -> dict:
    """Build a client payload from an HTML form submission."""

    name = parse_str(form.get("name"))
    program = parse_str(form.get("program"))
    weight = parse_float(form.get("weight"))
    return {
        "name": name,
        "age": parse_int(form.get("age")),
        "height": parse_float(form.get("height")),
        "weight": weight,
        "program": program,
        "calories": services.estimate_calories(weight, program),
        "target_weight": parse_float(form.get("target_weight")),
        "target_adherence": parse_int(form.get("target_adherence")),
        "membership_status": parse_str(form.get("membership_status"), "Active"),
        "membership_end": parse_str(form.get("membership_end")) or None,
    }


def _client_context(client: dict, plan: dict | None = None) -> dict:
    """Assemble everything the client-detail template needs."""

    client_id = client["id"]
    return {
        "client": client,
        "bmi": services.calculate_bmi(client.get("weight"), client.get("height")),
        "progress": repo.list_progress(client_id),
        "progress_summary": repo.progress_summary(client_id),
        "workouts": repo.list_workouts(client_id),
        "metrics": repo.list_metrics(client_id),
        "latest_metrics": repo.latest_metrics(client_id),
        "programs": services.get_programs(),
        "plan": plan,
    }


@views_bp.route("/")
def index():
    """Dashboard with aggregate stats and the client roster."""

    return render_template(
        "index.html",
        stats=repo.dashboard_stats(),
        clients=repo.list_clients(),
        programs=services.get_programs(),
    )


@views_bp.route("/clients")
def clients():
    """Client directory with an inline registration form."""

    return render_template(
        "clients.html",
        clients=repo.list_clients(),
        programs=services.get_programs(),
    )


@views_bp.route("/clients", methods=["POST"])
def create_client():
    """Create or update a client from the directory form."""

    data = _client_form_data(request.form)
    if not data["name"]:
        flash("Client name is required.", "error")
        return redirect(url_for("views.clients"))

    client = repo.upsert_client(data)
    flash(f"Client '{client['name']}' saved.", "success")
    return redirect(url_for("views.client_detail", client_id=client["id"]))


@views_bp.route("/clients/<int:client_id>")
def client_detail(client_id: int):
    """Detailed profile page for a single client."""

    client = repo.get_client(client_id)
    if not client:
        abort(404)
    return render_template("client_detail.html", **_client_context(client))


@views_bp.route("/clients/<int:client_id>/update", methods=["POST"])
def update_client(client_id: int):
    """Update an existing client's profile."""

    client = repo.get_client(client_id)
    if not client:
        abort(404)

    data = _client_form_data(request.form)
    if not data["name"]:
        data["name"] = client["name"]
    repo.upsert_client(data)
    flash("Client profile updated.", "success")
    return redirect(url_for("views.client_detail", client_id=client_id))


@views_bp.route("/clients/<int:client_id>/delete", methods=["POST"])
def delete_client(client_id: int):
    """Remove a client and all associated records."""

    repo.delete_client(client_id)
    flash("Client deleted.", "success")
    return redirect(url_for("views.clients"))


@views_bp.route("/clients/<int:client_id>/progress", methods=["POST"])
def add_progress(client_id: int):
    """Log a weekly adherence value."""

    if not repo.get_client(client_id):
        abort(404)

    week = request.form.get("week") or datetime.now().strftime("Week %U - %Y")
    adherence = parse_int(request.form.get("adherence"), 0)
    repo.add_progress(client_id, week, adherence)
    flash("Weekly progress logged.", "success")
    return redirect(url_for("views.client_detail", client_id=client_id))


@views_bp.route("/clients/<int:client_id>/workouts", methods=["POST"])
def add_workout(client_id: int):
    """Log a workout and an optional exercise."""

    if not repo.get_client(client_id):
        abort(404)

    exercise_name = parse_str(request.form.get("exercise_name"))
    exercise = None
    if exercise_name:
        exercise = {
            "name": exercise_name,
            "sets": parse_int(request.form.get("sets")),
            "reps": parse_int(request.form.get("reps")),
            "weight": parse_float(request.form.get("exercise_weight")),
        }

    repo.add_workout(
        client_id=client_id,
        date=parse_str(request.form.get("date"), date.today().isoformat()),
        workout_type=parse_str(request.form.get("workout_type"), "Strength"),
        duration_min=parse_int(request.form.get("duration_min")),
        notes=parse_str(request.form.get("notes")) or None,
        exercise=exercise,
    )
    flash("Workout logged.", "success")
    return redirect(url_for("views.client_detail", client_id=client_id))


@views_bp.route("/clients/<int:client_id>/metrics", methods=["POST"])
def add_metrics(client_id: int):
    """Log body metrics (weight, waist, body-fat)."""

    if not repo.get_client(client_id):
        abort(404)

    repo.add_metrics(
        client_id=client_id,
        date=parse_str(request.form.get("date"), date.today().isoformat()),
        weight=parse_float(request.form.get("weight")),
        waist=parse_float(request.form.get("waist")),
        bodyfat=parse_float(request.form.get("bodyfat")),
    )
    flash("Body metrics logged.", "success")
    return redirect(url_for("views.client_detail", client_id=client_id))


@views_bp.route("/clients/<int:client_id>/generate", methods=["POST"])
def generate_program(client_id: int):
    """Generate an AI-style workout plan and render it inline."""

    client = repo.get_client(client_id)
    if not client:
        abort(404)

    experience = parse_str(request.form.get("experience"), "beginner").lower()
    plan = services.generate_program(client.get("program"), experience)
    flash(f"Generated a {experience} plan for {client['name']}.", "success")
    return render_template("client_detail.html", **_client_context(client, plan=plan))


@views_bp.route("/programs")
def programs():
    """Static catalogue of training programs and their calorie factors."""

    return render_template("programs.html", programs=services.get_programs())
