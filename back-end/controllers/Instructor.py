from application.setup import app
from flask_security import current_user, roles_accepted
from application.models import (
    Notifications,
    NotificationPreferences,
    db,
    Submissions,
    Milestones,
    Teams,
)
from flask import abort, request, send_file
from datetime import datetime, timezone
import os


@app.route("/teacher/team_management/individual", methods=["GET"])
@roles_accepted("Instructor", "TA")
def get_teams():

    teams = Teams.query.all()
    team_list = [
        {
            "id": team.id,
            "name": team.name,
        }
        for team in teams
    ]
    return {"teams": team_list}, 200


@app.route(
    "/teacher/team_management/individual/progress/<int:team_id>", methods=["GET"]
)
@roles_accepted("Instructor", "TA")
def get_team_progress(team_id):

    milestones = Milestones.query.all()
    team_submissions = db.session.query(Submissions).filter(
        Submissions.team_id == team_id
    )
    if team_id:
        milestones_data = []
        for milestone in milestones:
            individual_milestone = {
                "id": milestone.id,
                "title": milestone.title,
                "description": milestone.description,
                "deadline": milestone.deadline.strftime("%Y-%m-%d %H:%M:%S"),
                "created_at": milestone.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "tasks": [],
            }
            for task in milestone.task_milestones:
                task_submission = team_submissions.filter(
                    Submissions.task_id == task.id
                ).first()
                individual_milestone["tasks"].append(
                    {
                        "task_id": task.id,
                        "description": task.description,
                        "is_completed": True if task_submission else False,
                        "feedback": (
                            task_submission.feedback if task_submission else None
                        ),
                        "feedback_time": (
                            task_submission.feedback_time if task_submission else None
                        ),
                    }
                )

            milestones_data.append(individual_milestone)

        return milestones_data, 200
    else:
        return abort(404, "Team not found.")


@app.route(
    "/teacher/team_management/individual/submission/<int:team_id>/<int:task_id>",
    methods=["GET"],
)
@roles_accepted("Instructor", "TA")
def view_submission(team_id, task_id):
    submission = Submissions.query.filter(
        Submissions.task_id == task_id, Submissions.team_id == team_id
    ).first()

    if not submission or not submission.documents:
        return abort(404, "Submission or document not found")

    document = submission.documents

    # Check file existence
    if not os.path.exists(document.file_url):
        return abort(404, "File not found")

    return send_file(document.file_url)


@app.route(
    "/teacher/team_management/individual/feedback/<int:team_id>/<int:task_id>",
    methods=["POST"],
)
@roles_accepted("Instructor", "TA")
def provide_feedback(team_id, task_id):
    data = request.get_json()
    if not data or "feedback" not in data:
        return abort(400, "Feedback data is required")

    feedback_content = data.get("feedback")
    if not isinstance(feedback_content, str) or not feedback_content.strip():
        return abort(400, "Feedback must be a non-empty string")

    # Find the relevant submission
    submission = Submissions.query.filter(
        Submissions.task_id == task_id, Submissions.team_id == team_id
    ).first()
    if not submission:
        return abort(404, "Submission not found")

    # Update feedback-related fields
    submission.feedback_by = current_user.id
    submission.feedback = feedback_content.strip()  # sanitize whitespace
    submission.feedback_time = datetime.now(timezone.utc)
    db.session.commit()
    return {"message": "The feedback is successfully provided."}, 201
