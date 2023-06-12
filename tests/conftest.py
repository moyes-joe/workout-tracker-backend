from __future__ import annotations

from typing import Generator

import boto3
import freezegun
import jwt
import pytest
from fastapi.testclient import TestClient
from moto import mock_dynamodb
from mypy_boto3_dynamodb.client import DynamoDBClient

from src import model
from src.adapters import repository
from src.config import config
from src.main import app


@pytest.fixture
def aws_mock_envs(monkeypatch) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def dynamodb_table(aws_mock_envs) -> Generator[str, None, None]:
    with mock_dynamodb():
        client: DynamoDBClient = boto3.client("dynamodb")  # type: ignore
        table_name = config.TABLE_NAME
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table_name


@pytest.fixture
def plans_repository(
    dynamodb_table: str,
) -> repository.WorkoutRepository[model.WorkoutPlan]:
    return repository.get_workout_plans_repository(table_name=dynamodb_table)


@pytest.fixture
def logs_repository(
    dynamodb_table: str,
) -> repository.WorkoutRepository[model.WorkoutLog]:
    return repository.get_workout_logs_repository(table_name=dynamodb_table)


@pytest.fixture
def id_token(user_email) -> str:
    return jwt.encode({"cognito:username": user_email}, "secret")


@pytest.fixture
def user_email() -> str:
    return "user@email.com"


@pytest.fixture
def client(
    plans_repository: repository.WorkoutRepository[model.WorkoutPlan],
    logs_repository: repository.WorkoutRepository[model.WorkoutLog],
) -> TestClient:
    app.dependency_overrides[
        repository.WorkoutRepository[model.WorkoutPlan]
    ] = lambda: plans_repository
    app.dependency_overrides[
        repository.WorkoutRepository[model.WorkoutLog]
    ] = lambda: logs_repository

    return TestClient(app)


@pytest.fixture
def API_V1_STR() -> str:
    return "/api/v1"


@pytest.fixture
def now_iso() -> str:
    return "2021-01-01T00:00:00+00:00"


@pytest.fixture
def frozen_time(now_iso: str) -> Generator[None, None, None]:
    with freezegun.freeze_time(now_iso):
        yield
