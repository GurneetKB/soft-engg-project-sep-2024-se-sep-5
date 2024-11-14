from application.setup import app, github_client
from flask_security import current_user, roles_accepted, roles_required
from application.models import (
    Tasks,
    db,
    Submissions,
    Milestones,
    Teams,
)
from flask import abort, request, send_file
from datetime import datetime, timezone
import os
from datetime import datetime
import os


def get_teams_under_user(user):
    if current_user.has_role("Instructor"):
        teams = Teams.query.filter(Teams.instructor_id == user.id).all()
    else:
        teams = Teams.query.filter(Teams.ta_id == user.id).all()
    return teams


def get_single_team_under_user(user, team_id):
    if current_user.has_role("Instructor"):
        team = Teams.query.filter(
            Teams.instructor_id == user.id, Teams.id == team_id
        ).first()
    else:
        team = Teams.query.filter(Teams.ta_id == user.id, Teams.id == team_id).first()
    return team


@app.route("/teacher/milestone_management", methods=["GET"])
@roles_accepted("Instructor", "TA")
def get_all_milestones():

    milestone_objects = Milestones.query.all()

    teams = get_teams_under_user(current_user)

    no_of_students = 0
    for team in teams:
        no_of_students += len(team.members)

    total_teams = len(teams)

    response_data = {
        "no_of_teams": total_teams,
        "no_of_students": no_of_students,
        "milestones": [],
    }

    for milestone in milestone_objects:
        tasks = milestone.task_milestones
        if not tasks:
            milestone.completion_rate = 0.0
            continue

        completed_teams = (
            db.session.query(Submissions.team_id)
            .join(Tasks, Tasks.id == Submissions.task_id)
            .filter(
                Tasks.milestone_id == milestone.id,
                Submissions.team_id.in_([team.id for team in teams]),
            )
            .group_by(Submissions.team_id)
            .having(db.func.count(db.distinct(Submissions.task_id)) == len(tasks))
            .count()
            or 0
        )

        response_data["milestones"].append(
            {
                "id": milestone.id,
                "title": milestone.title,
                "description": milestone.description,
                "deadline": milestone.deadline,
                "completion_rate": (
                    (completed_teams / total_teams) * 100 if total_teams != 0 else 0
                ),
            }
        )

    return response_data


@app.route("/teacher/milestone_management", methods=["POST"])
@roles_required("Instructor")
def create_milestone():
    data = request.get_json()

    # Extract fields
    title = data.get("title")
    description = data.get("description")
    deadline = data.get("deadline")
    tasks = data.get("tasks", [])

    # Basic validation checks
    errors = []
    if not title or not isinstance(title, str):
        errors.append("Title is required and must be a string.")
    if not description or not isinstance(description, str):
        errors.append("Description is required and must be a string.")
    if not deadline:
        errors.append("Deadline is required.")
    else:
        try:
            parsed_deadline = datetime.strptime(
                deadline, "%a, %d %b %Y %H:%M:%S %Z"
            ).replace(tzinfo=timezone.utc)
            if parsed_deadline <= datetime.now(timezone.utc):
                errors.append("Deadline must be set to a future date and time.")
        except ValueError:
            errors.append("Deadline must be a valid GMT format datetime.")

    # Validate tasks
    if not isinstance(tasks, list):
        errors.append("Tasks must be a list.")
    else:
        for i, task_data in enumerate(tasks, 1):
            if not isinstance(task_data, dict) or "description" not in task_data:
                errors.append(f"Task {i} must be an object with a 'description' field.")
            elif not isinstance(task_data["description"], str):
                errors.append(f"Description in Task {i} must be a string.")

    # If there are validation errors, return them
    if errors:
        return abort(400, errors)

    # Create milestone object
    milestone_object = Milestones(
        title=title,
        description=description,
        deadline=parsed_deadline,
        created_by=current_user.id,
        created_at=datetime.now(timezone.utc),
    )

    # Add milestone to session
    db.session.add(milestone_object)
    db.session.flush()  # Ensure milestone_object.id is available for tasks

    # Create tasks and associate with milestone
    for task_data in tasks:
        task_description = task_data["description"]
        task = Tasks(description=task_description, milestone_id=milestone_object.id)
        db.session.add(task)

    # Commit all changes
    db.session.commit()

    return {"message": "Milestone published successfully."}, 201


@app.route("/teacher/milestone_management/<int:milestone_id>", methods=["GET"])
@roles_required("Instructor")
def get_milestone(milestone_id):
    milestone_object = Milestones.query.filter_by(id=milestone_id).first()
    if not milestone_object:
        return abort(404, "Milestone not found.")

    milestone_data = {
        "title": milestone_object.title,
        "description": milestone_object.description,
        "deadline": milestone_object.deadline.strftime("%Y-%m-%dT%H:%M"),
        "tasks": [
            {"description": task.description}
            for task in milestone_object.task_milestones
        ],
    }

    return milestone_data


@app.route("/teacher/milestone_management/<int:milestone_id>", methods=["PUT"])
@roles_required("Instructor")
def update_milestone(milestone_id):
    # Fetch milestone
    milestone_object = Milestones.query.filter_by(id=milestone_id).first()
    if not milestone_object:
        return abort(404, "Milestone not found.")

    data = request.get_json()
    errors = []

    # Validate and update title
    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            errors.append("Title must be a non-empty string.")
        else:
            milestone_object.title = title

    # Validate and update description
    if "description" in data:
        description = data["description"]
        if not isinstance(description, str) or not description.strip():
            errors.append("Description must be a non-empty string.")
        else:
            milestone_object.description = description

    # Validate and update deadline
    if "deadline" in data:
        deadline = data["deadline"]
        try:
            # Parse the deadline and check if it is in the future
            parsed_deadline = datetime.strptime(
                deadline, "%a, %d %b %Y %H:%M:%S %Z"
            ).replace(tzinfo=timezone.utc)
            if parsed_deadline <= datetime.now(timezone.utc):
                errors.append("Deadline must be set to a future date and time.")
            else:
                milestone_object.deadline = parsed_deadline
        except ValueError:
            errors.append("Deadline must be a valid GMT format datetime.")

    # Validate tasks
    if "tasks" in data:
        tasks = data["tasks"]
        if not isinstance(tasks, list):
            errors.append("Tasks must be provided as a list.")
        else:
            # Remove existing tasks if tasks data is valid
            for task in milestone_object.task_milestones:
                db.session.delete(task)

            # Add new tasks with validation
            for i, task_data in enumerate(tasks, 1):
                task_description = task_data.get("description")
                if not isinstance(task_data, dict) or not task_description:
                    errors.append(
                        f"Task {i} must have a non-empty 'description' field."
                    )
                elif not isinstance(task_description, str):
                    errors.append(f"Description in Task {i} must be a string.")
                else:
                    new_task = Tasks(
                        description=task_description, milestone=milestone_object
                    )
                    db.session.add(new_task)

    # If validation errors exist, return them
    if errors:
        return abort(400, errors)

    # Commit changes
    db.session.commit()
    return {"message": "Milestone updated successfully."}, 201


@app.route("/teacher/milestone_management/<int:milestone_id>", methods=["DELETE"])
@roles_required("Instructor")
def delete_milestone(milestone_id):
    delete_object = Milestones.query.filter_by(id=milestone_id).first()
    if not delete_object:
        return abort(404, "Milestone not found.")

    db.session.delete(delete_object)
    db.session.commit()
    return {"message": "Milestone is deleted"}, 200


@app.route("/teacher/team_management/overall", methods=["GET"])
@roles_accepted("Instructor", "TA")
def get_overall_teams_progress():

    response_data = []
    milestones = db.session.query(Milestones).all()
    milestone_count = len(milestones)
    teams = get_teams_under_user(current_user)
    for team in teams:
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

    teams = get_teams_under_user(current_user)
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

    team = get_single_team_under_user(current_user, team_id)
    if not team:
        return abort(404, "Team not found")
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


@app.route("/teacher/team_management/individual/<int:team_id>/members", methods=["GET"])
@roles_accepted("Instructor", "TA")
def get_team_member_details(team_id):

    team = get_single_team_under_user(current_user, team_id)
    if not team:
        return abort(404, "Team not found")
    return {
        "members": [
            {
                "id": member.id,
                "name": member.username,
            }
            for member in team.members
        ]
    }, 200


@app.route(
    "/teacher/team_management/individual/progress/<int:team_id>", methods=["GET"]
)
@roles_accepted("Instructor", "TA")
def get_team_progress(team_id):

    team = get_single_team_under_user(current_user, team_id)
    if not team:
        return abort(404, "Team not found")

    milestones = Milestones.query.all()
    team_submissions = db.session.query(Submissions).filter(
        Submissions.team_id == team_id
    )
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
                    "feedback": (task_submission.feedback if task_submission else None),
                    "feedback_time": (
                        task_submission.feedback_time if task_submission else None
                    ),
                }
            )

        milestones_data.append(individual_milestone)

    return milestones_data, 200


@app.route(
    "/teacher/team_management/individual/submission/<int:team_id>/<int:task_id>",
    methods=["GET"],
)
@roles_accepted("Instructor", "TA")
def view_submission(team_id, task_id):

    team = get_single_team_under_user(current_user, team_id)
    if not team:
        return abort(404, "Team not found")

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

    team = get_single_team_under_user(current_user, team_id)
    if not team:
        return abort(404, "Team not found")

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


@app.route(
    "/teacher/team_management/individual/github/<int:team_id>",
    methods=["POST"],
)
def get_github_details(team_id):
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        github_username = None
        team = get_single_team_under_user(current_user, team_id)

        if not team:
            return abort(404, "Team not found")

        if user_id:
            for member in team.members:
                if member.id == user_id:
                    github_username = member.github_username
            if not github_username:
                return abort(404, "Team member not found.")

        if not team.github_repo_url:
            return abort(404, "No GitHub repository URL found for this team")

        # Fetch commit details, passing in the username if provided
        commit_details = fetch_commit_details(team.github_repo_url, github_username)

        if "status" in commit_details:
            return abort(int(commit_details["status"]), commit_details["message"])

        return {
            "name": github_username or team.name,
            "githubRepoUrl": team.github_repo_url,
            "totalCommits": commit_details["totalCommits"],
            "linesOfCodeAdded": commit_details["linesOfCodeAdded"],
            "linesOfCodeDeleted": commit_details["linesOfCodeDeleted"],
            "milestones": commit_details["milestones"],
        }

    except ValueError as e:
        return abort(500, str(e))


def fetch_commit_details(repo_url, username=None):
    # Extract owner and repo name from the URL
    repo_url = repo_url.rstrip("/")  # Remove trailing slash if any
    if repo_url.startswith("https://"):
        parts = repo_url.split("/")
        owner = parts[-2]
        repo_name = parts[-1].replace(".git", "")
    elif repo_url.startswith("git@"):
        repo_part = repo_url.split(":")[1]
        owner, repo_name = repo_part.replace(".git", "").split("/")
    else:
        raise ValueError(f"Invalid GitHub URL format: {repo_url}")

    # Get all milestone names and IDs from the database
    milestone_names = {
        milestone.id: milestone.title
        for milestone in db.session.query(Milestones.id, Milestones.title).all()
    }

    # Get the repository
    try:
        repo = github_client.get_repo(f"{owner}/{repo_name}")

        # Initialize general statistics
        commits = repo.get_commits(author=username) if username else repo.get_commits()

        total_commits = 0
        lines_added = 0
        lines_deleted = 0
        milestones_stats = {}

        # Process each commit to collect milestone-related stats
        for commit in commits:
            total_commits += 1
            detailed_commit = repo.get_commit(commit.sha)
            commit_message = commit.commit.message

            # Update general stats
            lines_added += detailed_commit.stats.additions
            lines_deleted += detailed_commit.stats.deletions

            # Check for milestone in commit message in the format "Milestone-<id> <message>"
            if commit_message.lower().startswith("milestone-"):
                try:
                    # Extract milestone ID and fetch the corresponding name
                    milestone_id_str = commit_message.split()[0].split("-")[1]
                    milestone_id = int(milestone_id_str)

                    # Look up the milestone name in the dictionary
                    milestone_name = milestone_names.get(milestone_id)

                    # ignore the milestone whose ids are not present in the database
                    if not milestone_name:
                        continue

                    # Initialize milestone stats if it doesn't exist
                    if milestone_name not in milestones_stats:
                        milestones_stats[milestone_name] = {
                            "name": milestone_name,
                            "commits": 0,
                            "linesOfCodeAdded": 0,
                            "linesOfCodeDeleted": 0,
                        }

                    # Update milestone-specific stats
                    milestones_stats[milestone_name]["commits"] += 1
                    milestones_stats[milestone_name][
                        "linesOfCodeAdded"
                    ] += detailed_commit.stats.additions
                    milestones_stats[milestone_name][
                        "linesOfCodeDeleted"
                    ] += detailed_commit.stats.deletions

                except (IndexError, ValueError):
                    # Skip commits that don't follow the milestone format strictly
                    continue

        # Prepare final milestone list sorted by milestone ID
        milestones = list(milestones_stats.values())

        return {
            "totalCommits": total_commits,
            "linesOfCodeAdded": lines_added,
            "linesOfCodeDeleted": lines_deleted,
            "milestones": milestones,
        }
    except Exception as e:
        return e.data
