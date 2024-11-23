from unittest.mock import patch, MagicMock


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Milestones.query")
@patch("apis.student.milestone_management.db.session.query")
def test_get_milestone_details_success(
    mock_query, mock_milestones_query, mock_get_team_id, client, student_token
):
    """
    Test successful retrieval of milestone details.
    """

    mock_get_team_id.return_value = 1

    mock_milestone = MagicMock(
        id=1,
        title="Milestone 1",
        description="Milestone Description",
        deadline="2024-12-31",
        created_at="2024-01-01",
        task_milestones=[
            MagicMock(id=101, description="Task 1"),
            MagicMock(id=102, description="Task 2"),
        ],
    )
    mock_milestones_query.get.return_value = mock_milestone

    mock_submission_1 = MagicMock(
        task_id=101, feedback="Great work", feedback_time="2024-11-20"
    )
    mock_query.return_value.filter.return_value.filter.return_value.first.side_effect = [
        mock_submission_1,
        None,
    ]
    response = client.get(
        "/student/milestone_management/individual/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1
    assert len(data["tasks"]) == 2
    assert data["tasks"][0]["task_id"] == 101
    assert data["tasks"][0]["is_completed"] is True
    assert data["tasks"][1]["is_completed"] is False


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Milestones.query")
def test_get_milestone_details_milestone_not_found(
    mock_milestones, mock_get_team_id, client, student_token
):
    """
    Test 404 error when the milestone does not exist.
    """
    mock_get_team_id.return_value = 1
    mock_milestones.get.return_value = None

    response = client.get(
        "/student/milestone_management/individual/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "Milestone or team not found." in data["response"]["errors"][0]


@patch("apis.student.milestone_management.get_team_id")
@patch("apis.student.milestone_management.Milestones.query")
def test_get_milestone_details_team_not_found(
    mock_milestones, mock_get_team_id, client, student_token
):
    """
    Test 404 error when the team does not exist.
    """
    mock_get_team_id.return_value = None
    mock_milestones.get.return_value = MagicMock()

    response = client.get(
        "/student/milestone_management/individual/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "Milestone or team not found." in data["response"]["errors"][0]


@patch("apis.student.milestone_management.get_team_id")
def test_get_milestone_details_internal_error(mock_get_team_id, client, student_token):
    """
    Test 500 error due to unexpected exception.
    """
    mock_get_team_id.side_effect = Exception("Unexpected error")

    response = client.get(
        "/student/milestone_management/individual/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 500


def test_get_milestone_invalid_role(client, instructor_token):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """
    response = client.get(
        "/student/milestone_management/individual/1",
        headers={"Authentication-Token": instructor_token},
    )
    assert response.status_code == 403
