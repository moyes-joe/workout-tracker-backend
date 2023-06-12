from __future__ import annotations

from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from src import model
from src.adapters import repository
from tests.utils import add_workout_log_to_db


def test_create_workout_plan(
    client: TestClient, id_token: str, API_V1_STR: str
) -> None:
    """
    GIVEN a valid workout log
    WHEN a POST request is made to /api/v1/logs
    THEN the response is be 201 (created) and the workout log is be returned
    """
    workout_plan_create = {
        "name": "test-plan",
        "plans": [{"name": "test-exercise", "sets": 1}],
        "logs": [
            {
                "name": "test-exercise",
                "sets": [{"reps": 1, "weight": 1}],
            }
        ],
    }

    response = client.post(
        f"{API_V1_STR}/logs",
        json=workout_plan_create,
        headers={"Authorization": id_token},
    )

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()
    assert body["name"] == workout_plan_create["name"]
    assert body["id"] is not None


def test_get_workout_plan(
    client: TestClient,
    API_V1_STR: str,
    id_token: str,
    user_email: str,
    logs_repository: repository.WorkoutRepository[model.WorkoutLog],
) -> None:
    """
    GIVEN a valid workout log
    WHEN a GET request is made to /api/v1/logs/{log_id}
    THEN the response is be 200 (ok) and the workout log is be returned
    """
    workout_log = add_workout_log_to_db(
        logs_repository=logs_repository, user_email=user_email
    )

    response = client.get(
        f"{API_V1_STR}/logs/{workout_log.id}", headers={"Authorization": id_token}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["name"] == workout_log.name
    assert body["id"] == workout_log.id


def test_get_workout_plan_not_found(
    client: TestClient, API_V1_STR: str, id_token: str
) -> None:
    """
    GIVEN a valid workout log id
    WHEN a GET request is made to /api/v1/logs/{log_id} with an invalid id
    THEN the response is be 404 (not found)
    """
    id = str(uuid4())

    response = client.get(
        f"{API_V1_STR}/logs/{id}", headers={"Authorization": id_token}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    body = response.json()
    assert id in body["detail"]


def test_list_workout_plans(
    client: TestClient,
    API_V1_STR: str,
    id_token: str,
    user_email: str,
    logs_repository: repository.WorkoutRepository[model.WorkoutLog],
) -> None:
    """
    GIVEN multiple workout logs
    WHEN a GET request is made to /api/v1/logs
    THEN the response is be 200 (ok) and the workout logs are be returned
    """
    workout_log_1 = add_workout_log_to_db(
        logs_repository=logs_repository, user_email=user_email
    )
    workout_log_2 = add_workout_log_to_db(
        logs_repository=logs_repository, user_email=user_email
    )

    response = client.get(f"{API_V1_STR}/logs", headers={"Authorization": id_token})

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert len(body) == 2

    ids = [workout_log_1.id, workout_log_2.id]
    assert body[0]["id"] in ids
    assert body[1]["id"] in ids


def test_update_workout_plan(
    client: TestClient,
    API_V1_STR: str,
    id_token: str,
    user_email: str,
    logs_repository: repository.WorkoutRepository[model.WorkoutLog],
) -> None:
    """
    GIVEN a valid workout log
    WHEN a PATCH request is made to /api/v1/logs/{log_id}
    THEN the response is be 200 (ok) and the workout log is be returned
    """
    workout_log = add_workout_log_to_db(
        logs_repository=logs_repository, user_email=user_email
    )

    workout_log_update = {"name": "test-log-update"}
    response = client.patch(
        f"{API_V1_STR}/logs/{workout_log.id}",
        json=workout_log_update,
        headers={"Authorization": id_token},
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["name"] == workout_log_update["name"]
    assert body["id"] == workout_log.id


def test_delete_workout_plan(
    client: TestClient,
    API_V1_STR: str,
    id_token: str,
    user_email: str,
    logs_repository: repository.WorkoutRepository[model.WorkoutLog],
) -> None:
    """
    GIVEN a valid workout log
    WHEN a DELETE request is made to /api/v1/logs/{log_id}
    THEN the response is be 200 (ok) and the workout log is be returned
    """
    workout_log = add_workout_log_to_db(
        logs_repository=logs_repository, user_email=user_email
    )

    response = client.delete(
        f"{API_V1_STR}/logs/{workout_log.id}", headers={"Authorization": id_token}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert logs_repository.get(id=workout_log.id, owner=user_email) is None
