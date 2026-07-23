from copy import deepcopy
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src import app as app_module
from src.app import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_activity_store():
    """Reset the in-memory activity store before and after each backend test."""
    original_store = deepcopy(app_module.activities)

    app_module.activities.clear()
    app_module.activities.update(deepcopy(original_store))

    yield

    app_module.activities.clear()
    app_module.activities.update(deepcopy(original_store))


def test_get_activities_returns_activity_catalog():
    # Arrange
    expected_activity_names = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Basketball Club",
        "Drama Club",
        "Art Workshop",
        "Math Olympiad",
        "Science Club",
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert set(payload).issuperset(expected_activity_names)
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_succeeds_for_a_new_student():
    # Arrange
    activity_name = "Chess Club"
    student_email = f"student-{uuid4().hex}@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={student_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {student_email} for {activity_name}"

    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    assert student_email in activities_response.json()[activity_name]["participants"]


def test_signup_for_activity_rejects_a_duplicate_student():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={duplicate_email}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_from_activity_succeeds_for_an_active_participant():
    # Arrange
    activity_name = "Chess Club"
    student_email = f"student-{uuid4().hex}@mergington.edu"
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={student_email}"
    )
    assert signup_response.status_code == 200

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={student_email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == (
        f"Unregistered {student_email} from {activity_name}"
    )

    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    assert student_email not in activities_response.json()[activity_name]["participants"]


def test_unregister_from_activity_returns_not_found_for_an_unknown_student():
    # Arrange
    activity_name = "Chess Club"
    student_email = f"student-{uuid4().hex}@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={student_email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
