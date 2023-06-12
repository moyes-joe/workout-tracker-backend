from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src import exceptions, model
from src.adapters.repository import WorkoutRepository, get_workout_logs_repository
from src.api.deps import get_user_email

_logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_workout_plan(
    *,
    repository: WorkoutRepository[model.WorkoutLog] = Depends(
        get_workout_logs_repository
    ),
    user_email: str = Depends(get_user_email),
    workout_log: model.WorkoutLogCreate,
) -> model.WorkoutLog:
    """Create a users workout plan."""
    _logger.info(f"Creating workout plan {workout_log.name!r} for user {user_email!r}")
    try:
        log = repository.create(
            model=workout_log,
            owner=user_email,
        )
    except exceptions.DuplicateWorkoutError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Workout log {workout_log.name!r} already exists",
        )

    _logger.info(f"Created workout log {workout_log!r} for user {user_email!r}")
    return log


@router.get("/{log_id}", status_code=status.HTTP_200_OK)
def get_workout_log(
    *,
    repository: WorkoutRepository[model.WorkoutLog] = Depends(
        get_workout_logs_repository
    ),
    user_email: str = Depends(get_user_email),
    log_id: UUID,
) -> model.WorkoutLog:
    """Get a users workout log by name."""
    _logger.info(f"Getting workout log {log_id!r} for user {user_email!r}")
    workout_log = repository.get(id=str(log_id), owner=user_email)
    if workout_log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout log {log_id!r} not found",
        )
    return workout_log


@router.get("/", status_code=status.HTTP_200_OK)
def list_workout_logs(
    *,
    repository: WorkoutRepository[model.WorkoutLog] = Depends(
        get_workout_logs_repository
    ),
    user_email: str = Depends(get_user_email),
) -> list[model.WorkoutLog]:
    """List all workout logs for a user."""
    _logger.info(f"Listing workout logs for user {user_email!r}")
    return repository.list(owner=user_email)


@router.patch("/{log_id}", status_code=status.HTTP_200_OK)
def update_workout_log(
    *,
    repository: WorkoutRepository[model.WorkoutLog] = Depends(
        get_workout_logs_repository
    ),
    user_email: str = Depends(get_user_email),
    log_id: UUID,
    workout_plan_update: model.WorkoutLogUpdate,
) -> model.WorkoutLog:
    """Update a users workout log."""
    _logger.info(f"Updating workout log {log_id!r} for user {user_email!r}")
    try:
        db_plan = repository.get(id=str(log_id), owner=user_email)
        if not db_plan:
            raise HTTPException(
                status_code=404, detail=f"Workout log {log_id!r} not found"
            )
        return repository.update(
            id=str(log_id),
            owner=user_email,
            db_model=db_plan,
            update_model=workout_plan_update,
        )
    except exceptions.WorkoutNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout log {log_id!r} not found",
        )


@router.delete("/{log_id}")
def delete_workout_log(
    *,
    repository: WorkoutRepository[model.WorkoutLog] = Depends(
        get_workout_logs_repository
    ),
    user_email: str = Depends(get_user_email),
    log_id: UUID,
) -> Response:
    """Delete a users workout log."""
    _logger.info(f"Deleting workout log {log_id!r} for user {user_email!r}")
    log = repository.get(id=str(log_id), owner=user_email)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout log {log_id!r} not found",
        )
    repository.delete(id=str(log_id), owner=user_email)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
