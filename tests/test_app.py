import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = {
        name: {key: list(value) if key == "participants" else value for key, value in activity.items()}
        for name, activity in activities.items()
    }
    yield
    activities.clear()
    activities.update({
        name: {key: list(value) if key == "participants" else value for key, value in activity.items()}
        for name, activity in original.items()
    })


client = TestClient(app)


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activities


def test_valid_signup_adds_student():
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    email = "michael@mergington.edu"

    response = client.post(f"/activities/Chess Club/signup?email={email}")

    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_unregister_participant_removes_email():
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/Chess Club/participants/{email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_nonexistent_activity_still_returns_404():
    response = client.post("/activities/Unknown Activity/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_from_nonexistent_activity_returns_404():
    email = "test@mergington.edu"

    response = client.delete(f"/activities/Unknown Activity/participants/{email}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_nonparticipant_returns_404():
    email = "test@mergington.edu"

    response = client.delete(f"/activities/Chess Club/participants/{email}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}
    assert email not in activities["Chess Club"]["participants"]
