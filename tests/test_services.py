"""Unit tests for the pure business logic in ``aceest.services``.

These tests need no Flask app or database, which proves the domain logic is
decoupled from the framework.
"""

import random

import pytest

from aceest import services


# --------------------------------------------------------------------------- #
# Programs
# --------------------------------------------------------------------------- #
def test_get_programs_returns_full_catalogue():
    programs = services.get_programs()
    assert set(programs) == {
        "Fat Loss (FL) - 3 day",
        "Fat Loss (FL) - 5 day",
        "Muscle Gain (MG) - PPL",
        "Beginner (BG)",
    }


def test_get_program_returns_definition():
    program = services.get_program("Muscle Gain (MG) - PPL")
    assert program["factor"] == 35
    assert program["focus"] == "Hypertrophy"


def test_get_program_unknown_returns_none():
    assert services.get_program("Nonexistent") is None


# --------------------------------------------------------------------------- #
# Calorie estimation
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("weight", "program", "expected"),
    [
        (82, "Muscle Gain (MG) - PPL", 2870),
        (70, "Fat Loss (FL) - 3 day", 1540),
        (60, "Fat Loss (FL) - 5 day", 1440),
        (50, "Beginner (BG)", 1300),
    ],
)
def test_estimate_calories(weight, program, expected):
    assert services.estimate_calories(weight, program) == expected


def test_estimate_calories_rounds_to_nearest_int():
    assert services.estimate_calories(70.4, "Fat Loss (FL) - 3 day") == round(70.4 * 22)


@pytest.mark.parametrize("weight", [None, 0])
def test_estimate_calories_missing_weight_returns_none(weight):
    assert services.estimate_calories(weight, "Beginner (BG)") is None


def test_estimate_calories_unknown_program_returns_none():
    assert services.estimate_calories(80, "Unknown") is None


# --------------------------------------------------------------------------- #
# BMI
# --------------------------------------------------------------------------- #
def test_calculate_bmi_normal():
    result = services.calculate_bmi(70, 175)
    assert result["bmi"] == 22.9
    assert result["category"] == "Normal"
    assert "risk" in result


@pytest.mark.parametrize(
    ("weight", "height", "category"),
    [
        (50, 175, "Underweight"),
        (70, 175, "Normal"),
        (85, 175, "Overweight"),
        (100, 175, "Obese"),
    ],
)
def test_calculate_bmi_categories(weight, height, category):
    assert services.calculate_bmi(weight, height)["category"] == category


@pytest.mark.parametrize(
    ("weight", "height"),
    [(None, 175), (70, None), (70, 0), (0, 175)],
)
def test_calculate_bmi_invalid_inputs_return_none(weight, height):
    assert services.calculate_bmi(weight, height) is None


# --------------------------------------------------------------------------- #
# Program generator
# --------------------------------------------------------------------------- #
def test_generate_program_is_deterministic_with_seed():
    first = services.generate_program("Fat Loss (FL) - 3 day", "beginner", random.Random(42))
    second = services.generate_program("Fat Loss (FL) - 3 day", "beginner", random.Random(42))
    assert first == second


@pytest.mark.parametrize(
    ("experience", "days"),
    [("beginner", 3), ("intermediate", 4), ("advanced", 5)],
)
def test_generate_program_day_count_by_experience(experience, days):
    plan = services.generate_program("Beginner (BG)", experience, random.Random(1))
    assert len(plan["schedule"]) == days


def test_generate_program_unknown_experience_defaults_to_beginner():
    plan = services.generate_program("Beginner (BG)", "expert", random.Random(1))
    assert plan["experience"] == "beginner"
    assert len(plan["schedule"]) == 3


@pytest.mark.parametrize(
    ("program", "focus"),
    [
        ("Fat Loss (FL) - 3 day", "Conditioning"),
        ("Muscle Gain (MG) - PPL", "Hypertrophy"),
        ("Beginner (BG)", "Full Body"),
        (None, "Full Body"),
    ],
)
def test_generate_program_focus_mapping(program, focus):
    plan = services.generate_program(program, "beginner", random.Random(7))
    assert plan["focus"] == focus


def test_generate_program_exercise_shape_and_bounds():
    plan = services.generate_program("Muscle Gain (MG) - PPL", "intermediate", random.Random(3))
    assert plan["program"] == "Muscle Gain (MG) - PPL"
    for day in plan["schedule"]:
        assert day["day"] in {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
        assert 3 <= len(day["exercises"]) <= 4
        for exercise in day["exercises"]:
            assert exercise["name"] in services.EXERCISE_POOL["Hypertrophy"]
            assert 3 <= exercise["sets"] <= 4
            assert 8 <= exercise["reps"] <= 15
