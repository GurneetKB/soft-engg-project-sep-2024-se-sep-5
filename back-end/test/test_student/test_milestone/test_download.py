import pytest
from unittest.mock import patch, MagicMock
from application.setup import create_app
from flask import Response


@pytest.fixture(scope="module")
def client():
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


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Submissions.query")
@patch("apis.student.milestone_management.os.path.exists")
@patch("apis.student.milestone_management.send_file")
def test_download_submission_success(
    mock_send_file,
    mock_os_path_exists,
    mock_submissions_query,
    mock_get_team_id,
    client,
    student_token,
):
    """
    Test successful download of a submission document.
    """
    mock_get_team_id.return_value = 1

    # Mock submission and document
    mock_submission = MagicMock()
    mock_document = MagicMock(
        file_url="/path/to/document.pdf",
        title="Milestone1_Task101_TeamAlpha",
    )
    mock_submission.documents = mock_document
    mock_submissions_query.filter.return_value.first.return_value = mock_submission
    mock_os_path_exists.return_value = True
    mock_send_file.return_value = Response()

    response = client.get(
        "/student/download_submission/101",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    assert mock_send_file.called_with(mock_document.file_url)


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Submissions.query")
@patch("apis.student.milestone_management.os.path.exists")
def test_download_submission_file_not_found(
    mock_os_path_exists, mock_submissions_query, mock_get_team_id, client, student_token
):
    """
    Test 404 error when the file is not found on the server.
    """
    mock_get_team_id.return_value = 1

    mock_submission = MagicMock()
    mock_document = MagicMock(file_url="/path/to/document.pdf")
    mock_submission.documents = mock_document
    mock_submissions_query.filter.return_value.first.return_value = mock_submission
    mock_os_path_exists.return_value = False

    response = client.get(
        "/student/download_submission/101",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "File not found" in data["response"]["errors"]


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Submissions.query")
def test_download_submission_not_found(
    mock_submissions_query, mock_get_team_id, client, student_token
):
    """
    Test 404 error when the submission or document does not exist.
    """
    mock_get_team_id.return_value = 1
    mock_submissions_query.filter.return_value.first.return_value = None

    response = client.get(
        "/student/download_submission/101",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "Submission or document not found" in data["response"]["errors"]


@patch("apis.student.milestone_management.get_team_id")
def test_download_submission_unauthorized(mock_get_team_id, client):
    """
    Test 403 error when the user is not authorized.
    """
    mock_get_team_id.return_value = None

    response = client.get("/student/download_submission/101")

    assert response.status_code == 403
