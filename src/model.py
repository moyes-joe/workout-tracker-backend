from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


def now_isoformat() -> str:
    """Return the current time in ISO format."""
    return datetime.now(tz=timezone.utc).isoformat()


class WorkoutType(str, Enum):
    LOG = "LOG"
    PLAN = "PLAN"


class SetLog(BaseModel):
    weight: Decimal
    reps: int


class ExerciseLog(BaseModel):
    name: str
    sets: list[SetLog]


class ExercisePlan(BaseModel):
    name: str
    sets: int


class BaseWorkoutCreate(BaseModel):
    name: str


class WorkoutPlanCreate(BaseWorkoutCreate):
    exercises: list[ExercisePlan]


class WorkoutLogCreate(BaseWorkoutCreate):
    plans: list[ExercisePlan]
    logs: list[ExerciseLog]


class BaseWorkoutDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    created_at: str = Field(default_factory=now_isoformat)


class WorkoutPlan(BaseWorkoutDB):
    exercises: list[ExercisePlan]


class WorkoutLog(BaseWorkoutDB):
    plans: list[ExercisePlan]
    logs: list[ExerciseLog]


class BaseWorkoutUpdate(BaseModel):
    name: str | None = None


class WorkoutPlanUpdate(BaseWorkoutUpdate):
    exercises: list[ExercisePlan] | None = None


class WorkoutLogUpdate(BaseWorkoutUpdate):
    plans: list[ExercisePlan] | None = None
    logs: list[ExerciseLog] | None = None
