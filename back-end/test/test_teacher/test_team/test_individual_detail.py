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
    # Login as a student and get a token
    response = client.post(
        "/login?include_auth_token",
        json={"username": "student1", "password": "password123"},
    )
    return response.json["response"]["user"]["authentication_token"]


# Mock data for the team and its members
def mock_team_data():
    class MockUser:
        def __init__(self, id, username, email, github_username=None):
            self.id = id
            self.username = username
            self.email = email
            self.github_username = github_username

    class MockTeam:
        def __init__(self, id, name, members, github_repo_url, instructor, ta):
            self.id = id
            self.name = name
            self.members = members
            self.github_repo_url = github_repo_url
            self.instructor = instructor
            self.ta = ta

    members = [
        MockUser(
            id=1,
            username="JohnDoe",
            email="john@example.com",
            github_username="john123",
        ),
        MockUser(
            id=2,
            username="JaneDoe",
            email="jane@example.com",
            github_username="jane456",
        ),
    ]
    instructor = MockUser(id=3, username="Instructor", email="instructor@example.com")
    ta = MockUser(id=4, username="TeachingAssistant", email="ta@example.com")
    return MockTeam(
        id=1,
        name="Team Alpha",
        members=members,
        github_repo_url="https://github.com/example/repo",
        instructor=instructor,
        ta=ta,
    )


@patch("apis.teacher.team_management.get_single_team_under_user")
def test_get_team_details_success(
    mock_get_single_team_under_user, client, instructor_token
):
    """
    Test successful retrieval of team details for a valid team ID.
    """
    mock_get_single_team_under_user.return_value = mock_team_data()

    response = client.get(
        "/teacher/team_management/individual/detail/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "team" in data
    assert data["team"]["id"] == 1
    assert data["team"]["name"] == "Team Alpha"
    assert len(data["team"]["members"]) == 2
    assert data["team"]["members"][0]["id"] == 1
    assert data["team"]["members"][0]["github_username"] == "john123"
    assert data["team"]["github_repo_url"] == "https://github.com/example/repo"
    assert data["team"]["instructor"]["id"] == 3
    assert data["team"]["ta"]["id"] == 4


@patch("apis.teacher.team_management.get_single_team_under_user")
def test_get_team_details_team_not_found(
    mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 404 response when the team is not found.
    """
    mock_get_single_team_under_user.return_value = None

    response = client.get(
        "/teacher/team_management/individual/detail/999",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Team not found" in data["response"]["errors"][0]


@patch("apis.teacher.team_management.get_single_team_under_user")
def test_get_team_details_invalid_role(
    mock_get_single_team_under_user, client, student_token
):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """
    mock_get_single_team_under_user.return_value = mock_team_data()

    response = client.get(
        "/teacher/team_management/individual/detail/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 403
    data = response.get_json()
    assert "errors" in data["response"]


@patch("apis.teacher.team_management.get_single_team_under_user")
def test_get_team_details_internal_server_error(
    mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_get_single_team_under_user.side_effect = Exception("Unexpected error")

    response = client.get(
        "/teacher/team_management/individual/detail/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Unexpected error" in data["response"]["errors"][0]
