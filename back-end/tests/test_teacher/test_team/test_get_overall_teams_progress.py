from unittest.mock import patch, MagicMock
from flask import json


@patch("apis.teacher.team_management.fetch_commit_details")
@patch("apis.teacher.team_management.ai_client.chat.completions.create")
def test_get_overall_teams_progress_success(
    mock_ai_client, mock_fetch_commit_details, client, instructor_token
):
    ai_response = {
        "teams": [
            {
                "team_name": "Team Alpha",
                "rank": 1,
                "status": "on_track",
                "reason": "High progress with consistent GitHub activity.",
            }
        ]
    }
    mock_choice_message_content = json.dumps(ai_response)

    # Mock the AI client's completion response
    mock_choice = MagicMock()
    mock_choice.message.content = mock_choice_message_content

    mock_ai_client.return_value.choices = [mock_choice]

    # Mock GitHub stats
    mock_fetch_commit_details.return_value = {
        "total_commits": 10,
        "lines_of_code_added": 500,
        "lines_of_code_deleted": 100,
        "milestones": [],
    }

    response = client.get(
        "/teacher/team_management/overall",
        headers={"Authentication-Token": instructor_token},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["team_name"] == "Team Alpha"
    assert data[0]["rank"] == 1
    assert data[0]["status"] == "on_track"


def test_get_overall_teams_progress_unauthorized(client):
    response = client.get("/teacher/team_management/overall")
    assert response.status_code == 403


@patch("apis.teacher.team_management.ai_client.chat.completions.create")
def test_get_overall_teams_progress_ai_failure(
    mock_ai_client, client, instructor_token
):
    mock_ai_client.side_effect = Exception("AI service failed")

    response = client.get(
        "/teacher/team_management/overall",
        headers={"Authentication-Token": instructor_token},
    )
    assert response.status_code == 500
    assert "AI service failed" in response.get_data(as_text=True)


@patch("apis.teacher.team_management.fetch_commit_details")
def test_get_overall_teams_progress_no_github_stats(
    mock_fetch_commit_details, client, instructor_token
):
    mock_fetch_commit_details.return_value = {
        "total_commits": 0,
        "lines_of_code_added": 0,
        "lines_of_code_deleted": 0,
        "milestones": [],
    }

    response = client.get(
        "/teacher/team_management/overall",
        headers={"Authentication-Token": instructor_token},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["team_name"] == "Team Alpha"
    assert data[0]["progress"] == 0


@patch("apis.teacher.team_management.db.session.query")
def test_get_overall_teams_progress_internal_error(
    mock_db_query, client, instructor_token
):
    mock_db_query.side_effect = Exception("Database error")

    response = client.get(
        "/teacher/team_management/overall",
        headers={"Authentication-Token": instructor_token},
    )
    assert response.status_code == 500
    assert "Database error" in response.get_data(as_text=True)
