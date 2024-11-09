from application.setup import app
from flask_security import current_user, roles_accepted
from application.models import (
    Tasks,
    Users,
    db,
    Submissions,
    Milestones,
    Teams,
)
from flask import abort, request, send_file, jsonify
from datetime import datetime, timezone
import os


@app.route("/teacher/milestone_management/numbers", methods=["GET"])
@roles_accepted("Instructor", "TA")
def get_team_student_no():

    teams = Teams.query.all()
    students = 0
    for user in Users.query.all():
        for role in user.roles:
            if role.name == "Student":
                students += 1

    return {"no_of_teams": len(teams), "no_of_students": students}


@app.route("/teacher/team_management/overall", methods=["GET"])
@roles_accepted("Instructor", "TA")
def get_overall_teams_progress():

    response_data = []
    milestones = db.session.query(Milestones).all()
    milestone_count = len(milestones)

    for team in db.session.query(Teams):
        completion_rate = 0

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
                .filter(Submissions.team_id == team.id)
                .filter(Tasks.milestone_id == milestone.id)
                .scalar()
            )

            completion_rate += (
                (submission_count / (task_count * milestone_count))
                if task_count != 0
                else 0
            )

        # Prepare the response data
        response_data.append(
            {
                "name": team.name,
                "progress": round(completion_rate * 100),
            }
        )

    return response_data, 200


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


@app.route("/teacher/team_management/individual/detail/<int:team_id>", methods=["GET"])
@roles_accepted("Instructor", "TA")
def get_team_details(team_id):

    team = Teams.query.get(team_id)
    if not team:
        abort(404, "Team not found")
    team = {
        "id": team.id,
        "name": team.name,
        "members": [
            {
                "id": member.id,
                "username": member.username,
                "email": member.email,
            }
            for member in team.members
        ],
        "github_repo_url": team.github_repo_url,
        "instructor": {"id": team.instructor.id, "username": team.instructor.username},
        "ta": {"id": team.ta.id, "username": team.ta.username},
    }
    return {"team": team}, 200


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


team_data = {
    "1": {
        "totalCommits": 120,
        "linesOfCodeAdded": 5000,
        "linesOfCodeDeleted": 300,
        "milestones": [
            {"name": "Milestone 1", "commits": 30, "linesOfCodeAdded": 1200, "linesOfCodeDeleted": 100},
            {"name": "Milestone 2", "commits": 25, "linesOfCodeAdded": 1300, "linesOfCodeDeleted": 50},
            {"name": "Milestone 3", "commits": 40, "linesOfCodeAdded": 1600, "linesOfCodeDeleted": 100},
            {"name": "Milestone 4", "commits": 25, "linesOfCodeAdded": 900, "linesOfCodeDeleted": 50}
        ]
    },
    "2": {
        "totalCommits": 85,
        "linesOfCodeAdded": 4200,
        "linesOfCodeDeleted": 250,
        "milestones": [
            {"name": "Milestone 1", "commits": 20, "linesOfCodeAdded": 1000, "linesOfCodeDeleted": 80},
            {"name": "Milestone 2", "commits": 15, "linesOfCodeAdded": 1200, "linesOfCodeDeleted": 60},
            {"name": "Milestone 3", "commits": 30, "linesOfCodeAdded": 1500, "linesOfCodeDeleted": 70},
            {"name": "Milestone 4", "commits": 20, "linesOfCodeAdded": 500, "linesOfCodeDeleted": 40}
        ]
    },
        "3": {
        "totalCommits": 85,
        "linesOfCodeAdded": 4200,
        "linesOfCodeDeleted": 250,
        "milestones": [
            {"name": "Milestone 1", "commits": 20, "linesOfCodeAdded": 1000, "linesOfCodeDeleted": 80},
            {"name": "Milestone 2", "commits": 15, "linesOfCodeAdded": 1200, "linesOfCodeDeleted": 60},
            {"name": "Milestone 3", "commits": 30, "linesOfCodeAdded": 1500, "linesOfCodeDeleted": 70},
            {"name": "Milestone 4", "commits": 20, "linesOfCodeAdded": 500, "linesOfCodeDeleted": 40}
        ]
    },
       "4": {
        "totalCommits": 85,
        "linesOfCodeAdded": 4200,
        "linesOfCodeDeleted": 250,
        "milestones": [
            {"name": "Milestone 1", "commits": 20, "linesOfCodeAdded": 1000, "linesOfCodeDeleted": 80},
            {"name": "Milestone 2", "commits": 15, "linesOfCodeAdded": 1200, "linesOfCodeDeleted": 60},
            {"name": "Milestone 3", "commits": 30, "linesOfCodeAdded": 1500, "linesOfCodeDeleted": 70},
            {"name": "Milestone 4", "commits": 20, "linesOfCodeAdded": 500, "linesOfCodeDeleted": 40}
        ]
    },
}

@app.route('/teacher/team_management/individual/github/<team_id>', methods=['GET'])
def get_github_details(team_id):
    team_details = team_data.get(team_id)
    if team_details:
        return jsonify({
            "teamId": team_id,
            "totalCommits": team_details["totalCommits"],
            "linesOfCodeAdded": team_details["linesOfCodeAdded"],
            "linesOfCodeDeleted": team_details["linesOfCodeDeleted"],
            "milestones": team_details["milestones"]
        })
    else:
        return jsonify({"error": "Team not found"}), 404