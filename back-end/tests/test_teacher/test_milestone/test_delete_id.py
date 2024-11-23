from unittest.mock import patch


@patch("apis.teacher.milestone_management.Milestones.query")
@patch("apis.teacher.milestone_management.db.session.delete")
@patch("apis.teacher.milestone_management.db.session.commit")
def test_delete_milestone_success(
    mock_commit, mock_delete, mock_query, client, instructor_token
):
    """
    Test successful deletion of a milestone.
    """
    mock_query.get.return_value = "Mock Milestone Object"

    response = client.delete(
        "/teacher/milestone_management/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Milestone is deleted"
    mock_delete.assert_called_once_with("Mock Milestone Object")
    mock_commit.assert_called_once()


@patch("apis.teacher.milestone_management.Milestones.query")
def test_delete_milestone_not_found(mock_query, client, instructor_token):
    """
    Test 404 response when the milestone does not exist.
    """
    mock_query.get.return_value = None

    response = client.delete(
        "/teacher/milestone_management/999",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Milestone not found." in data["response"]["errors"]


def test_delete_milestone_invalid_role(client, ta_token):
    """
    Test 403 response when a user without the required role tries to delete a milestone.
    """

    response = client.delete(
        "/teacher/milestone_management/1",
        headers={"Authentication-Token": ta_token},
    )

    assert response.status_code == 403


@patch("apis.teacher.milestone_management.Milestones.query")
def test_delete_milestone_internal_server_error(mock_query, client, instructor_token):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_query.get.side_effect = Exception("Unexpected error")

    response = client.delete(
        "/teacher/milestone_management/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Unexpected error" in data["response"]["errors"][0]
