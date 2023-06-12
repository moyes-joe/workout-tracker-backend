from __future__ import annotations

import logging
from typing import Any

from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.service_resource import Table

from src.exceptions import DuplicateWorkoutError, WorkoutError
from src.model import (
    BaseWorkoutCreate,
    BaseWorkoutUpdate,
    WorkoutLog,
    WorkoutPlan,
    WorkoutType,
)

from .workout_protocol import ModelType, WorkoutRepository


def _get_pk(owner: str, workout_type: WorkoutType) -> str:
    return f"OWNER#{owner}#WORKOUT_{workout_type}"


def _get_sk(workout_type: WorkoutType, id: str = "") -> str:
    if workout_type == WorkoutType.PLAN:
        return f"WORKOUT_PLAN#{id}"
    elif workout_type == WorkoutType.LOG:
        return f"WORKOUT_PLAN#{id}"
    else:
        raise ValueError("Invalid workout type")


def _create_dynamodb_item(owner: str, pk: str, sk: str, **attributes: Any) -> dict:
    return {
        "PK": pk,
        "SK": sk,
        "owner": owner,
        **attributes,
    }


class DynamoDBWorkoutRepository(WorkoutRepository[ModelType]):
    def __init__(self, table: Table, workout_type: WorkoutType, model: type[ModelType]):
        self._table = table
        self._workout_type: WorkoutType = workout_type
        self._model = model
        self._logger = logging.getLogger(__name__)

    def create(self, model: BaseWorkoutCreate, owner: str) -> ModelType:
        model_db = self._model(**model.dict())
        self._logger.info(
            f"Creating {self._workout_type} {model_db.id} for owner {owner!r}"
        )
        pk = _get_pk(owner=owner, workout_type=self._workout_type)
        sk = _get_sk(workout_type=self._workout_type, id=model_db.id)
        item = _create_dynamodb_item(
            owner=owner,
            pk=pk,
            sk=sk,
            **model_db.dict(),
        )
        try:
            self._table.put_item(Item=item)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise DuplicateWorkoutError(
                    f"{self._workout_type} already exists for owner {owner!r}"
                )
            else:
                self._logger.debug(
                    f"Error creating {self._workout_type}", exc_info=True
                )
                raise WorkoutError(f"Error creating {self._workout_type}")

        return model_db

    def get(self, id: str, owner: str) -> ModelType | None:
        self._logger.info(f"Getting {self._workout_type} {id} for owner {owner!r}")

        try:
            response = self._table.get_item(
                Key={
                    "PK": _get_pk(owner=owner, workout_type=self._workout_type),
                    "SK": _get_sk(workout_type=self._workout_type, id=id),
                }
            )
        except ClientError:
            self._logger.error(f"Error getting {self._workout_type!r}", exc_info=True)
            raise WorkoutError(f"Error getting {self._workout_type!r}")

        item = response.get("Item")

        return self._model(**item) if item else None  # type: ignore

    def list(self, owner: str) -> list[ModelType]:
        self._logger.info(f"Listing {self._workout_type}s for owner {owner!r}")

        try:
            response = self._table.query(
                KeyConditionExpression="PK = :pk",
                ExpressionAttributeValues={
                    ":pk": _get_pk(owner=owner, workout_type=self._workout_type)
                },
            )
        except ClientError:
            self._logger.error(f"Error listing {self._workout_type}", exc_info=True)
            raise WorkoutError(f"Error listing {self._workout_type}")

        items = response["Items"]

        return [self._model(**item) for item in items]  # type: ignore

    def update(
        self,
        id: str,
        update_model: BaseWorkoutUpdate,
        db_model: ModelType,
        owner: str,
    ) -> ModelType:
        self._logger.info(f"Updating {self._workout_type} {id!r} for owner {owner!r}")
        update_data = update_model.dict(exclude_unset=True)
        for field in db_model.dict().keys():
            if field in update_data:
                setattr(db_model, field, update_data[field])

        pk = _get_pk(owner=owner, workout_type=self._workout_type)
        sk = _get_sk(workout_type=self._workout_type, id=id)
        item = _create_dynamodb_item(
            owner=owner,
            pk=pk,
            sk=sk,
            **db_model.dict(),
        )

        try:
            self._table.put_item(Item=item)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise DuplicateWorkoutError(
                    f"{self._workout_type} {db_model.name!r} already exists for owner {owner!r}"
                )
            else:
                self._logger.debug(
                    f"Error creating {self._workout_type}", exc_info=True
                )
                raise WorkoutError(f"Error creating {self._workout_type}")
        return self._model(**item)

    def delete(self, id: str, owner: str) -> None:
        self._logger.info(f"Deleting {self._workout_type} {id!r} for owner {owner!r}")

        try:
            self._table.delete_item(
                Key={
                    "PK": _get_pk(owner=owner, workout_type=self._workout_type),
                    "SK": _get_sk(workout_type=self._workout_type, id=id),
                }
            )
        except ClientError:
            self._logger.error(f"Error deleting {self._workout_type}", exc_info=True)
            raise WorkoutError(f"Error deleting {self._workout_type}")

    def health_check(self) -> None:
        self._logger.info(f"Health checking {self._workout_type}")
        try:
            self._table.scan(Limit=1)
        except ClientError:
            self._logger.error(f"Error health checking {self._workout_type}")
            raise WorkoutError(f"Error health checking {self._workout_type}")


class DynamoDBWorkoutPlanRepository(DynamoDBWorkoutRepository[WorkoutPlan]):
    pass


class DynamoDBWorkoutLogRepository(DynamoDBWorkoutRepository[WorkoutLog]):
    pass
