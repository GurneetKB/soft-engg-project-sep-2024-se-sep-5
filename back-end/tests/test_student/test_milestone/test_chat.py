from datetime import datetime
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_milestones():
    mock_milestone_1 = MagicMock()
    mock_milestone_1.title = "Milestone 1"
    mock_milestone_1.description = "Description for milestone 1"
    mock_milestone_1.deadline = datetime.now()
    mock_milestone_1.task_milestones = [
        MagicMock(description="Task 1"),
        MagicMock(description="Task 2"),
    ]

    mock_milestone_2 = MagicMock()
    mock_milestone_2.title = "Milestone 2"
    mock_milestone_2.description = "Description for milestone 2"
    mock_milestone_2.deadline = datetime.now()
    mock_milestone_2.task_milestones = [
        MagicMock(description="Task A"),
        MagicMock(description="Task B"),
    ]

    return [mock_milestone_1, mock_milestone_2]


@patch("apis.student.milestone_management.db.session.query")
@patch("apis.student.milestone_management.ai_client.chat.completions.create")
def test_chat_success(
    mock_ai_client, mock_db_query, client, student_token, mock_milestones
):
    """
    Test successful chat completion with valid input and milestones.
    """
    mock_db_query.return_value.all.return_value = mock_milestones

    mock_ai_client.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="AI response"))]
    )

    response = client.post(
        "/student/chat",
        json={"message": "What are the tasks for Milestone 1?"},
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "analysis" in data
    assert data["analysis"] == "AI response"


def test_chat_missing_message(client, student_token):
    """
    Test 400 response when the user message is missing.
    """
    response = client.post(
        "/student/chat",
        json={},
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "message" in data["response"]["errors"][0]
    assert data["response"]["errors"][0] == "User message can not be empty"


def test_chat_invalid_role(client, instructor_token):
    """
    Test 403 response when an unauthorized user tries to access the chat.
    """
    response = client.post(
        "/student/chat",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 403


@patch("apis.student.milestone_management.db.session.query")
def test_chat_internal_server_error(mock_db_query, client, student_token):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_db_query.side_effect = Exception("Database error")

    response = client.post(
        "/student/chat",
        json={"message": "What is the deadline for Milestone 1?"},
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert (
        "An unexpected error occurred. Try again later."
        in data["response"]["errors"][0]
    )


@patch("apis.student.milestone_management.db.session.query")
@patch("apis.student.milestone_management.ai_client.chat.completions.create")
def test_chat_no_milestones(mock_ai_client, mock_db_query, client, student_token):
    """
    Test chat behavior when no milestones are available in the database.
    """
    mock_db_query.return_value.all.return_value = []

    mock_ai_client.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="No milestones available"))]
    )

    response = client.post(
        "/student/chat",
        json={"message": "Tell me about milestones"},
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "analysis" in data
    assert data["analysis"] == "No milestones available"
