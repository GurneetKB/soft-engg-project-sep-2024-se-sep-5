from application.setup import app
from flask_security import current_user, roles_required
from application.models import (
    Milestones,
    Submissions,
    Tasks,
    Teams,
    NotificationPreferences,
    UserNotifications,
    team_students,
    db,
)
from flask import abort, request
from datetime import datetime, timezone


def get_team_id(user):
    return (
        db.session.query(team_students.c.team_id)
        .filter(team_students.c.student_id == user.id)
        .scalar()
    )


@app.route("/student/notifications", methods=["GET"])
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


@app.route("/student/notifications/<int:notification_id>", methods=["GET"])
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


@app.route("/student/notifications/mark_all_as_read")
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

    return {"message": "Notification preferences updated successfully."}, 200


@app.route("/student/milestone_management/overall", methods=["GET"])
@roles_required("Student")
def get_team_milestones():
    # Get the team ID associated with the current student
    team_id = get_team_id(current_user)

    if not team_id:
        abort(400, "No team is assigned to you yet.")

    # Retrieve the team along with its milestones, tasks, and submissions
    team = db.session.query(Teams).filter(Teams.id == team_id).first()

    # Prepare milestone data
    team_milestone_for_user = []

    milestones = db.session.query(Milestones).all()

    for milestone in milestones:
        # Get the number of tasks in the milestone
        task_count = (
            db.session.query(db.func.count(Tasks.id))
            .filter(Tasks.milestone_id == milestone.id)
            .scalar()
        )

        # Get the number of submissions associated with the milestone tasks
        submission_count = (
            db.session.query(db.func.count(Submissions.id))
            .join(Tasks, Submissions.task_id == Tasks.id)
            .filter(Submissions.team_id == team_id)
            .filter(Tasks.milestone_id == milestone.id)
            .scalar()
        )

        team_milestone_for_user.append(
            {
                "milestone_id": milestone.id,
                "title": milestone.title,
                "completion_percentage": (
                    (submission_count / task_count) * 100 if task_count != 0 else 0
                ),
            }
        )

    # Prepare the response data
    response_data = {
        "team_name": team.name,
        "milestones": team_milestone_for_user,
    }

    return response_data, 200


# Define the endpoint to get details of a specific milestone
@app.route("/student/milestone_management/individual", methods=["GET"])
@roles_required("Student")
def get_milestones():
    # Fetch all milestones for the student
    milestones = Milestones.query.all()
    milestone_list = [
        {
            "id": milestone.id,
            "title": milestone.title,
        }
        for milestone in milestones
    ]
    return {"milestones": milestone_list}, 200


@app.route(
    "/student/milestone_management/individual/<int:milestone_id>", methods=["GET"]
)
@roles_required("Student")
def get_milestone_details(milestone_id):
    team_id = get_team_id(current_user)
    milestone = Milestones.query.get(milestone_id)
    team_submissions = db.session.query(Submissions.id).filter(
        Submissions.team_id == team_id
    )
    if milestone:
        # Prepare a dictionary with the milestone details
        milestone_data = {
            "id": milestone.id,
            "title": milestone.title,
            "description": milestone.description,
            "deadline": milestone.deadline.strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": milestone.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "tasks": [
                {
                    "task_id": task.id,
                    "description": task.description,
                    "is_completed": team_submissions.filter(
                        Submissions.task_id == task.id
                    ).scalar(),
                }
                for task in milestone.task_milestones
            ],
        }
        return milestone_data, 200
    else:
        return abort(404, "Milestone not found")
