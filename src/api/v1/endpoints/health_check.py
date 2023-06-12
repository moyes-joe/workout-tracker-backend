from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.adapters.repository import (
    WorkoutRepository,
    get_workout_logs_repository,
    get_workout_plans_repository,
)

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def health_check(
    *,
    workout_plans_repository: WorkoutRepository = Depends(get_workout_plans_repository),
    workout_logs_repository: WorkoutRepository = Depends(get_workout_logs_repository),
) -> dict[str, str]:
    """Health check endpoint.

    Checks if the database is available.
    """
    try:
        workout_plans_repository.health_check()
        workout_logs_repository.health_check()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available",
        )
    return {"message": "OK"}
