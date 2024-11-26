from unittest.mock import patch, MagicMock
import pytest


@pytest.fixture
def mock_submission():
    mock_submission = MagicMock()
    mock_document = MagicMock()
    mock_document.file_url = "/path/to/file.pdf"
    mock_submission.documents = mock_document
    return mock_submission


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Submissions.query")
@patch("apis.teacher.team_management.os.path.exists")
@patch("apis.teacher.team_management.send_file")
def test_view_submission_success(
    mock_send_file,
    mock_path_exists,
    mock_submissions_query,
    mock_get_single_team_under_user,
    mock_submission,
    client,
    instructor_token,
):
    """
    Test successful retrieval of submission file for a specific task and team.
    """
    mock_get_single_team_under_user.return_value = True

    mock_filter = MagicMock()
    mock_filter.first.return_value = mock_submission
    mock_submissions_query.filter.return_value = mock_filter

    mock_path_exists.return_value = True

    mock_send_file.return_value = "file data"

    response = client.get(
        "/teacher/team_management/individual/submission/1/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 200
    assert response.data == b"file data"


@patch("apis.teacher.team_management.get_single_team_under_user")
def test_view_submission_team_not_found(
    mock_get_single_team_under_user, client, instructor_token
):
    """
    Test case when the team is not found.
    """
    mock_get_single_team_under_user.return_value = None

    response = client.get(
        "/teacher/team_management/individual/submission/1/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    assert "Team not found" in response.get_data(as_text=True)


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Submissions.query.filter")
def test_view_submission_not_found(
    mock_filter, mock_get_single_team_under_user, client, instructor_token
):
    """
    Test case when the submission or document is not found.
    """
    mock_get_single_team_under_user.return_value = True

    mock_filter.return_value.first.return_value = None

    response = client.get(
        "/teacher/team_management/individual/submission/1/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    assert "Submission or document not found" in response.get_data(as_text=True)


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Submissions.query")
@patch("apis.teacher.team_management.os.path.exists")
def test_view_submission_file_not_found(
    mock_path_exists,
    mock_submissions_query,
    mock_get_single_team_under_user,
    mock_submission,
    client,
    instructor_token,
):
    """
    Test case when the file does not exist on the server.
    """
    mock_get_single_team_under_user.return_value = True

    mock_filter = MagicMock()
    mock_filter.first.return_value = mock_submission
    mock_submissions_query.filter.return_value = mock_filter

    mock_path_exists.return_value = False

    response = client.get(
        "/teacher/team_management/individual/submission/1/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    assert "File not found" in response.get_data(as_text=True)


def test_view_submission_forbidden(client, student_token):
    """
    Test case when the user does not have the required role.
    """

    response = client.get(
        "/teacher/team_management/individual/submission/1/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 403


@patch("apis.teacher.team_management.get_single_team_under_user")
def test_view_submission_internal_server_error(
    mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_get_single_team_under_user.side_effect = Exception("Unexpected error")

    response = client.get(
        "/teacher/team_management/individual/submission/1/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Unexpected error" in data["response"]["errors"][0]
