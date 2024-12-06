from unittest.mock import patch


@patch("apis.student.notifications.UserNotifications.query")
def test_get_notifications_success(mock_query, client, student_token):
    """
    Test successful retrieval of notifications for the current student.
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
        "/student/notifications",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "notifications" in data
    assert len(data["notifications"]) == 2

    first_notification = data["notifications"][0]
    assert first_notification["id"] == 1
    assert first_notification["title"] == "Assignment Due"
    assert first_notification["type"] == "DEADLINE"
    assert first_notification["created_at"] == "2024-11-20T10:00:00Z"
    assert first_notification["read_at"] is None


@patch("apis.student.notifications.UserNotifications.query")
def test_get_notifications_no_notifications(mock_query, client, student_token):
    """
    Test successful response when the user has no notifications.
    """
    mock_query.filter_by.return_value.all.return_value = []

    response = client.get(
        "/student/notifications",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "notifications" in data
    assert len(data["notifications"]) == 0


@patch("apis.student.notifications.UserNotifications.query")
def test_get_notifications_internal_server_error(mock_query, client, student_token):
    """
    Test 500 response when an internal server error occurs.
    """
    mock_query.filter_by.return_value.all.side_effect = Exception("Unexpected error")

    response = client.get(
        "/student/notifications",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "errors" in data["response"]
    assert (
        "An unexpected error occurred. Try again later."
        in data["response"]["errors"][0]
    )


def test_get_notifications_invalid_role(client, ta_token):
    """
    Test 403 response when a user without the Student role tries to access notifications.
    """
    response = client.get(
        "/student/notifications",
        headers={"Authentication-Token": ta_token},
    )

    assert response.status_code == 403
