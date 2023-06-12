from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src import exceptions, model
from src.adapters.repository import WorkoutRepository, get_workout_plans_repository
from src.api.deps import get_user_email

_logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_workout_plan(
    *,
    repository: WorkoutRepository[model.WorkoutPlan] = Depends(
        get_workout_plans_repository
    ),
    user_email: str = Depends(get_user_email),
    workout_plan: model.WorkoutPlanCreate,
) -> model.WorkoutPlan:
    """Create a users workout plan."""
    _logger.info(f"Creating workout plan {workout_plan.name!r} for user {user_email!r}")
    try:
        plan = repository.create(
            model=workout_plan,
            owner=user_email,
        )
    except exceptions.DuplicateWorkoutError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Workout plan {workout_plan.name!r} already exists",
        )

    _logger.info(f"Created workout plan {workout_plan!r} for user {user_email!r}")
    return plan


@router.get("/{plan_id}", status_code=status.HTTP_200_OK)
def get_workout_plan(
    *,
    repository: WorkoutRepository[model.WorkoutPlan] = Depends(
        get_workout_plans_repository
    ),
    user_email: str = Depends(get_user_email),
    plan_id: UUID,
) -> model.WorkoutPlan:
    """Get a users workout plan by name."""
    _logger.info(f"Getting workout plan {plan_id!r} for user {user_email!r}")
    plan = repository.get(id=str(plan_id), owner=user_email)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout plan {plan_id!r} not found",
        )
    return plan


@router.get("/", status_code=status.HTTP_200_OK)
def list_workout_plan(
    *,
    repository: WorkoutRepository[model.WorkoutPlan] = Depends(
        get_workout_plans_repository
    ),
    user_email: str = Depends(get_user_email),
) -> list[model.WorkoutPlan]:
    """List all workout plans for a user."""
    _logger.info(f"Listing workout plans for user {user_email!r}")
    return repository.list(owner=user_email)


@router.patch("/{plan_id}", status_code=status.HTTP_200_OK)
def update_workout_plan(
    *,
    repository: WorkoutRepository[model.WorkoutPlan] = Depends(
        get_workout_plans_repository
    ),
    user_email: str = Depends(get_user_email),
    plan_id: UUID,
    workout_plan_update: model.WorkoutPlanUpdate,
) -> model.WorkoutPlan:
    """Update a users workout plan."""
    _logger.info(f"Updating workout plan {plan_id!r} for user {user_email!r}")
    try:
        db_plan = repository.get(id=str(plan_id), owner=user_email)
        if not db_plan:
            raise HTTPException(
                status_code=404, detail=f"Workout plan {plan_id!r} not found"
            )
        return repository.update(
            id=str(plan_id),
            owner=user_email,
            db_model=db_plan,
            update_model=workout_plan_update,
        )
    except exceptions.WorkoutNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout plan {plan_id!r} not found",
        )


@router.delete("/{plan_id}")
def delete_workout_plan(
    *,
    repository: WorkoutRepository[model.WorkoutPlan] = Depends(
        get_workout_plans_repository
    ),
    user_email: str = Depends(get_user_email),
    plan_id: UUID,
) -> Response:
    """Delete a users workout plan."""
    _logger.info(f"Deleting workout plan {plan_id!r} for user {user_email!r}")
    plan = repository.get(id=str(plan_id), owner=user_email)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout plan {plan_id!r} not found",
        )
    repository.delete(id=str(plan_id), owner=user_email)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
