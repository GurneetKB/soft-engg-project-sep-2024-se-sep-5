from unittest.mock import patch


def mock_milestone_data():
    class MockTask:
        def __init__(self, description):
            self.description = description

    class MockMilestone:
        def __init__(self, title, description, deadline, task_milestones):
            self.title = title
            self.description = description
            self.deadline = deadline
            self.task_milestones = task_milestones

    tasks = [
        MockTask(description="Task 1 description"),
        MockTask(description="Task 2 description"),
    ]
    return MockMilestone(
        title="Milestone Title",
        description="Milestone Description",
        deadline="2024-12-31",
        task_milestones=tasks,
    )


@patch("apis.teacher.milestone_management.Milestones.query")
def test_get_milestone_success(mock_query, client, instructor_token):
    """
    Test successful retrieval of milestone details.
    """
    mock_query.get.return_value = mock_milestone_data()

    response = client.get(
        "/teacher/milestone_management/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "title" in data
    assert data["title"] == "Milestone Title"
    assert data["description"] == "Milestone Description"
    assert data["deadline"] == "2024-12-31"
    assert "tasks" in data
    assert len(data["tasks"]) == 2
    assert data["tasks"][0]["description"] == "Task 1 description"


@patch("apis.teacher.milestone_management.Milestones.query")
def test_get_milestone_not_found(mock_query, client, instructor_token):
    """
    Test 404 response when the milestone is not found.
    """
    mock_query.get.return_value = None

    response = client.get(
        "/teacher/milestone_management/999",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Milestone not found." in data["response"]["errors"][0]


@patch("apis.teacher.milestone_management.Milestones.query")
def test_get_milestone_invalid_role(mock_query, client, student_token):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """
    mock_query.get.return_value = mock_milestone_data()

    response = client.get(
        "/teacher/milestone_management/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 403


@patch("apis.teacher.milestone_management.Milestones.query")
def test_get_milestone_internal_server_error(mock_query, client, instructor_token):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_query.get.side_effect = Exception("Unexpected error")

    response = client.get(
        "/teacher/milestone_management/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert (
        "An unexpected error occurred. Try again later."
        in data["response"]["errors"][0]
    )
