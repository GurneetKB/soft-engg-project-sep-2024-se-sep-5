from unittest.mock import patch, MagicMock


@patch("apis.student.milestone_management.Milestones.query")
def test_get_milestones_success(mock_query, client, student_token):
    """
    Test successful retrieval of all milestones.
    """
    mock_milestones = [
        MagicMock(id=1, title="Milestone 1"),
        MagicMock(id=2, title="Milestone 2"),
    ]
    mock_query.all.return_value = mock_milestones

    response = client.get(
        "/student/milestone_management/individual",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["milestones"]) == 2
    assert data["milestones"][0]["id"] == 1
    assert data["milestones"][0]["title"] == "Milestone 1"
    assert data["milestones"][1]["id"] == 2
    assert data["milestones"][1]["title"] == "Milestone 2"


@patch("apis.student.milestone_management.Milestones.query")
def test_get_milestones_empty(mock_query, client, student_token):
    """
    Test 200 response when no milestones are available.
    """
    mock_query.all.return_value = []

    response = client.get(
        "/student/milestone_management/individual",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["milestones"]) == 0
    assert "milestones" in data


@patch("apis.student.milestone_management.Milestones.query")
def test_get_milestones_internal_server_error(mock_query, client, student_token):
    """
    Test 500 response when there is a database query failure.
    """
    mock_query.all.side_effect = Exception("Database error")

    response = client.get(
        "/student/milestone_management/individual",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 500


def test_get_milestones_invalid_role(client, instructor_token):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """
    response = client.get(
        "/student/milestone_management/individual",
        headers={"Authentication-Token": instructor_token},
    )
    assert response.status_code == 403
