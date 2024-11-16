from apis.student.setup import student
from flask_security import current_user, roles_required
from application.models import (
    NotificationPreferences,
    UserNotifications,
    db,
)
from flask import abort, request
from datetime import datetime, timezone


@student.route("/notifications", methods=["GET"])
@roles_required("Student")
def get_notifications():

    # Query the UserNotifications for the current user's notifications
    notifications = UserNotifications.query.filter_by(user_id=current_user.id).all()

    notification_list = [
        {
            "id": notification.notifications.id,
            "title": notification.notifications.title,
            "type": notification.notifications.type.value,
            "created_at": notification.notifications.created_at,
            "read_at": notification.read_at,
        }
        for notification in notifications
    ]

    return {"notifications": notification_list}, 200


@student.route("/notifications/<int:notification_id>", methods=["GET"])
@roles_required("Student")
def get_notification_detail(notification_id):

    # Fetch the UserNotification by ID and ensure it belongs to the current user
    user_notification = UserNotifications.query.filter_by(
        notification_id=notification_id, user_id=current_user.id
    ).first()

    # Check if the notification exists and is accessible by the current user
    if not user_notification:
        return abort(404, "Notification not found or access denied.")

    data = {
        "id": user_notification.notifications.id,
        "title": user_notification.notifications.title,
        "message": user_notification.notifications.message,
        "type": user_notification.notifications.type.value,
        "created_at": user_notification.notifications.created_at,
        "read_at": user_notification.read_at,
    }

    # Mark notification as read
    user_notification.read_at = datetime.now(timezone.utc)
    db.session.commit()

    return data, 200


@student.route("/notifications/mark_all_as_read", methods=["GET"])
@roles_required("Student")
def mark_all_notifications_as_read():

    # Query all unread notifications for the current user
    unread_notifications = UserNotifications.query.filter_by(
        user_id=current_user.id, read_at=None
    ).all()

    # Mark each notification as read
    for notification in unread_notifications:
        notification.read_at = datetime.now(timezone.utc)

    db.session.commit()

    return {"message": "All notifications marked as read."}, 200


@student.route("/notifications/preferences", methods=["GET"])
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


@student.route("/notifications/preferences", methods=["PUT"])
@roles_required("Student")
def set_notification_preferences():
    data = request.get_json()
    email_deadline_pref = data.get("email_deadline_notifications")
    in_app_deadline_pref = data.get("in_app_deadline_notifications")
    email_feedback_pref = data.get("email_feedback_notifications")
    in_app_feedback_pref = data.get("in_app_feedback_notifications")

    # Validate input for each preference
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

    db.session.commit()

    return {"message": "Notification preferences updated successfully."}, 201
