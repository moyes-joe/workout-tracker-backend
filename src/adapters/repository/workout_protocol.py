from __future__ import annotations

from typing import Protocol, TypeVar

from src.model import BaseWorkoutCreate, BaseWorkoutDB, BaseWorkoutUpdate

ModelType = TypeVar("ModelType", bound=BaseWorkoutDB)


class WorkoutRepository(Protocol[ModelType]):
    def create(self, model: BaseWorkoutCreate, owner: str) -> ModelType:
        ...

    def get(self, id: str, owner: str) -> ModelType | None:
        ...

    def list(self, owner: str) -> list[ModelType]:
        ...

    def update(
        self, id: str, update_model: BaseWorkoutUpdate, db_model: ModelType, owner: str
    ) -> ModelType:
        ...

    def delete(self, id: str, owner: str) -> None:
        ...

    def health_check(self) -> None:
        ...
