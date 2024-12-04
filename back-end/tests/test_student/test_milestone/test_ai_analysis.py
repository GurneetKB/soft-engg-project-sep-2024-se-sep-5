from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timezone, timedelta
import pytest


@pytest.fixture
def mock_submission():
    """
    Fixture to create a mock submission with associated task and milestone.

    This can be used across different tests to provide a consistent mock submission.
    """
    mock_document = MagicMock(file_url="test_document.pdf")
    mock_milestone = MagicMock(
        description="Milestone description",
        deadline=datetime.now(timezone.utc) + timedelta(days=1),
    )
    mock_task = MagicMock(description="Task description", milestone=mock_milestone)
    mock_submission = MagicMock(task=mock_task, documents=mock_document)

    return mock_submission


@pytest.fixture
def past_deadline_submission():
    """
    Fixture to create a mock submission with a past deadline.
    """
    mock_document = MagicMock(file_url="test_document.pdf")
    mock_milestone = MagicMock(
        description="Milestone description",
        deadline=datetime.now(timezone.utc) - timedelta(days=1),
    )
    mock_task = MagicMock(description="Task description", milestone=mock_milestone)
    mock_submission = MagicMock(task=mock_task, documents=mock_document)

    return mock_submission


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Submissions.query")
@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data=b"Mocked PDF content")
@patch("apis.student.milestone_management.PdfReader")
def test_get_ai_analysis_success(
    mock_pdf_reader,
    mock_file,
    mock_path_exists,
    mock_query,
    mock_get_team_id,
    client,
    student_token,
    mock_submission,
):
    """
    Test successful AI analysis.
    """
    mock_get_team_id.return_value = 1
    mock_query.filter_by.return_value.first.return_value = mock_submission
    mock_path_exists.return_value = True

    mock_ai_response = MagicMock()
    mock_ai_response.choices = [MagicMock(message=MagicMock(content="AI response"))]

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Mocked PDF content"
    mock_pdf_reader.return_value.pages = [mock_page]

    with patch(
        "apis.student.milestone_management.ai_client.chat.completions.create",
        return_value=mock_ai_response,
    ):
        response = client.get(
            "/student/milestone_management/individual/ai_analysis/1",
            headers={"Authentication-Token": student_token},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "analysis" in data
        assert data["analysis"] == "AI response"


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Submissions.query")
def test_get_ai_analysis_submission_not_found(
    mock_query, mock_get_team_id, client, student_token
):
    """
    Test 404 response when the submission or document is not found.
    """
    mock_get_team_id.return_value = 1
    mock_query.filter_by.return_value.first.return_value = None

    response = client.get(
        "/student/milestone_management/individual/ai_analysis/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Submission or document not found" in data["response"]["errors"][0]


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Submissions.query")
def test_get_ai_analysis_deadline_passed(
    mock_query, mock_get_team_id, client, student_token, past_deadline_submission
):
    """
    Test 400 response when the milestone deadline has passed.
    """
    mock_get_team_id.return_value = 1

    mock_query.filter_by.return_value.first.return_value = past_deadline_submission

    response = client.get(
        "/student/milestone_management/individual/ai_analysis/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Milestone Deadline Passed" in data["response"]["errors"][0]


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Submissions.query")
def test_get_ai_analysis_file_not_found(
    mock_query, mock_get_team_id, client, student_token, mock_submission
):
    """
    Test 404 response when the document file does not exist.
    """
    mock_get_team_id.return_value = 1

    mock_query.filter_by.return_value.first.return_value = mock_submission

    with patch("os.path.exists", return_value=False):
        response = client.get(
            "/student/milestone_management/individual/ai_analysis/1",
            headers={"Authentication-Token": student_token},
        )

        assert response.status_code == 404
        data = response.get_json()
        assert "errors" in data["response"]
        assert "File not found" in data["response"]["errors"][0]


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Submissions.query")
@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data=b"Mocked PDF content")
@patch("apis.student.milestone_management.PdfReader")
def test_get_ai_analysis_ai_error(
    mock_pdf_reader,
    mock_file,
    mock_path_exists,
    mock_query,
    mock_get_team_id,
    client,
    student_token,
    mock_submission,
):
    """
    Test 500 response when an AI analysis error occurs.
    """
    mock_get_team_id.return_value = 1

    mock_query.filter_by.return_value.first.return_value = mock_submission
    mock_path_exists.return_value = True

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Mocked PDF content"
    mock_pdf_reader.return_value.pages = [mock_page]

    with patch(
        "apis.student.milestone_management.ai_client.chat.completions.create",
        side_effect=Exception("AI error"),
    ):
        response = client.get(
            "/student/milestone_management/individual/ai_analysis/1",
            headers={"Authentication-Token": student_token},
        )

        assert response.status_code == 500
        data = response.get_json()
        assert "errors" in data["response"]
        assert "AI analysis error" in data["response"]["errors"][0]


def test_get_ai_analysis_invalid_role(client, instructor_token):
    """
    Test 403 response when an unauthorized user tries to access the endpoint.
    """
    response = client.get(
        "/student/milestone_management/individual/ai_analysis/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 403
