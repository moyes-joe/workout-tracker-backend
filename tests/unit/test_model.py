from __future__ import annotations

from decimal import Decimal

import pytest

from src.model import (
    ExerciseLog,
    ExercisePlan,
    SetLog,
    WorkoutLog,
    WorkoutPlan,
    now_isoformat,
)


@pytest.mark.usefixtures("frozen_time")
def test_workout_plan(now_iso: str):
    name = "Leg Day"
    exercises = [ExercisePlan(name="Squats", sets=3)]

    plan = WorkoutPlan(name=name, exercises=exercises)
    assert plan.name == name
    assert plan.exercises == exercises
    assert plan.created_at == now_iso
    assert plan.id is not None


@pytest.mark.usefixtures("frozen_time")
def test_workout_log(now_iso: str):
    name = "Leg Day"
    plans = [ExercisePlan(name="Squats", sets=3)]
    logs = [ExerciseLog(name="Squats", sets=[SetLog(weight=Decimal(100), reps=10)])]
    log = WorkoutLog(
        name=name,
        plans=plans,
        logs=logs,
    )
    assert log.name == name
    assert log.plans == plans
    assert log.logs == logs
    assert log.created_at == now_iso
    assert log.id is not None


@pytest.mark.usefixtures("frozen_time")
def test_workout_log_with_id(now_iso: str):
    assert now_isoformat() == now_iso
