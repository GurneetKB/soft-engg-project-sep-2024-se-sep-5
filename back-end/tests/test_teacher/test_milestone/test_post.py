from unittest.mock import patch
from datetime import datetime, timedelta, timezone


def future_deadline():
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    return future_time.strftime("%a, %d %b %Y %H:%M:%S %Z")


@patch("apis.teacher.milestone_management.db.session.add")
@patch("apis.teacher.milestone_management.db.session.commit")
def test_create_milestone_success(mock_commit, mock_add, client, instructor_token):
    """
    Test successful creation of a milestone.
    """
    payload = {
        "title": "Milestone 1",
        "description": "Complete project setup",
        "deadline": future_deadline(),
        "tasks": [
            {"description": "Task 1"},
            {"description": "Task 2"},
        ],
    }
    response = client.post(
        "/teacher/milestone_management",
        json=payload,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Milestone published successfully."
    assert mock_add.call_count == 3  # 1 for milestone, 2 for tasks
    mock_commit.assert_called_once()


def test_create_milestone_missing_title(client, instructor_token):
    """
    Test creation fails when title is missing.
    """
    payload = {
        "description": "Complete project setup",
        "deadline": future_deadline(),
        "tasks": [{"description": "Task 1"}],
    }
    response = client.post(
        "/teacher/milestone_management",
        json=payload,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "Title is required and must be a string." in data["response"]["errors"]


def test_create_milestone_invalid_deadline_format(client, instructor_token):
    """
    Test creation fails when the deadline is in an invalid format.
    """
    payload = {
        "title": "Milestone 1",
        "description": "Complete project setup",
        "deadline": "invalid date",
        "tasks": [{"description": "Task 1"}],
    }
    response = client.post(
        "/teacher/milestone_management",
        json=payload,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "Deadline must be a valid GMT format datetime." in data["response"]["errors"]


def test_create_milestone_past_deadline(client, instructor_token):
    """
    Test creation fails when the deadline is in the past.
    """
    past_deadline = (datetime.now(timezone.utc) - timedelta(days=1)).strftime(
        "%a, %d %b %Y %H:%M:%S %Z"
    )
    payload = {
        "title": "Milestone 1",
        "description": "Complete project setup",
        "deadline": past_deadline,
        "tasks": [{"description": "Task 1"}],
    }
    response = client.post(
        "/teacher/milestone_management",
        json=payload,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert (
        "Deadline must be set to a future date and time." in data["response"]["errors"]
    )


def test_create_milestone_invalid_tasks_format(client, instructor_token):
    """
    Test creation fails when tasks are not a list.
    """
    payload = {
        "title": "Milestone 1",
        "description": "Complete project setup",
        "deadline": future_deadline(),
        "tasks": "invalid format",
    }
    response = client.post(
        "/teacher/milestone_management",
        json=payload,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "Tasks must be a list." in data["response"]["errors"]


def test_create_milestone_invalid_task_description(client, instructor_token):
    """
    Test creation fails when a task description is missing or not a string.
    """
    payload = {
        "title": "Milestone 1",
        "description": "Complete project setup",
        "deadline": future_deadline(),
        "tasks": [
            {"invalid_key": "Task 1"},
            {"description": 123},
        ],
    }
    response = client.post(
        "/teacher/milestone_management",
        json=payload,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert (
        "Task 1 must be an object with a 'description' field."
        in data["response"]["errors"]
    )
    assert "Description in Task 2 must be a string." in data["response"]["errors"]


def test_create_milestone_unauthorized(client, ta_token):
    """
    Test creation fails when the user does not have the required role.
    """
    response = client.post(
        "/teacher/milestone_management",
        headers={"Authentication-Token": ta_token},
    )

    assert response.status_code == 403


@patch("apis.teacher.milestone_management.db.session.commit")
def test_create_milestone_internal_server_error(mock_commit, client, instructor_token):
    """
    Test 500 response when an internal server error occurs, such as a database failure.
    """
    mock_commit.side_effect = Exception("Database error")

    milestone_data = {
        "title": "New Milestone",
        "description": "This is a new milestone for the project.",
        "deadline": "Mon, 25 Nov 2024 10:00:00 GMT",
        "tasks": [
            {"description": "Task 1 for milestone"},
            {"description": "Task 2 for milestone"},
        ],
    }

    response = client.post(
        "/teacher/milestone_management",
        json=milestone_data,
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Database error" in data["response"]["errors"]
