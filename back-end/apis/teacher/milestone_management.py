from apis.teacher.setup import (
    teacher,
    get_teams_under_user,
)
from flask_security import current_user, roles_accepted, roles_required
from application.models import Tasks, db, Submissions, Milestones
from flask import abort, request
from datetime import datetime, timezone


@teacher.route("/milestone_management", methods=["GET"])
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


@teacher.route("/milestone_management", methods=["POST"])
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


@teacher.route("/milestone_management/<int:milestone_id>", methods=["GET"])
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


@teacher.route("/milestone_management/<int:milestone_id>", methods=["PUT"])
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


@teacher.route("/milestone_management/<int:milestone_id>", methods=["DELETE"])
@roles_required("Instructor")
def delete_milestone(milestone_id):
    delete_object = Milestones.query.filter_by(id=milestone_id).first()
    if not delete_object:
        return abort(404, "Milestone not found.")

    db.session.delete(delete_object)
    db.session.commit()
    return {"message": "Milestone is deleted"}, 200
