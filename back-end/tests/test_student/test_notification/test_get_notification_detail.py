from unittest.mock import patch
from datetime import datetime, timezone


@patch("apis.student.notifications.UserNotifications.query")
@patch("apis.student.notifications.db.session.commit")
def test_get_notification_detail_success(
    mock_commit, mock_query, client, student_token
):
    """
    Test successful retrieval of notification details and marking it as read.
    """
    mock_notification = type(
        "MockUserNotifications",
        (),
        {
            "notifications": type(
                "MockNotifications",
                (),
                {
                    "id": 1,
                    "title": "Test Notification",
                    "message": "This is a test message.",
                    "type": type("MockType", (object,), {"value": "MILESTONE_UPDATE"}),
                    "created_at": datetime(2024, 11, 23, 12, 0, 0, tzinfo=timezone.utc),
                },
            ),
            "read_at": None,
        },
    )
    mock_query.filter_by.return_value.first.return_value = mock_notification

    response = client.get(
        "/student/notifications/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "id" in data
    assert "title" in data
    assert data["title"] == "Test Notification"
    assert "message" in data
    assert data["message"] == "This is a test message."
    assert "type" in data
    assert data["type"] == "MILESTONE_UPDATE"
    assert "created_at" in data
    assert data["created_at"] == "Sat, 23 Nov 2024 12:00:00 GMT"
    assert "read_at" in data
    assert data["read_at"] is None

    mock_commit.assert_called_once()


@patch("apis.student.notifications.UserNotifications.query")
def test_get_notification_detail_not_found(mock_query, client, student_token):
    """
    Test 404 response when the notification does not exist or the user cannot access it.
    """
    mock_query.filter_by.return_value.first.return_value = None

    response = client.get(
        "/student/notifications/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "errors" in data["response"]
    assert "Notification not found or access denied." in data["response"]["errors"]


def test_get_notification_detail_invalid_role(client, ta_token):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """
    response = client.get(
        "/student/notifications/1",
        headers={"Authentication-Token": ta_token},
    )

    assert response.status_code == 403


@patch("apis.student.notifications.UserNotifications.query")
def test_get_notification_detail_internal_server_error(
    mock_query, client, student_token
):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_query.filter_by.return_value.first.side_effect = Exception("Unexpected error")

    response = client.get(
        "/student/notifications/1",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert (
        "An unexpected error occurred. Try again later."
        in data["response"]["errors"][0]
    )
