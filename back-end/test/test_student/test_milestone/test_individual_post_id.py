import pytest
from unittest.mock import patch, MagicMock
from application.setup import create_app
from io import BytesIO
from datetime import datetime, timedelta, timezone
import os


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
def mock_milestone():
    return MagicMock(
        id=1,
        deadline=datetime.now(timezone.utc) + timedelta(days=1),
        task_milestones=[
            MagicMock(id=101, description="Task 1"),
            MagicMock(id=102, description="Task 2"),
        ],
    )


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Milestones.query")
@patch("apis.student.milestone_management.Teams.query")
@patch("apis.student.milestone_management.os.makedirs")
@patch("apis.student.milestone_management.os.path.join")
@patch("apis.student.milestone_management.Submissions.query")
def test_submit_milestone_success(
    mock_submissions_query,
    mock_os_path_join,
    mock_os_makedirs,
    mock_teams_query,
    mock_milestones_query,
    mock_get_team_id,
    client,
    student_token,
    tmp_path,
    mock_milestone,
):
    """
    Test successful submission of milestone documents.
    """

    mock_get_team_id.return_value = 1
    mock_team = MagicMock(id=1, name="Team Alpha")
    mock_teams_query.get.return_value = mock_team

    mock_milestones_query.get.return_value = mock_milestone

    mock_submissions_query.filter_by.return_value.first.return_value = None

    file_data = {
        "101": (BytesIO(b"PDF content"), "task101.pdf"),
        "102": (BytesIO(b"PDF content"), "task102.pdf"),
    }

    mock_os_path_join.side_effect = lambda *args: str(tmp_path.joinpath(*args[1:]))

    with patch("werkzeug.datastructures.FileStorage.save") as mock_file_save:
        response = client.post(
            "/student/milestone_management/individual/1",
            headers={"Authentication-Token": student_token},
            data=file_data,
            content_type="multipart/form-data",
        )

    assert (
        response.status_code == 201
    ), f"Unexpected status code: {response.status_code}, response: {response.data}"
    data = response.get_json()
    assert data["message"] == "Milestone documents submitted successfully"

    mock_get_team_id.assert_called_once()
    mock_teams_query.get.assert_called_once_with(1)
    mock_milestones_query.get.assert_called_once_with(1)
    mock_os_makedirs.assert_called_once()
    assert mock_file_save.call_count == 2

    saved_files = [call.args[0] for call in mock_file_save.call_args_list]
    assert all(str(tmp_path) in file_path for file_path in saved_files)
    assert any("Milestone1_Task101_Team" in file_path for file_path in saved_files)
    assert any("Milestone1_Task102_Team" in file_path for file_path in saved_files)


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Milestones.query")
@patch("apis.student.milestone_management.Teams.query")
def test_submit_milestone_deadline_passed(
    mock_teams_query, mock_milestones_query, mock_get_team_id, client, student_token
):
    """
    Test 400 error when the milestone deadline has passed.
    """
    mock_get_team_id.return_value = 1
    mock_team = MagicMock(name="Team Alpha")
    mock_teams_query.get.return_value = mock_team

    mock_milestone = MagicMock(
        id=1,
        deadline=datetime.now(timezone.utc) - timedelta(days=1),
        task_milestones=[MagicMock(id=101, description="Task 1")],
    )
    mock_milestones_query.get.return_value = mock_milestone
    file_data = {"101": (BytesIO(b"PDF content"), "task101.pdf")}

    response = client.post(
        "/student/milestone_management/individual/1",
        headers={"Authentication-Token": student_token},
        data=file_data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "Cannot submit after the milestone deadline" in data["response"]["errors"]


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Milestones.query")
@patch("apis.student.milestone_management.Teams.query")
def test_submit_milestone_invalid_task_or_file(
    mock_teams_query, mock_milestones_query, mock_get_team_id, client, student_token
):
    """
    Test 400 error for invalid task ID or file type.
    """
    mock_get_team_id.return_value = 1
    mock_team = MagicMock(name="Team Alpha")
    mock_teams_query.get.return_value = mock_team

    mock_milestone = MagicMock(
        id=1,
        deadline=datetime.now(timezone.utc) + timedelta(days=1),
        task_milestones=[MagicMock(id=101, description="Task 1")],
    )
    mock_milestones_query.get.return_value = mock_milestone

    file_data = {"999": (BytesIO(b"PDF content"), "task999.docx")}

    response = client.post(
        "/student/milestone_management/individual/1",
        headers={"Authentication-Token": student_token},
        data=file_data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert (
        "Task 999 is not valid for this milestone or the file is not a PDF"
        in data["response"]["errors"]
    )


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Milestones.query")
def test_submit_milestone_not_found(
    mock_milestones_query, mock_get_team_id, client, student_token
):
    """
    Test 404 error when the milestone or team does not exist.
    """
    mock_get_team_id.return_value = None
    mock_milestones_query.get.return_value = None

    file_data = {"101": (BytesIO(b"PDF content"), "task101.pdf")}

    response = client.post(
        "/student/milestone_management/individual/1",
        headers={"Authentication-Token": student_token},
        data=file_data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "Milestone or team not found" in data["response"]["errors"]


def test_submit_milestone_invalid_role(client, instructor_token):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """
    response = client.post(
        "/student/milestone_management/individual/1",
        headers={"Authentication-Token": instructor_token},
    )
    assert response.status_code == 403
