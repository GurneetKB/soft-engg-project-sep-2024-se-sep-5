import pytest
from unittest.mock import patch, MagicMock
from application.setup import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app("sqlite:///testing.sqlite3", testing=True)
    with app.test_client() as client:
        yield client


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


@pytest.fixture
def student_token(client):
    response = client.post(
        "/login?include_auth_token",
        json={"username": "student1", "password": "password123"},
    )
    return response.json["response"]["user"]["authentication_token"]


@pytest.fixture
def mock_team():
    return {"id": 1, "name": "Team Alpha"}


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.db.session.query")
def test_get_team_milestones_success(
    mock_query, mock_get_team_id, mock_team, client, student_token
):
    """Test successful retrieval of team milestones."""
    mock_get_team_id.return_value = 1
    mock_team_instance = type("Team", (), mock_team)
    mock_query.return_value.filter.return_value.first.return_value = mock_team_instance

    mock_milestones = [
        MagicMock(id=1, title="Milestone 1"),
        MagicMock(id=2, title="Milestone 2"),
    ]
    mock_query.return_value.all.return_value = mock_milestones

    mock_query.return_value.filter.return_value.scalar.side_effect = [
        5,
        3,
    ]
    mock_query.return_value.join.return_value.filter.return_value.filter.return_value.scalar.side_effect = [
        4,
        2,
    ]

    response = client.get(
        "/student/milestone_management/overall",
        headers={"Authentication-Token": student_token},
    )

    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}, response: {response.data}"
    data = response.get_json()
    assert data["team_name"] == "Team Alpha"
    assert len(data["milestones"]) == 2
    assert data["milestones"][0]["completion_percentage"] == 80.0
    assert round(data["milestones"][1]["completion_percentage"], 2) == 66.67

    mock_get_team_id.assert_called_once()
    mock_query.return_value.all.assert_called_once()
    assert mock_query.return_value.filter.return_value.scalar.call_count == 2
    assert (
        mock_query.return_value.join.return_value.filter.return_value.filter.return_value.scalar.call_count
        == 2
    )

    assert data["milestones"][0]["milestone_id"] == 1
    assert data["milestones"][0]["title"] == "Milestone 1"
    assert data["milestones"][1]["milestone_id"] == 2
    assert data["milestones"][1]["title"] == "Milestone 2"


@patch("apis.student.milestone_management.get_team_id")
def test_get_team_milestones_no_team(mock_get_team_id, client, student_token):
    """
    Test 400 response when the student is not assigned to a team.
    """
    mock_get_team_id.return_value = None

    response = client.get(
        "/student/milestone_management/overall",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "No team is assigned to you yet." in data["response"]["errors"][0]


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.db.session.query")
def test_get_team_milestones_internal_server_error(
    mock_query, mock_get_team_id, client, student_token
):
    """
    Test 500 response when there is a database query failure.
    """
    mock_get_team_id.return_value = 1

    mock_query.side_effect = Exception("Database error")

    response = client.get(
        "/student/milestone_management/overall",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 500


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.db.session.query")
def test_get_team_milestones_empty_milestones(
    mock_query, mock_get_team_id, mock_team, client, student_token
):
    """
    Test 200 response with no milestones in the database.
    """
    mock_get_team_id.return_value = 1

    mock_query.return_value.filter.return_value.first.return_value = type(
        "Team", (), mock_team
    )

    mock_query.return_value.all.return_value = []

    response = client.get(
        "/student/milestone_management/overall",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["team_name"] == "Team Alpha"
    assert len(data["milestones"]) == 0


def test_get_team_milestones_invalid_role(client, instructor_token):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """
    response = client.get(
        "/student/milestone_management/overall",
        headers={"Authentication-Token": instructor_token},
    )
    assert response.status_code == 403
