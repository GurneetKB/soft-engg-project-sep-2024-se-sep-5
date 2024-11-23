import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_submission():
    return MagicMock(id=1, task_id=1, team_id=1)


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Submissions.query")
@patch("apis.teacher.team_management.db.session.commit")
def test_provide_feedback_success(
    mock_db_commit,
    mock_submissions_query,
    mock_get_single_team_under_user,
    mock_submission,
    client,
    instructor_token,
):
    """
    Test successful feedback submission for a valid team and task.
    """
    mock_get_single_team_under_user.return_value = True

    mock_filter = MagicMock()
    mock_filter.first.return_value = mock_submission
    mock_submissions_query.filter.return_value = mock_filter

    data = {"feedback": "Excellent work!"}

    response = client.post(
        "/teacher/team_management/individual/feedback/1/1",
        json=data,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 201
    assert "message" in response.json
    assert response.json["message"] == "The feedback is successfully provided."
    mock_db_commit.assert_called_once()


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Submissions.query.filter")
def test_provide_feedback_team_not_found(
    mock_filter, mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 404 response when the team is not found.
    """
    mock_get_single_team_under_user.return_value = None
    mock_filter.return_value.first.return_value = None

    data = {"feedback": "Excellent work!"}

    response = client.post(
        "/teacher/team_management/individual/feedback/999/1",
        json=data,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Team not found" in data["response"]["errors"][0]


def test_provide_feedback_missing_feedback(client, instructor_token):
    """
    Test 400 response when feedback is missing in the request data.
    """
    data = {}

    response = client.post(
        "/teacher/team_management/individual/feedback/1/1",
        json=data,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Feedback data is required" in data["response"]["errors"][0]


def test_provide_feedback_invalid_feedback(client, instructor_token):
    """
    Test 400 response when feedback is not a valid string.
    """
    data = {"feedback": ""}

    response = client.post(
        "/teacher/team_management/individual/feedback/1/1",
        json=data,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Feedback must be a non-empty string" in data["response"]["errors"][0]


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Submissions.query.filter")
def test_provide_feedback_submission_not_found(
    mock_filter, mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 404 response when the submission is not found.
    """
    mock_get_single_team_under_user.return_value = True
    mock_filter.return_value.first.return_value = None

    data = {"feedback": "Excellent work!"}

    response = client.post(
        "/teacher/team_management/individual/feedback/1/999",
        json=data,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Submission not found" in data["response"]["errors"][0]


def test_provide_feedback_invalid_role(client, student_token):
    """
    Test 403 response when a user without the required role tries to provide feedback.
    """
    data = {"feedback": "Excellent work!"}

    response = client.post(
        "/teacher/team_management/individual/feedback/1/1",
        json=data,
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 403
    data = response.get_json()
    assert "errors" in data["response"]


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Submissions.query.filter")
def test_provide_feedback_internal_server_error(
    mock_filter, mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_get_single_team_under_user.side_effect = Exception("Unexpected error")
    mock_filter.return_value.first.return_value = None

    data = {"feedback": "Excellent work!"}

    response = client.post(
        "/teacher/team_management/individual/feedback/1/1",
        json=data,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Unexpected error" in data["response"]["errors"][0]
