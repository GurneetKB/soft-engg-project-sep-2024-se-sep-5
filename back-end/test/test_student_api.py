import pytest
import os
from io import BytesIO
from datetime import datetime, timezone
from application.setup import create_app
from application.models import *


@pytest.fixture
def valid_file():
    # Create a valid PDF file in memory
    return BytesIO(b"PDF content goes here.")


@pytest.fixture
def client(scope="session"):

    app = create_app("sqlite:///testing.sqlite3", testing=True)
    with app.test_client() as client:
        yield client


@pytest.fixture
def student_token(client):
    # Login as a student and get a token
    response = client.post(
        "/login?include_auth_token",
        json={"username": "student1", "password": "password123"},
    )
    return response.json["response"]["user"]["authentication_token"]


@pytest.fixture
def user_notification(client, student_token):
    # Fetch or create a notification for the student
    student = Users.query.filter_by(username="student1").first()
    notification = Notifications(
        title="Test Notification",
        message="This is a test message",
        type="DEADLINE",
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(notification)
    db.session.commit()

    # Create a UserNotification for the student
    user_notification = UserNotifications(
        notification_id=notification.id,
        user_id=student.id,
        read_at=None,  # Initially, the notification is unread
    )
    db.session.add(user_notification)
    db.session.commit()
    return user_notification


def test_get_notifications(client, student_token):
    response = client.get(
        "/student/notifications", headers={"Authentication-Token": student_token}
    )
    assert response.status_code == 200, "Failed to fetch notifications"
    assert isinstance(
        response.json["notifications"], list
    ), "Notifications should be a list"


def test_get_notification_detail(client, student_token, user_notification):
    # Fetch the notification details using the notification_id
    notification_id = user_notification.notification_id

    response = client.get(
        f"/student/notifications/{notification_id}",
        headers={"Authentication-Token": student_token},
    )

    # Assert the response is correct
    assert response.status_code == 200, "Failed to fetch notification detail"

    notification_data = response.json
    assert notification_data["id"] == user_notification.notifications.id
    assert notification_data["title"] == user_notification.notifications.title
    assert notification_data["message"] == user_notification.notifications.message
    assert notification_data["type"] == user_notification.notifications.type.value

    # Re-fetch the user_notification from the database to make sure it is persistent within the session
    user_notification = UserNotifications.query.get(user_notification.id)

    # Check if the notification is marked as read
    assert (
        user_notification.read_at is not None
    ), "Notification should be marked as read"


def test_mark_all_notifications_as_read(client, student_token, user_notification):
    # First, create multiple unread notifications for the student
    student = Users.query.filter_by(username="student1").first()

    # Create additional notifications
    additional_notification1 = Notifications(
        title="Test Notification 1",
        message="This is another test message 1",
        type="FEEDBACK",
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(additional_notification1)

    additional_notification2 = Notifications(
        title="Test Notification 2",
        message="This is another test message 2",
        type="DEADLINE",
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(additional_notification2)

    db.session.commit()  # Commit the notifications to the database

    # Re-fetch the student instance to avoid DetachedInstanceError
    student = Users.query.filter_by(username="student1").first()

    # Create UserNotification entries for the new notifications
    user_notification1 = UserNotifications(
        notification_id=additional_notification1.id, user_id=student.id, read_at=None
    )
    user_notification2 = UserNotifications(
        notification_id=additional_notification2.id, user_id=student.id, read_at=None
    )
    db.session.add(user_notification1)
    db.session.add(user_notification2)
    db.session.commit()

    # Re-fetch the student instance again before performing any further queries
    student = Users.query.filter_by(username="student1").first()

    # Send request to mark all notifications as read
    response = client.get(
        "/student/notifications/mark_all_as_read",
        headers={"Authentication-Token": student_token},
    )

    # Assert the response is correct
    assert response.status_code == 200, "Failed to mark all notifications as read"
    assert response.json["message"] == "All notifications marked as read."

    # Re-fetch the unread notifications to verify they are marked as read
    unread_notifications = UserNotifications.query.filter_by(
        user_id=student.id, read_at=None
    ).all()
    assert len(unread_notifications) == 0, "Some notifications were not marked as read"


def test_get_notification_preferences(client, student_token):
    # Fetch or create the notification preferences for the student
    student = Users.query.filter_by(username="student1").first()

    preferences = NotificationPreferences.query.filter_by(user_id=student.id).first()
    if not preferences:
        preferences = NotificationPreferences(
            user_id=student.id,
            email_deadline_notifications=True,
            in_app_deadline_notifications=True,
            email_feedback_notifications=True,
            in_app_feedback_notifications=False,
        )
        db.session.add(preferences)
        db.session.commit()

    db.session.refresh(preferences)

    # Convert preferences to a dict for comparison
    expected_preferences = {
        "email_deadline_notifications": preferences.email_deadline_notifications,
        "in_app_deadline_notifications": preferences.in_app_deadline_notifications,
        "email_feedback_notifications": preferences.email_feedback_notifications,
        "in_app_feedback_notifications": preferences.in_app_feedback_notifications,
    }

    # Send request to get notification preferences
    response = client.get(
        "/student/notifications/preferences",
        headers={"Authentication-Token": student_token},
    )

    # Assert the response is correct
    assert response.status_code == 200, "Failed to fetch notification preferences"

    # Compare response JSON with expected preferences
    response_json = response.json
    for key, value in expected_preferences.items():
        assert response_json.get(key) == value, f"Mismatch in {key}"


def test_get_notification_preferences_not_found(client, student_token):
    # Ensure the student does not have any notification preferences
    student = Users.query.filter_by(username="student1").first()

    # Delete the existing preferences if any
    preferences = NotificationPreferences.query.filter_by(user_id=student.id).first()
    if preferences:
        db.session.delete(preferences)
        db.session.commit()

    # Send request to get notification preferences
    response = client.get(
        "/student/notifications/preferences",
        headers={"Authentication-Token": student_token},
    )

    # Check if the response contains JSON
    assert (
        response.content_type == "application/json"
    ), "Expected response to be in JSON format"

    # If response is JSON, try parsing it
    try:
        response_json = response.json
    except Exception as e:
        pytest.fail(f"Failed to parse JSON from response: {e}")

    # Assert the response is correct
    assert response.status_code == 404, "Notification preferences should not be found"
    assert (
        response_json.get("response")["errors"][0]
        == "Notification preferences not found."
    ), f"Unexpected message: {response_json.get('message')}"


# Returning a JSON Response for Not Found: When no preferences are found, jsonify is used to explicitly return a JSON response with the message key.


def test_mark_all_notifications_as_read_no_unread(client, student_token):
    # Send request to mark all notifications as read
    response = client.get(
        "/student/notifications/mark_all_as_read",
        headers={"Authentication-Token": student_token},
    )

    # Assert the response is correct
    assert response.status_code == 200, "Failed to mark all notifications as read"
    assert response.json["message"] == "All notifications marked as read."

    # Ensure the session is fresh to avoid DetachedInstanceError
    student = Users.query.filter_by(username="student1").first()
    db.session.refresh(student)

    unread_notifications = UserNotifications.query.filter_by(
        user_id=student.id, read_at=None
    ).all()
    assert len(unread_notifications) == 0, "There should be no unread notifications"


@pytest.fixture
def milestone(client):
    milestone = Milestones(
        title="Test Milestone",
        description="This is a test milestone",
        deadline=datetime(2024, 12, 15, tzinfo=timezone.utc),
        created_at=datetime.now(tz=timezone.utc),
    )
    db.session.add(milestone)
    db.session.commit()
    return milestone


def test_get_milestones(client, student_token):
    # Get all milestones for the student
    response = client.get(
        "/student/milestone_management/individual",
        headers={"Authentication-Token": student_token},
    )

    # Assert the response is correct
    assert response.status_code == 200, "Failed to get milestones"

    # Check the structure of the response
    assert "milestones" in response.json, "Milestones key not found"
    assert isinstance(response.json["milestones"], list), "Milestones should be a list"

    # Check if the milestones have the correct attributes
    for milestone in response.json["milestones"]:
        assert "id" in milestone, "Milestone id not found"
        assert "title" in milestone, "Milestone title not found"


@pytest.fixture
def milestone_id(milestone):
    return milestone.id


def test_get_milestone_details(client, student_token, milestone_id):
    response = client.get(
        f"/student/milestone_management/individual/{milestone_id}",
        headers={"Authentication-Token": student_token},
    )

    assert response.status_code == 200, "Failed to get milestone details"
    assert "title" in response.json, "Milestone title not found"
    assert "description" in response.json, "Milestone description not found"
    assert "tasks" in response.json, "Milestone tasks not found"

    # Optionally, check the values of the milestone details
    assert response.json["title"] == "Test Milestone", "Unexpected milestone title"
    assert (
        response.json["description"] == "This is a test milestone"
    ), "Unexpected milestone description"


@pytest.fixture
def team(client):
    # Create a team for the student
    team = Teams(name="Test Team")
    db.session.add(team)
    db.session.commit()
    return team


@pytest.fixture
def submission(client, student_token, milestone, team):
    # Create a submission for a task under the milestone
    task_id = 1  # Example task ID
    file_dir = os.path.join(
        app.config["UPLOAD_FOLDER"],
        f"team_{team.id}",
        f"milestone_{milestone.id}",
    )
    os.makedirs(file_dir, exist_ok=True)
    file_path = os.path.join(
        file_dir, f"Milestone{milestone.id}_Task{task_id}_Team{team.name}.pdf"
    )
    with open(file_path, "wb") as f:
        f.write(b"PDF content")

    submission = Submissions(
        task_id=task_id,
        team_id=team.id,
        submission_time=datetime.now(timezone.utc),
    )
    db.session.add(submission)
    db.session.commit()

    document = Documents(
        title=f"Milestone{milestone.id}_Task{task_id}_Team{team.name}",
        file_url=file_path,
        submission=submission,
    )
    db.session.add(document)
    db.session.commit()

    return submission, file_path
