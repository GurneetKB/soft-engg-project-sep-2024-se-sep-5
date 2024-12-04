import pytest
from unittest.mock import patch


@pytest.fixture
def mock_teams_under_user():
    return [
        {"id": 1, "name": "Team Alpha"},
        {"id": 2, "name": "Team Beta"},
    ]


@patch("apis.teacher.team_management.get_teams_under_user")
def test_get_teams_success(
    mock_get_teams_under_user, mock_teams_under_user, client, instructor_token
):
    """
    Test successful retrieval of teams for a valid instructor.
    """
    mock_get_teams_under_user.return_value = [
        type("Teams", (), mock_team) for mock_team in mock_teams_under_user
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


def test_get_teams_invalid_role(client, student_token):
    """
    Test access denied for a user without the required role.
    """

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
    assert (
        "An unexpected error occurred. Try again later."
        in data["response"]["errors"][0]
    )
