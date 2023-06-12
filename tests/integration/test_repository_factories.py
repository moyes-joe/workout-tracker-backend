from src.adapters.repository import (
    DynamoDBWorkoutLogRepository,
    DynamoDBWorkoutPlanRepository,
    get_workout_logs_repository,
    get_workout_plans_repository,
)


def test_get_workout_plans_repository():
    """Test get_workout_plans_repository."""
    repo = get_workout_plans_repository()
    assert isinstance(repo, DynamoDBWorkoutPlanRepository)


def test_get_workout_logs_repository():
    """Test get_workout_logs_repository."""
    repo = get_workout_logs_repository()
    assert isinstance(repo, DynamoDBWorkoutLogRepository)
