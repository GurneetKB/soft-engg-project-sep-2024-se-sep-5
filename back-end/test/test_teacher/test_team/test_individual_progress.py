import pytest
from application.setup import create_app
from application.models import *
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta


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


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.db.session.query")
def test_get_team_progress_success(
    mock_query,
    mock_get_single_team_under_user,
    client,
    instructor_token,
):
    """
    Test successful retrieval of team progress for a valid team ID.
    """
    mock_get_single_team_under_user.return_value = True

    mock_query_instance = MagicMock()
    mock_query.return_value = mock_query_instance

    # Mock the filter call to return another mock that simulates the behavior of an SQLAlchemy query
    mock_filtered_query = MagicMock()
    mock_query_instance.filter.return_value = mock_filtered_query

    def mock_submission():
        return MagicMock(
            task_id=1,
            submission_time=datetime.now() - timedelta(days=5),
            feedback="Great work!",
            feedback_time=datetime.now() - timedelta(days=4),
        )

    mock_filtered_query.filter.return_value.first = mock_submission

    response = client.get(
        "/teacher/team_management/individual/progress/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 200
    data = response.get_json()

    assert len(data) > 0, "No milestones returned"

    for milestone in data:
        assert "id" in milestone
        assert "title" in milestone
        assert "description" in milestone
        assert "deadline" in milestone
        assert "created_at" in milestone
        assert "tasks" in milestone
        assert isinstance(milestone["tasks"], list)

        for task in milestone["tasks"]:
            assert "task_id" in task
            assert "description" in task
            assert "is_completed" in task
            assert "submission_time" in task
            assert "feedback" in task
            assert "feedback_time" in task

    assert any(
        task["is_completed"] for milestone in data for task in milestone["tasks"]
    ), "No completed tasks found"
    assert any(
        task["feedback"] == "Great work!"
        for milestone in data
        for task in milestone["tasks"]
    ), "No task with expected feedback found"


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Milestones.query.all")
def test_get_team_progress_team_not_found(
    mock_milestones_query, mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 404 response when the team ID is not found.
    """
    mock_get_single_team_under_user.return_value = None
    mock_milestones_query.return_value = []

    response = client.get(
        "/teacher/team_management/individual/progress/999",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Team not found" in data["response"]["errors"][0]


def test_get_team_progress_invalid_role(client, student_token):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """
    response = client.get(
        "/teacher/team_management/individual/progress/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 403


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Milestones.query.all")
def test_get_team_progress_internal_server_error(
    mock_milestones_query, mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_get_single_team_under_user.side_effect = Exception("Unexpected error")
    mock_milestones_query.return_value = []

    response = client.get(
        "/teacher/team_management/individual/progress/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Unexpected error" in data["response"]["errors"][0]
