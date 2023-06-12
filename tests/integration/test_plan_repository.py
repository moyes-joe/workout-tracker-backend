from __future__ import annotations

import pytest

from src import model
from src.adapters import repository
from tests.utils import add_workout_plan_to_db


@pytest.mark.usefixtures("frozen_time")
def test_create_workout_plan(
    plans_repository: repository.DynamoDBWorkoutPlanRepository,
    user_email: str,
    now_iso: str,
) -> None:
    """
    GIVEN a valid workout plan
    WHEN a workout plan is created
    THEN the workout plan is be returned
    """
    workout_plan = add_workout_plan_to_db(
        plans_repository=plans_repository, user_email=user_email
    )

    workout_plan_retrieved = plans_repository.get(id=workout_plan.id, owner=user_email)
    assert workout_plan_retrieved is not None
    assert workout_plan_retrieved.name == workout_plan.name
    assert workout_plan_retrieved.exercises == workout_plan.exercises
    assert workout_plan_retrieved.id is not None
    assert workout_plan_retrieved.created_at == now_iso


def test_list_user_workout_plans(
    plans_repository: repository.DynamoDBWorkoutPlanRepository,
    user_email: str,
) -> None:
    """
    GIVEN multiple workout plans
    WHEN a list of workout plans is requested for a user
    THEN only the workout plans for that user are returned
    """
    workout_plan_1 = add_workout_plan_to_db(
        plans_repository=plans_repository, user_email=user_email
    )
    workout_plan_2 = add_workout_plan_to_db(
        plans_repository=plans_repository, user_email=user_email
    )
    add_workout_plan_to_db(
        plans_repository=plans_repository, user_email="another_user@email.com"
    )

    workout_plan_retrieved = plans_repository.list(owner=user_email)
    assert len(workout_plan_retrieved) == 2
    assert workout_plan_1 in workout_plan_retrieved
    assert workout_plan_2 in workout_plan_retrieved


def test_update_workout_plan(
    plans_repository: repository.DynamoDBWorkoutPlanRepository,
    user_email: str,
) -> None:
    """
    GIVEN a valid workout plan
    WHEN that workout plan is updated
    THEN the updated workout plan is returned
    """
    workout_plan = add_workout_plan_to_db(
        plans_repository=plans_repository, user_email=user_email
    )

    workout_plan_update = model.WorkoutPlanUpdate(
        exercises=[model.ExercisePlan(name="test-exercise", sets=1)],
    )
    plan_updated = plans_repository.update(
        id=workout_plan.id,
        update_model=workout_plan_update,
        db_model=workout_plan,
        owner=user_email,
    )

    assert plan_updated is not None
    assert plan_updated.name == workout_plan.name
    assert plan_updated.exercises == workout_plan_update.exercises
    assert plan_updated.id == workout_plan.id


def test_delete_workout_plan(
    plans_repository: repository.DynamoDBWorkoutPlanRepository,
    user_email: str,
) -> None:
    """
    GIVEN a valid workout plan
    WHEN that workout plan is deleted
    THEN the workout plan is no longer returned
    """
    workout_plan = add_workout_plan_to_db(
        plans_repository=plans_repository, user_email=user_email
    )

    plans_repository.delete(workout_plan.id, owner=user_email)

    assert plans_repository.get(id=workout_plan.id, owner=user_email) is None
