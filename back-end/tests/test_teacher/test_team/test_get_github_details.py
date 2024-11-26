from unittest.mock import patch, MagicMock


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.fetch_commit_details")
def test_get_github_details_success(
    mock_fetch_commit_details,
    mock_get_single_team_under_user,
    client,
    instructor_token,
):
    """
    Test successful retrieval of GitHub details for a team.
    """
    mock_get_single_team_under_user.return_value = type(
        "Team",
        (),
        {
            "github_repo_url": "https://github.com/example/repo",
            "name": "Team Alpha",
            "members": [],
        },
    )
    mock_fetch_commit_details.return_value = {
        "total_commits": 42,
        "lines_of_code_added": 1500,
        "lines_of_code_deleted": 500,
        "milestones": [{"id": 1, "title": "Milestone 1", "commits": 20}],
    }

    response = client.get(
        "/teacher/team_management/individual/github/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Team Alpha"
    assert data["github_repo_url"] == "https://github.com/example/repo"
    assert data["total_commits"] == 42
    assert data["lines_of_code_added"] == 1500
    assert data["lines_of_code_deleted"] == 500
    assert len(data["milestones"]) == 1
    assert data["milestones"][0]["id"] == 1
    assert data["milestones"][0]["title"] == "Milestone 1"
    assert data["milestones"][0]["commits"] == 20


@patch("apis.teacher.team_management.get_single_team_under_user")
def test_get_github_details_team_not_found(
    mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 404 response when the team is not found.
    """
    mock_get_single_team_under_user.return_value = None

    response = client.get(
        "/teacher/team_management/individual/github/999",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "Team not found" in data["response"]["errors"][0]


@patch("apis.teacher.team_management.get_single_team_under_user")
def test_get_github_details_no_github_url(
    mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 404 response when the team does not have a GitHub URL.
    """
    mock_get_single_team_under_user.return_value = MagicMock(
        github_repo_url=None, members=[]
    )

    response = client.get(
        "/teacher/team_management/individual/github/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "No GitHub repository URL found" in data["response"]["errors"][0]


@patch("apis.teacher.team_management.get_single_team_under_user")
def test_get_github_details_invalid_user_id(
    mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 400 response when the user ID is invalid.
    """
    mock_get_single_team_under_user.return_value = MagicMock()

    response = client.get(
        "/teacher/team_management/individual/github/1?user_id=invalid",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "User id must be integer." in data["response"]["errors"][0]


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.fetch_commit_details")
def test_get_github_details_fetch_error(
    mock_fetch_commit_details, mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 502 response when fetching from GitHub fails.
    """
    mock_get_single_team_under_user.return_value = MagicMock(
        github_repo_url="https://github.com/example/repo", members=[]
    )
    mock_fetch_commit_details.return_value = {
        "status": "error",
        "message": "GitHub API failed.",
    }

    response = client.get(
        "/teacher/team_management/individual/github/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 502
    data = response.get_json()
    assert "GitHub API failed." in data["response"]["errors"][0]


def test_get_github_details_invalid_role(client, student_token):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """
    response = client.get(
        "/teacher/team_management/individual/github/1",
        headers={"Authentication-Token": student_token},
    )
    assert response.status_code == 403


@patch("apis.teacher.team_management.get_single_team_under_user")
def test_get_github_details_internal_server_error(
    mock_get_single_team_under_user, client, instructor_token
):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_get_single_team_under_user.side_effect = Exception("Unexpected error")

    response = client.get(
        "/teacher/team_management/individual/github/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Unexpected error" in data["response"]["errors"][0]
