from apis.student.setup import student, get_team_id
from flask_security import current_user, roles_required
from application.models import (
    Documents,
    Milestones,
    Submissions,
    Tasks,
    Teams,
    db,
)
from flask import abort, make_response, request, send_file, current_app
from datetime import datetime, timezone
import os


@student.route("/milestone_management/overall", methods=["GET"])
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


@student.route("/milestone_management/individual", methods=["GET"])
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


@student.route("/milestone_management/individual/<int:milestone_id>", methods=["GET"])
@roles_required("Student")
def get_milestone_details(milestone_id):
    team_id = get_team_id(current_user)
    milestone = Milestones.query.get(milestone_id)
    team_submissions = db.session.query(Submissions).filter(
        Submissions.team_id == team_id
    )
    if milestone and team_id:
        # Prepare a dictionary with the milestone details
        milestone_data = {
            "id": milestone.id,
            "title": milestone.title,
            "description": milestone.description,
            "deadline": milestone.deadline,
            "created_at": milestone.created_at,
            "tasks": [],
        }
        for task in milestone.task_milestones:
            task_submission = team_submissions.filter(
                Submissions.task_id == task.id
            ).first()
            milestone_data["tasks"].append(
                {
                    "task_id": task.id,
                    "description": task.description,
                    "is_completed": True if task_submission else False,
                    "feedback": task_submission.feedback if task_submission else None,
                    "feedback_time": (
                        task_submission.feedback_time if task_submission else None
                    ),
                }
            )
        return milestone_data, 200
    else:
        return abort(404, "Milestone or team not found.")


@student.route("/milestone_management/individual/<int:milestone_id>", methods=["POST"])
@roles_required("Student")
def submit_milestone(milestone_id):
    team_id = get_team_id(current_user)
    saved_files = []
    tasks = []
    # Fetch the milestone and team details
    milestone = Milestones.query.get(milestone_id)
    team = Teams.query.get(team_id)

    # Check if milestone and team exist
    if not milestone or not team:
        return abort(404, "Milestone or team not found")

    # Check if the milestone deadline has passed
    if milestone.deadline.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return abort(400, "Cannot submit after the milestone deadline")

    # Verify tasks under the milestone
    milestone_tasks = {str(task.id): task for task in milestone.task_milestones}

    # Prepare the directory for storing uploaded files
    file_dir = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        f"team_{team_id}",
        f"milestone_{milestone_id}",
    )
    os.makedirs(file_dir, exist_ok=True)

    # Check and process each file in the form data
    for key in request.files:
        task_id = key
        file = request.files.get(key)
        # Ensure task exists under the current milestone and the file is a PDF
        if task_id in milestone_tasks and file.filename.lower().endswith(".pdf"):

            # Generate document title and save file
            document_title = f"Milestone{milestone_id}_Task{task_id}_Team{team.name}"
            file_url = os.path.join(file_dir, document_title + ".pdf")
            file.save(file_url)
            saved_files.append(file_url)

            # Check if a previous submission exists for this team and task and delete it
            existing_submission = Submissions.query.filter_by(
                team_id=team_id, task_id=task_id
            ).first()
            if existing_submission:
                db.session.delete(existing_submission)

            # Create a new submission
            new_submission = Submissions(
                task_id=task_id,
                team_id=team_id,
                submission_time=datetime.now(timezone.utc),
            )
            db.session.add(new_submission)

            # Associate document with specific task
            document = Documents(
                title=document_title,
                file_url=file_url,
                submission=new_submission,
            )
            db.session.add(document)
            tasks.append(task_id)

        else:
            # remove the files that were saved till now
            for saved_file in saved_files:
                os.remove(saved_file)
            abort(
                400,
                f"Task {task_id} is not valid for this milestone or the file is not a PDF",
            )

    db.session.commit()

    return {"message": "Milestone documents submitted successfully"}, 201


@student.route("/download_submission/<int:task_id>", methods=["GET"])
@roles_required("Student")
def download_submission(task_id):
    team_id = get_team_id(current_user)
    submission = Submissions.query.filter(
        Submissions.task_id == task_id, Submissions.team_id == team_id
    ).first()

    if not submission or not submission.documents:
        return abort(404, "Submission or document not found")

    document = submission.documents

    # Check file existence
    if not os.path.exists(document.file_url):
        return abort(404, "File not found")

    file_response = make_response(send_file(document.file_url))
    file_response.headers["Content-Disposition"] = (
        f'attachment; filename="{document.title}.pdf"'
    )
    return file_response, 200
