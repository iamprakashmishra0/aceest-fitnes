"""Core business logic for ACEest Fitness & Gym.

Every function in this module is a *pure* function: it takes plain Python
values and returns plain Python values with no database or framework
dependency. This makes the logic trivially unit-testable with Pytest in the
later phases of the assignment.
"""

import random

#: Program catalogue derived from the ACEest baseline application.
PROGRAMS = {
    "Fat Loss (FL) - 3 day": {
        "factor": 22,
        "focus": "Conditioning",
        "desc": "3-day full-body fat loss",
    },
    "Fat Loss (FL) - 5 day": {
        "factor": 24,
        "focus": "Conditioning",
        "desc": "5-day split, higher volume fat loss",
    },
    "Muscle Gain (MG) - PPL": {
        "factor": 35,
        "focus": "Hypertrophy",
        "desc": "Push/Pull/Legs hypertrophy",
    },
    "Beginner (BG)": {
        "factor": 26,
        "focus": "Full Body",
        "desc": "3-day simple beginner full-body",
    },
}

#: Exercise pool used by the AI-style program generator.
EXERCISE_POOL = {
    "Strength": [
        "Squat",
        "Deadlift",
        "Bench Press",
        "Overhead Press",
        "Pull-Up",
        "Barbell Row",
    ],
    "Hypertrophy": [
        "Leg Press",
        "Incline Dumbbell Press",
        "Lat Pulldown",
        "Lateral Raise",
        "Bicep Curl",
        "Tricep Extension",
    ],
    "Conditioning": [
        "Running",
        "Cycling",
        "Rowing",
        "Burpees",
        "Jump Rope",
        "Kettlebell Swings",
    ],
    "Full Body": [
        "Push-Up",
        "Pull-Up",
        "Lunge",
        "Plank",
        "Dumbbell Row",
        "Dumbbell Press",
    ],
}

_EXPERIENCE_PRESETS = {
    "beginner": {"sets": (2, 3), "reps": (8, 12), "days": 3},
    "intermediate": {"sets": (3, 4), "reps": (8, 15), "days": 4},
    "advanced": {"sets": (4, 5), "reps": (6, 15), "days": 5},
}

_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def get_programs() -> dict:
    """Return the full program catalogue."""

    return PROGRAMS


def get_program(name: str) -> dict | None:
    """Return a single program definition or ``None`` if unknown."""

    return PROGRAMS.get(name)


def estimate_calories(weight_kg: float | None, program_name: str) -> int | None:
    """Estimate daily calories as ``weight * program factor``.

    Returns ``None`` when the weight or program is missing.
    """

    program = get_program(program_name)
    if not program or not weight_kg:
        return None
    return int(round(weight_kg * program["factor"]))


def _bmi_band(bmi: float) -> tuple[str, str]:
    """Return the ``(category, risk)`` pair for a BMI value."""

    if bmi < 18.5:
        return "Underweight", "Potential nutrient deficiency and low energy."
    if bmi < 25:
        return "Normal", "Low risk if active and strong."
    if bmi < 30:
        return "Overweight", "Moderate risk; focus on adherence and progressive activity."
    return "Obese", "Higher risk; prioritise fat loss, consistency and supervision."


def calculate_bmi(weight_kg: float | None, height_cm: float | None) -> dict | None:
    """Calculate BMI and return it with a category and risk note.

    Returns ``None`` when the inputs are missing or invalid.
    """

    if not weight_kg or not height_cm or height_cm <= 0:
        return None

    meters = height_cm / 100.0
    bmi = round(weight_kg / (meters * meters), 1)
    category, risk = _bmi_band(bmi)
    return {"bmi": bmi, "category": category, "risk": risk}


def generate_program(
    program_name: str | None,
    experience: str = "beginner",
    rng: random.Random | None = None,
) -> dict:
    """Generate a weekly workout plan for a client.

    Args:
        program_name: The client's program (drives the training focus).
        experience: One of ``beginner``, ``intermediate`` or ``advanced``.
        rng: Optional random source, injected so tests are deterministic.

    Returns:
        A dictionary describing the generated schedule.
    """

    rng = rng or random
    experience = (experience or "beginner").lower()
    preset = _EXPERIENCE_PRESETS.get(experience, _EXPERIENCE_PRESETS["beginner"])

    focus = _focus_for(program_name)
    pool = EXERCISE_POOL[focus]
    days = _WEEKDAYS[: preset["days"]]
    exercises_per_day = min(4 if preset["days"] >= 4 else 3, len(pool))

    schedule = []
    for day in days:
        picks = rng.sample(pool, k=exercises_per_day)
        schedule.append(
            {
                "day": day,
                "exercises": [
                    {
                        "name": exercise,
                        "sets": rng.randint(*preset["sets"]),
                        "reps": rng.randint(*preset["reps"]),
                    }
                    for exercise in picks
                ],
            }
        )

    return {
        "program": program_name,
        "experience": experience,
        "focus": focus,
        "schedule": schedule,
    }


def _focus_for(program_name: str | None) -> str:
    """Map a program name to a training focus / exercise pool key."""

    name = (program_name or "").lower()
    if "fat" in name:
        return "Conditioning"
    if "muscle" in name:
        return "Hypertrophy"
    return "Full Body"
