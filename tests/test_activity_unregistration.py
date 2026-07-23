from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_from_activity():
    student_email = f"student-{uuid4().hex}@mergington.edu"

    signup_response = client.post(
        f"/activities/Chess Club/signup?email={student_email}"
    )
    assert signup_response.status_code == 200

    unregister_response = client.delete(
        f"/activities/Chess Club/unregister?email={student_email}"
    )

    assert unregister_response.status_code == 200
    assert "Unregistered" in unregister_response.json()["message"]

    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    assert student_email not in activities_response.json()["Chess Club"]["participants"]
