import pytest
from application.setup import create_app
from application.models import *
from unittest.mock import patch


@pytest.fixture
def client(scope="session"):
    app = create_app("sqlite:///testing.sqlite3", testing=True)
    with app.test_client() as client:
        yield client


@pytest.fixture
def student_token(client):
    response = client.post(
        "/login?include_auth_token",
        json={"username": "student1", "password": "password123"},
    )
    return response.json["response"]["user"]["authentication_token"]


@pytest.fixture
def instructor_token(client):
    response = client.post(
        "/login?include_auth_token",
        json={"username": "profsmith", "password": "password123"},
    )
    assert (
        response.status_code == 200
    ), f"Login failed with status code {response.status_code}: {response.data}"
    return response.json["response"]["user"]["authentication_token"]


@patch("apis.teacher.team_management.get_teams_under_user")
def test_get_teams_success(mock_get_teams_under_user, client, instructor_token):
    """
    Test successful retrieval of teams for a valid instructor.
    """
    mock_get_teams_under_user.return_value = [
        Teams(id=1, name="Team Alpha"),
        Teams(id=2, name="Team Beta"),
    ]

    response = client.get(
        "/teacher/team_management/individual",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "teams" in data
    assert len(data["teams"]) == 2
    assert data["teams"][0]["id"] == 1
    assert data["teams"][0]["name"] == "Team Alpha"
    assert data["teams"][1]["id"] == 2
    assert data["teams"][1]["name"] == "Team Beta"


@patch("apis.teacher.team_management.get_teams_under_user")
def test_get_teams_no_teams(mock_get_teams_under_user, client, instructor_token):
    """
    Test successful response when no teams are found for the instructor.
    """
    mock_get_teams_under_user.return_value = []

    response = client.get(
        "/teacher/team_management/individual",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "teams" in data
    assert len(data["teams"]) == 0


@patch("apis.teacher.team_management.get_teams_under_user")
def test_get_teams_invalid_role(mock_get_teams_under_user, client, student_token):
    """
    Test access denied for a user without the required role.
    """
    mock_get_teams_under_user.return_value = []

    response = client.get(
        "/teacher/team_management/individual",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 403
    data = response.get_json()
    assert "errors" in data["response"]


@patch("apis.teacher.team_management.get_teams_under_user")
def test_get_teams_internal_server_error(
    mock_get_teams_under_user, client, instructor_token
):
    """
    Test internal server error when an exception occurs.
    """
    mock_get_teams_under_user.side_effect = Exception("Database error")

    response = client.get(
        "/teacher/team_management/individual",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Database error" in data["response"]["errors"][0]
