from __future__ import annotations

from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from src import model
from src.adapters import repository
from tests.utils import add_workout_plan_to_db


def test_create_workout_plan(
    client: TestClient, id_token: str, API_V1_STR: str
) -> None:
    """
    GIVEN a valid workout plan
    WHEN a POST request is made to /api/v1/plans
    THEN the response is be 201 (created) and the workout plan is be returned
    """
    workout_plan_create = {
        "name": "test-plan",
        "exercises": [{"name": "test-exercise", "sets": 1}],
    }

    response = client.post(
        f"{API_V1_STR}/plans",
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
    plans_repository: repository.WorkoutRepository[model.WorkoutPlan],
) -> None:
    """
    GIVEN a valid workout plan
    WHEN a GET request is made to /api/v1/plans/{plan_id}
    THEN the response is be 200 (ok) and the workout plan is be returned
    """
    workout_plan = add_workout_plan_to_db(
        plans_repository=plans_repository, user_email=user_email
    )

    response = client.get(
        f"{API_V1_STR}/plans/{workout_plan.id}", headers={"Authorization": id_token}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["name"] == workout_plan.name
    assert body["id"] == workout_plan.id


def test_get_workout_plan_not_found(
    client: TestClient,
    API_V1_STR: str,
    id_token: str,
) -> None:
    """
    GIVEN no workout plans
    WHEN a GET request is made to /api/v1/plans/{plan_id}
    THEN the response is be 404 (not found)
    """
    id = str(uuid4())
    response = client.get(
        f"{API_V1_STR}/plans/{id}", headers={"Authorization": id_token}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    body = response.json()
    assert id in body["detail"]


def test_list_workout_plans(
    client: TestClient,
    API_V1_STR: str,
    id_token: str,
    user_email: str,
    plans_repository: repository.WorkoutRepository[model.WorkoutPlan],
) -> None:
    """
    GIVEN multiple workout plans
    WHEN a GET request is made to /api/v1/plans
    THEN the response is be 200 (ok) and the workout plans are be returned
    """
    workout_plan_1 = add_workout_plan_to_db(
        plans_repository=plans_repository, user_email=user_email
    )
    workout_plan_2 = add_workout_plan_to_db(
        plans_repository=plans_repository, user_email=user_email
    )

    response = client.get(f"{API_V1_STR}/plans", headers={"Authorization": id_token})

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert len(body) == 2

    ids = [workout_plan_1.id, workout_plan_2.id]
    assert body[0]["id"] in ids
    assert body[1]["id"] in ids


def test_update_workout_plan(
    client: TestClient,
    API_V1_STR: str,
    id_token: str,
    user_email: str,
    plans_repository: repository.WorkoutRepository[model.WorkoutPlan],
) -> None:
    """
    GIVEN a valid workout plan
    WHEN a PATCH request is made to /api/v1/plans/{plan_id}
    THEN the response is be 200 (ok) and the workout plan is be returned
    """
    workout_plan = add_workout_plan_to_db(
        plans_repository=plans_repository, user_email=user_email
    )

    workout_plan_update = {"name": "updated-test-plan"}
    response = client.patch(
        f"{API_V1_STR}/plans/{workout_plan.id}",
        json=workout_plan_update,
        headers={"Authorization": id_token},
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["name"] == workout_plan_update["name"]
    assert body["id"] == workout_plan.id


def test_delete_workout_plan(
    client: TestClient,
    API_V1_STR: str,
    id_token: str,
    user_email: str,
    plans_repository: repository.WorkoutRepository[model.WorkoutPlan],
) -> None:
    """
    GIVEN a valid workout plan
    WHEN a DELETE request is made to /api/v1/plans/{plan_id}
    THEN the response is be 200 (ok) and the workout plan is be returned
    """
    workout_plan = add_workout_plan_to_db(
        plans_repository=plans_repository, user_email=user_email
    )

    response = client.delete(
        f"{API_V1_STR}/plans/{workout_plan.id}", headers={"Authorization": id_token}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert plans_repository.get(id=workout_plan.id, owner=user_email) is None
