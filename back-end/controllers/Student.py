from application.setup import app
from flask_security import current_user, roles_required
from application.models import Notifications, NotificationPreferences, TeamMilestones, Teams, team_students, db
from flask import abort, request
from datetime import datetime, timezone


@app.route("/student/notifications", methods=["GET"])
@roles_required("Student")
def get_notifications():

    notifications = Notifications.query.filter_by(user_id=current_user.id).all()

    notification_list = [
        {
            "id": notification.id,
            "title": notification.title,
            "type": notification.type,
            "created_at": notification.created_at,
            "read_at": notification.read_at,
        }
        for notification in notifications
    ]

    return notification_list, 200


@app.route("/student/notifications/<int:notification_id>", methods=["GET"])
@roles_required("Student")
def get_notification_detail(notification_id):

    # Fetch the notification by ID and ensure it belongs to the current user
    notification = Notifications.query.filter_by(
        id=notification_id, user_id=current_user.id
    ).first()

    # Check if the notification exists and is accessible by the current user
    if not notification:
        return abort(404, "Notification not found or access denied.")

    data = {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type,
        "created_at": notification.created_at,
        "read_at": notification.read_at,
    }

    notification.read_at = datetime.now(timezone.utc)
    db.session.commit()

    return data, 200


@app.route("/student/notifications/mark_all_as_read")
@roles_required("Student")
def mark_all_notifications_as_read():

    # Query all unread notifications for the current user
    unread_notifications = Notifications.query.filter_by(
        user_id=current_user.id, read_at=None
    ).all()

    # Mark each notification as read by setting the read_at timestamp
    for notification in unread_notifications:
        notification.read_at = datetime.now(timezone.utc)

    db.session.commit()

    return {"message": "All notifications marked as read."}, 200


@app.route("/student/notifications/preferences", methods=["GET"])
@roles_required("Student")
def get_notification_preferences():

    # Get the current user's notification preferences
    preferences = NotificationPreferences.query.filter_by(
        user_id=current_user.id
    ).first()

    if not preferences:
        return abort(404, "Notification preferences not found.")

    return {
        "email_deadline_notifications": preferences.email_deadline_notifications,
        "in_app_deadline_notifications": preferences.in_app_deadline_notifications,
        "email_feedback_notifications": preferences.email_feedback_notifications,
        "in_app_feedback_notifications": preferences.in_app_feedback_notifications,
    }, 200


@app.route("/student/notifications/preferences", methods=["PUT"])
@roles_required("Student")
def set_notification_preferences():
    # Parse the request JSON for preference settings
    data = request.get_json()
    email_deadline_pref = data.get("email_deadline_notifications")
    in_app_deadline_pref = data.get("in_app_deadline_notifications")
    email_feedback_pref = data.get("email_feedback_notifications")
    in_app_feedback_pref = data.get("in_app_feedback_notifications")

    # Validate each preference input
    for pref, value in {
        "email_deadline_notifications": email_deadline_pref,
        "in_app_deadline_notifications": in_app_deadline_pref,
        "email_feedback_notifications": email_feedback_pref,
        "in_app_feedback_notifications": in_app_feedback_pref,
    }.items():
        if value is not None and not isinstance(value, bool):
            return abort(400, f"{pref} must be a boolean value.")

    # Get the current user's notification preferences
    preferences = NotificationPreferences.query.filter_by(
        user_id=current_user.id
    ).first()

    if not preferences:
        return abort(404, "Notification preferences not found.")

    # Update preferences based on the provided data
    if email_deadline_pref is not None:
        preferences.email_deadline_notifications = email_deadline_pref
    if in_app_deadline_pref is not None:
        preferences.in_app_deadline_notifications = in_app_deadline_pref
    if email_feedback_pref is not None:
        preferences.email_feedback_notifications = email_feedback_pref
    if in_app_feedback_pref is not None:
        preferences.in_app_feedback_notifications = in_app_feedback_pref

    # Commit the changes to the database
    db.session.commit()

    return {"message": "Notification preferences updated successfully."}, 200


@app.route("/student/milestone_mnagement/overall", methods=["GET"])
@roles_required("Student")

def get_team_milestones():

    team_milestones_for_user = (
    db.session.query(TeamMilestones)
    .join(Teams)
    .join(team_students)
    .filter(team_students.c.student_id == current_user.id)
    .all()
    )

    teammilestone_for_user = [
        {
            "id": team_milestone.id,
            "title": team_milestone.milestone.title,
            "completion_percentage": team_milestone.completion_percentage,
        }
        for team_milestone in team_milestones_for_user
    ]

    return {"milestones": teammilestone_for_user,
            "team_name" : teammilestone_for_user[0]["name"]}, 200



