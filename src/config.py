from __future__ import annotations

from pydantic import BaseSettings


class Config(BaseSettings):
    """Application settings."""

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Workout Tracker"
    TABLE_NAME: str = "workout-tracker"
    DYNAMODB_URL: str | None = None


config = Config()
