from unittest.mock import patch


@patch("apis.student.notifications.NotificationPreferences.query")
def test_get_notification_preferences_success(mock_query, client, student_token):
    """
    Test successful retrieval of notification preferences.
    """
    mock_preferences = type(
        "MockPreferences",
        (),
        {
            "email_deadline_notifications": True,
            "in_app_deadline_notifications": False,
            "email_feedback_notifications": True,
            "in_app_feedback_notifications": False,
        },
    )
    mock_query.filter_by.return_value.first.return_value = mock_preferences

    response = client.get(
        "/student/notifications/preferences",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "email_deadline_notifications" in data
    assert data["email_deadline_notifications"] is True
    assert "in_app_deadline_notifications" in data
    assert data["in_app_deadline_notifications"] is False
    assert "email_feedback_notifications" in data
    assert data["email_feedback_notifications"] is True
    assert "in_app_feedback_notifications" in data
    assert data["in_app_feedback_notifications"] is False


@patch("apis.student.notifications.NotificationPreferences.query")
def test_get_notification_preferences_not_found(mock_query, client, student_token):
    """
    Test 404 response when no notification preferences are found for the user.
    """
    mock_query.filter_by.return_value.first.return_value = None

    response = client.get(
        "/student/notifications/preferences",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Notification preferences not found." in data["response"]["errors"]


@patch("apis.student.notifications.NotificationPreferences.query")
def test_get_notification_preferences_internal_server_error(
    mock_query, client, student_token
):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_query.filter_by.return_value.first.side_effect = Exception("Unexpected error")

    response = client.get(
        "/student/notifications/preferences",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Unexpected error" in data["response"]["errors"][0]


def test_get_notification_preferences_invalid_role(client, ta_token):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """

    response = client.get(
        "/student/notifications/preferences",
        headers={"Authentication-Token": ta_token},
    )

    assert response.status_code == 403
