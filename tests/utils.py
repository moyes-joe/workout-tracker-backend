from __future__ import annotations

import random
import string
from decimal import Decimal

from src import model
from src.adapters import repository


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def add_workout_plan_to_db(
    plans_repository: repository.WorkoutRepository[model.WorkoutPlan],
    user_email: str,
) -> model.WorkoutPlan:
    """Add a random workout plan to the database."""
    workout_plan_create = model.WorkoutPlanCreate(
        name=random_lower_string(),
        exercises=[
            model.ExercisePlan(name=random_lower_string(), sets=random.randint(1, 10))
            for _ in range(random.randint(1, 10))
        ],
    )
    return plans_repository.create(model=workout_plan_create, owner=user_email)


def add_workout_log_to_db(
    logs_repository: repository.WorkoutRepository[model.WorkoutLog],
    user_email: str,
) -> model.WorkoutLog:
    """Add a random workout log to the database."""
    workout_log_create = model.WorkoutLogCreate(
        name=random_lower_string(),
        plans=[
            model.ExercisePlan(
                name=random_lower_string(),
                sets=random.randint(1, 10),
            )
            for _ in range(random.randint(1, 10))
        ],
        logs=[
            model.ExerciseLog(
                name=random_lower_string(),
                sets=[
                    model.SetLog(
                        weight=Decimal(random.randint(1, 100)),
                        reps=random.randint(1, 100),
                    )
                    for _ in range(random.randint(1, 10))
                ],
            )
            for _ in range(random.randint(1, 10))
        ],
    )
    return logs_repository.create(model=workout_log_create, owner=user_email)
