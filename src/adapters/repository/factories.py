from __future__ import annotations

import logging
from functools import partial
from typing import Callable

import boto3
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table

from src.config import config
from src.model import WorkoutLog, WorkoutPlan, WorkoutType

from .dynamodb import DynamoDBWorkoutLogRepository, DynamoDBWorkoutPlanRepository
from .workout_protocol import WorkoutRepository

_logger = logging.getLogger(__name__)


def _configure_dynamodb_workout_repository(
    repository: Callable[[Table], WorkoutRepository],
    table_name: str | None = None,
    dynamodb_url: str | None = None,
) -> WorkoutRepository:
    """Get a workout repository configured for DynamoDB."""
    table_name = table_name or config.TABLE_NAME
    dynamodb_url = dynamodb_url or config.DYNAMODB_URL
    _logger.info(f"Connecting to DynamoDB at {dynamodb_url} and table {table_name}")
    dynamodb: DynamoDBServiceResource = boto3.resource(
        "dynamodb", endpoint_url=dynamodb_url
    )  # type: ignore
    table: Table = dynamodb.Table(table_name)
    return repository(table)


def get_workout_plans_repository(
    table_name: str | None = None,
    dynamodb_url: str | None = None,
) -> WorkoutRepository[WorkoutPlan]:
    """Get a workout plan repository."""
    repo = partial(
        DynamoDBWorkoutPlanRepository, workout_type=WorkoutType.PLAN, model=WorkoutPlan
    )
    return _configure_dynamodb_workout_repository(
        repository=repo, table_name=table_name, dynamodb_url=dynamodb_url
    )


def get_workout_logs_repository(
    table_name: str | None = None,
    dynamodb_url: str | None = None,
) -> WorkoutRepository[WorkoutLog]:
    """Get a workout log repository."""
    repo = partial(
        DynamoDBWorkoutLogRepository, workout_type=WorkoutType.LOG, model=WorkoutLog
    )
    return _configure_dynamodb_workout_repository(
        repository=repo, table_name=table_name, dynamodb_url=dynamodb_url
    )
