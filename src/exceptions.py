from __future__ import annotations


class WorkoutError(Exception):
    """Base class for workout exceptions."""


class DuplicateWorkoutError(WorkoutError):
    """Raised when a workout plan already exists."""


class WorkoutNotFoundError(WorkoutError):
    """Raised when a workout plan is not found."""
