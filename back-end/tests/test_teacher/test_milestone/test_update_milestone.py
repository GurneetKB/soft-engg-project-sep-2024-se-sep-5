from unittest.mock import patch
from datetime import datetime, timezone, timedelta


def mock_milestone_object():
    class MockTask:
        def __init__(self, description):
            self.description = description

    class MockMilestone:
        def __init__(self, id, title, description, deadline, task_milestones):
            self.id = id
            self.title = title
            self.description = description
            self.deadline = deadline
            self.task_milestones = task_milestones

    tasks = [MockTask(description="Task 1"), MockTask(description="Task 2")]
    return MockMilestone(
        id=1,
        title="Original Title",
        description="Original Description",
        deadline=datetime.now(timezone.utc) + timedelta(days=10),
        task_milestones=tasks,
    )


@patch("apis.teacher.milestone_management.Milestones.query.filter_by")
@patch("apis.teacher.milestone_management.db.session.commit")
def test_update_milestone_success(
    mock_commit, mock_filter_by, client, instructor_token
):
    """
    Test successful update of a milestone.
    """
    mock_filter_by.return_value.first.return_value = mock_milestone_object()
    updated_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "deadline": (datetime.now(timezone.utc) + timedelta(days=15)).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        ),
        "tasks": [{"description": "Updated Task 1"}, {"description": "Updated Task 2"}],
    }

    response = client.put(
        "/teacher/milestone_management/1",
        headers={"Authentication-Token": instructor_token},
        json=updated_data,
    )

    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Milestone updated successfully."
    mock_commit.assert_called_once()


@patch("apis.teacher.milestone_management.Milestones.query.filter_by")
def test_update_milestone_not_found(mock_filter_by, client, instructor_token):
    """
    Test 404 response when the milestone is not found.
    """
    mock_filter_by.return_value.first.return_value = None

    response = client.put(
        "/teacher/milestone_management/999",
        headers={"Authentication-Token": instructor_token},
        json={"title": "New Title"},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Milestone not found." in data["response"]["errors"]


@patch("apis.teacher.milestone_management.Milestones.query.filter_by")
def test_update_milestone_invalid_deadline(mock_filter_by, client, instructor_token):
    """
    Test 400 response when an invalid deadline is provided.
    """
    mock_filter_by.return_value.first.return_value = mock_milestone_object()
    invalid_data = {"deadline": "Invalid Deadline Format"}

    response = client.put(
        "/teacher/milestone_management/1",
        headers={"Authentication-Token": instructor_token},
        json=invalid_data,
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Deadline must be a valid GMT format datetime." in data["response"]["errors"]


@patch("apis.teacher.milestone_management.Milestones.query.filter_by")
def test_update_milestone_invalid_task(mock_filter_by, client, instructor_token):
    """
    Test 400 response when an invalid task format is provided.
    """
    mock_filter_by.return_value.first.return_value = mock_milestone_object()
    invalid_data = {"tasks": [{"invalid_field": "Task without description"}]}

    response = client.put(
        "/teacher/milestone_management/1",
        headers={"Authentication-Token": instructor_token},
        json=invalid_data,
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data["response"]
    assert (
        "Task 1 must have a non-empty 'description' field."
        in data["response"]["errors"]
    )


@patch("apis.teacher.milestone_management.Milestones.query.filter_by")
@patch("apis.teacher.milestone_management.db.session.commit")
def test_update_milestone_partial_update(
    mock_commit, mock_filter_by, client, instructor_token
):
    """
    Test successful partial update of a milestone (e.g., only updating the title).
    """
    mock_filter_by.return_value.first.return_value = mock_milestone_object()
    partial_data = {"title": "Partially Updated Title"}

    response = client.put(
        "/teacher/milestone_management/1",
        headers={"Authentication-Token": instructor_token},
        json=partial_data,
    )

    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Milestone updated successfully."
    mock_commit.assert_called_once()


def test_update_milestone_invalid_role(client, ta_token):
    """
    Test 403 response when a user without the required role tries to update a milestone.
    """
    response = client.put(
        "/teacher/milestone_management/1",
        headers={"Authentication-Token": ta_token},
    )

    assert response.status_code == 403


@patch("apis.teacher.milestone_management.db.session.commit")
def test_update_milestone_internal_server_error(mock_commit, client, instructor_token):
    """
    Test 500 response when an internal server error occurs, such as a database failure.
    """
    mock_commit.side_effect = Exception("Database error")

    response = client.put(
        "/teacher/milestone_management/1",
        json={"title": "New Milestone"},
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert (
        "An unexpected error occurred. Try again later." in data["response"]["errors"]
    )
