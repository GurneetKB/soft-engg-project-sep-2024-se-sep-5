from unittest.mock import patch, MagicMock


@patch("apis.teacher.milestone_management.Milestones.query")
@patch("apis.teacher.milestone_management.get_teams_under_user")
@patch("apis.teacher.milestone_management.db.session.query")
def test_get_all_milestones_success(
    mock_query,
    mock_get_teams_under_user,
    mock_milestones_query,
    client,
    instructor_token,
):
    """
    Test successful retrieval of all milestones and progress overview.
    """
    mock_milestone = MagicMock(
        id=1,
        title="Milestone 1",
        description="Complete initial tasks",
        deadline="2024-12-31",
        task_milestones=[MagicMock(id=101), MagicMock(id=102)],
    )
    mock_milestones_query.all.return_value = [mock_milestone]

    mock_team = MagicMock(id=1, members=["Student1", "Student2"])
    mock_get_teams_under_user.return_value = [mock_team]

    mock_query.return_value.join.return_value.filter.return_value.group_by.return_value.having.return_value.count.return_value = (
        1
    )

    response = client.get(
        "/teacher/milestone_management",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["no_of_teams"] == 1
    assert data["no_of_students"] == 2
    assert len(data["milestones"]) == 1
    assert data["milestones"][0]["id"] == 1
    assert data["milestones"][0]["completion_rate"] == 100.0


@patch("apis.teacher.milestone_management.Milestones.query")
@patch("apis.teacher.milestone_management.get_teams_under_user")
def test_get_all_milestones_no_teams(
    mock_get_teams_under_user, mock_milestones_query, client, instructor_token
):
    """
    Test case where the teacher has no teams under them.
    """
    mock_milestones_query.all.return_value = []
    mock_get_teams_under_user.return_value = []

    response = client.get(
        "/teacher/milestone_management",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["no_of_teams"] == 0
    assert data["no_of_students"] == 0
    assert data["milestones"] == []


@patch("apis.teacher.milestone_management.Milestones.query")
@patch("apis.teacher.milestone_management.get_teams_under_user")
@patch("apis.teacher.milestone_management.db.session.query")
def test_get_all_milestones_partial_completion(
    mock_query,
    mock_get_teams_under_user,
    mock_milestones_query,
    client,
    instructor_token,
):
    """
    Test case where only some teams have completed the milestone tasks.
    """
    mock_milestone = MagicMock(
        id=2,
        title="Milestone 2",
        description="Complete second tasks",
        deadline="2024-12-31",
        task_milestones=[MagicMock(id=201), MagicMock(id=202)],
    )
    mock_milestones_query.all.return_value = [mock_milestone]

    mock_team1 = MagicMock(id=1, members=["Student1", "Student2"])
    mock_team2 = MagicMock(id=2, members=["Student3"])
    mock_get_teams_under_user.return_value = [mock_team1, mock_team2]

    mock_query.return_value.join.return_value.filter.return_value.group_by.return_value.having.return_value.count.return_value = (
        1
    )

    response = client.get(
        "/teacher/milestone_management",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["no_of_teams"] == 2
    assert data["no_of_students"] == 3
    assert len(data["milestones"]) == 1
    assert data["milestones"][0]["completion_rate"] == 50.0


def test_get_all_milestones_unauthorized(client):
    """
    Test 403 error when an unauthorized user attempts to access the endpoint.
    """
    response = client.get("/teacher/milestone_management")

    assert response.status_code == 403


@patch("apis.teacher.milestone_management.Milestones.query")
def test_get_all_milestones_internal_server_error(
    mock_milestones_query, client, instructor_token
):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_milestones_query.all.side_effect = Exception("Unexpected error")

    response = client.get(
        "/teacher/milestone_management",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Unexpected error" in data["response"]["errors"][0]
