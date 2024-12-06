import pytest
from unittest.mock import patch


@pytest.fixture
def mock_preferences():
    return type(
        "MockPreferences",
        (),
        {
            "email_deadline_notifications": True,
            "in_app_deadline_notifications": False,
            "email_feedback_notifications": True,
            "in_app_feedback_notifications": False,
        },
    )


@patch("apis.student.notifications.NotificationPreferences.query")
@patch("apis.teacher.milestone_management.db.session.commit")
def test_set_notification_preferences_success(
    mock_commit, mock_query, client, student_token, mock_preferences
):
    """
    Test successful update of notification preferences.
    """

    mock_query.filter_by.return_value.first.return_value = mock_preferences

    new_preferences = {
        "email_deadline_notifications": False,
        "in_app_deadline_notifications": True,
        "email_feedback_notifications": False,
        "in_app_feedback_notifications": True,
    }

    response = client.put(
        "/student/notifications/preferences",
        json=new_preferences,
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Notification preferences updated successfully."

    mock_commit.assert_called_once()
    assert mock_preferences.email_deadline_notifications is False
    assert mock_preferences.in_app_deadline_notifications is True
    assert mock_preferences.email_feedback_notifications is False
    assert mock_preferences.in_app_feedback_notifications is True


@patch("apis.student.notifications.NotificationPreferences.query")
def test_set_notification_preferences_invalid_boolean(
    mock_query, client, student_token, mock_preferences
):
    """
    Test 400 response when invalid boolean values are provided in the request.
    """

    mock_query.filter_by.return_value.first.return_value = mock_preferences

    invalid_preferences = {
        "email_deadline_notifications": "true",
        "in_app_deadline_notifications": "false",
        "email_feedback_notifications": "yes",
        "in_app_feedback_notifications": "no",
    }

    response = client.put(
        "/student/notifications/preferences",
        json=invalid_preferences,
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data["response"]
    assert (
        "email_deadline_notifications must be a boolean value."
        in data["response"]["errors"]
    )


@patch("apis.student.notifications.NotificationPreferences.query")
def test_set_notification_preferences_not_found(mock_query, client, student_token):
    """
    Test 404 response when notification preferences are not found for the user.
    """
    mock_query.filter_by.return_value.first.return_value = None

    response = client.put(
        "/student/notifications/preferences",
        json={"email_deadline_notifications": True},
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Notification preferences not found." in data["response"]["errors"]


def test_set_notification_preferences_invalid_role(client, ta_token):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """

    response = client.put(
        "/student/notifications/preferences",
        json={"email_deadline_notifications": True},
        headers={"Authentication-Token": ta_token},
    )

    assert response.status_code == 403


@patch("apis.student.notifications.NotificationPreferences.query")
def test_set_notification_preferences_internal_server_error(
    mock_query, client, student_token
):
    """
    Test 500 response when an internal server error occurs (e.g., database failure).
    """
    mock_query.filter_by.return_value.first.side_effect = Exception("Unexpected error")

    response = client.put(
        "/student/notifications/preferences",
        json={"email_deadline_notifications": True},
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert (
        "An unexpected error occurred. Try again later."
        in data["response"]["errors"][0]
    )
