from unittest.mock import patch, MagicMock, mock_open


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Submissions.query")
@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data=b"Mocked PDF content")
@patch("apis.teacher.team_management.PdfReader")
@patch("apis.teacher.team_management.ai_client.chat.completions.create")
def test_get_ai_analysis_success(
    mock_ai_client,
    mock_pdf_reader,
    mock_file,
    mock_path_exists,
    mock_submissions_query,
    mock_get_single_team,
    client,
    instructor_token,
    mock_team,
):
    """
    Test successful AI analysis response for a valid team and task.
    """
    mock_get_single_team.return_value = type("Teams", (), mock_team)

    mock_filter_by = MagicMock()
    mock_filter_by.first.return_value = MagicMock(
        documents=MagicMock(file_url="/path/to/file.pdf"),
        task=MagicMock(
            description="Task description",
            milestone=MagicMock(description="Milestone description"),
        ),
    )
    mock_submissions_query.filter_by.return_value = mock_filter_by

    mock_path_exists.return_value = True

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Mocked PDF content"
    mock_pdf_reader.return_value.pages = [mock_page]

    mock_ai_client.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="AI Analysis result"))]
    )

    response = client.get(
        "/teacher/team_management/individual/ai_analysis/1/1",
        headers={"Authentication-Token": instructor_token},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "analysis" in data
    assert data["analysis"] == "AI Analysis result"


@patch("apis.teacher.team_management.get_single_team_under_user")
def test_get_ai_analysis_team_not_found(mock_get_single_team, client, instructor_token):
    """
    Test 404 response when the team is not found.
    """
    mock_get_single_team.return_value = None

    response = client.get(
        "/teacher/team_management/individual/ai_analysis/999/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "Team not found" in data["response"]["errors"][0]


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Submissions.query")
def test_get_ai_analysis_submission_not_found(
    mock_submissions_query, mock_get_single_team, client, instructor_token, mock_team
):
    """
    Test 404 response when the submission or document is not found.
    """
    mock_get_single_team.return_value = type("Teams", (), mock_team)

    mock_filter_by = MagicMock()
    mock_filter_by.first.return_value = None
    mock_submissions_query.filter_by.return_value = mock_filter_by

    response = client.get(
        "/teacher/team_management/individual/ai_analysis/1/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "Submission or document not found" in data["response"]["errors"][0]


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Submissions.query")
@patch("os.path.exists")
def test_get_ai_analysis_file_not_found(
    mock_path_exists,
    mock_submissions_query,
    mock_get_single_team,
    client,
    instructor_token,
    mock_team,
):
    """
    Test 404 response when the document file does not exist.
    """
    mock_get_single_team.return_value = type("Teams", (), mock_team)

    mock_filter_by = MagicMock()
    mock_filter_by.first.return_value = MagicMock(
        documents=MagicMock(file_url="/path/to/nonexistent_file.pdf")
    )
    mock_submissions_query.filter_by.return_value = mock_filter_by

    mock_path_exists.return_value = False

    response = client.get(
        "/teacher/team_management/individual/ai_analysis/1/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "File not found" in data["response"]["errors"][0]


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Submissions.query")
@patch("os.path.exists")
@patch("apis.teacher.team_management.PdfReader")
def test_get_ai_analysis_document_read_error(
    mock_pdf_reader,
    mock_path_exists,
    mock_submissions_query,
    mock_get_single_team,
    client,
    instructor_token,
    mock_team,
):
    """
    Test 500 response when an error occurs while reading the document.
    """
    mock_get_single_team.return_value = type("Teams", (), mock_team)

    mock_filter_by = MagicMock()
    mock_filter_by.first.return_value = MagicMock(
        documents=MagicMock(file_url="/path/to/file.pdf")
    )
    mock_submissions_query.filter_by.return_value = mock_filter_by

    mock_path_exists.return_value = True
    mock_pdf_reader.side_effect = Exception("PDF read error")

    response = client.get(
        "/teacher/team_management/individual/ai_analysis/1/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "Error reading document:" in data["response"]["errors"][0]


@patch("apis.teacher.team_management.get_single_team_under_user")
@patch("apis.teacher.team_management.Submissions.query")
@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data=b"Mocked PDF content")
@patch("apis.teacher.team_management.PdfReader")
@patch("apis.teacher.team_management.ai_client.chat.completions.create")
def test_get_ai_analysis_ai_error(
    mock_ai_client,
    mock_pdf_reader,
    mock_file,
    mock_path_exists,
    mock_submissions_query,
    mock_get_single_team,
    client,
    instructor_token,
    mock_team,
):
    """
    Test 500 response when an error occurs during AI analysis.
    """
    mock_get_single_team.return_value = type("Teams", (), mock_team)

    mock_filter_by = MagicMock()
    mock_filter_by.first.return_value = MagicMock(
        documents=MagicMock(file_url="/path/to/file.pdf"),
        task=MagicMock(
            description="Task description",
            milestone=MagicMock(description="Milestone description"),
        ),
    )
    mock_submissions_query.filter_by.return_value = mock_filter_by

    mock_path_exists.return_value = True

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Mocked PDF content"
    mock_pdf_reader.return_value.pages = [mock_page]

    mock_ai_client.side_effect = Exception("AI analysis failed")

    response = client.get(
        "/teacher/team_management/individual/ai_analysis/1/1",
        headers={"Authentication-Token": instructor_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "AI analysis error: AI analysis failed" in data["response"]["errors"][0]


def test_get_ai_analysis_invalid_role(client, student_token):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """
    response = client.get(
        "/teacher/team_management/individual/ai_analysis/1/1",
        headers={"Authentication-Token": student_token},
    )
    assert response.status_code == 403
