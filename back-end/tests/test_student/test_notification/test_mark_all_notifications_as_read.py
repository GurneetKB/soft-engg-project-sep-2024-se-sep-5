from unittest.mock import patch


@patch("apis.student.notifications.UserNotifications.query")
@patch("apis.student.notifications.db.session.commit")
def test_mark_all_notifications_as_read_success(
    mock_commit, mock_query, client, student_token
):
    """
    Test successful marking of all notifications as read.
    """
    mock_notifications = [
        type(
            "MockNotification",
            (object,),
            {
                "notifications": type(
                    "MockNotificationDetails",
                    (object,),
                    {
                        "id": 1,
                        "title": "Assignment Due",
                        "type": type("MockType", (object,), {"value": "DEADLINE"}),
                        "created_at": "2024-11-20T10:00:00Z",
                    },
                ),
                "read_at": None,
            },
        )(),
        type(
            "MockNotification",
            (object,),
            {
                "notifications": type(
                    "MockNotificationDetails",
                    (object,),
                    {
                        "id": 2,
                        "title": "New Milestone Released",
                        "type": type(
                            "MockType", (object,), {"value": "MILESTONE_UPDATE"}
                        ),
                        "created_at": "2024-11-19T14:30:00Z",
                    },
                ),
                "read_at": "2024-11-21T08:00:00Z",
            },
        )(),
    ]

    mock_query.filter_by.return_value.all.return_value = mock_notifications

    response = client.get(
        "/student/notifications/mark_all_as_read",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "All notifications marked as read."

    mock_commit.assert_called_once()


@patch("apis.student.notifications.UserNotifications.query")
def test_mark_all_notifications_as_read_no_unread(mock_query, client, student_token):
    """
    Test when there are no unread notifications.
    """
    mock_query.filter_by.return_value.all.return_value = []

    response = client.get(
        "/student/notifications/mark_all_as_read",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "All notifications marked as read."


def test_mark_all_notifications_as_read_invalid_role(client, ta_token):
    """
    Test 403 response when a user without the required role tries to access the endpoint.
    """
    response = client.get(
        "/student/notifications/mark_all_as_read",
        headers={"Authentication-Token": ta_token},
    )

    assert response.status_code == 403


@patch("apis.student.notifications.UserNotifications.query")
def test_mark_all_notifications_as_read_internal_server_error(
    mock_query, client, student_token
):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_query.filter_by.return_value.all.side_effect = Exception("Unexpected error")

    response = client.get(
        "/student/notifications/mark_all_as_read",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert (
        "An unexpected error occurred. Try again later."
        in data["response"]["errors"][0]
    )
