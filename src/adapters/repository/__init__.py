__all__ = [
    "DynamoDBWorkoutPlanRepository",
    "get_workout_plans_repository",
    "DynamoDBWorkoutLogRepository",
    "get_workout_logs_repository",
    "WorkoutRepository",
]
from .dynamodb import DynamoDBWorkoutLogRepository, DynamoDBWorkoutPlanRepository
from .factories import get_workout_logs_repository, get_workout_plans_repository
from .workout_protocol import WorkoutRepository
