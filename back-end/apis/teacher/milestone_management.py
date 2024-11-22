"""
Module: Teacher Milestone Management APIs
------------------------------------------
This module provides APIs for instructors and teaching assistants to manage milestones and tasks for student teams.
It allows for creating, reading, updating, and deleting milestones, as well as tracking milestone progress.

Dependencies:
- Flask: For routing and handling HTTP requests.
- Flask-Security: For role-based access control.
- SQLAlchemy ORM: For database operations.
- datetime, timezone: For date and time operations.

Roles Required:
- Instructor: Full access to all endpoints.
- TA (Teaching Assistant): Limited access to read-only endpoints.

Endpoints:
----------
1. GET /teacher/milestone_management
2. POST /teacher/milestone_management
3. GET /teacher/milestone_management/<int:milestone_id>
4. PUT /teacher/milestone_management/<int:milestone_id>
5. DELETE /teacher/milestone_management/<int:milestone_id>
"""

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
    """
    API: Get All Milestones and Progress Overview
    ----------------------------------------------
    Retrieves a list of all milestones, including their details and completion rates for the teams under the current user.

    Roles Accepted:
    - Instructor
    - TA

    Response:
    - 200: JSON object containing:
        - Total number of teams and students under the user.
        - List of milestones, each with:
            - ID
            - Title
            - Description
            - Deadline
            - Completion rate (percentage of teams that have completed the milestone).
    - 403: If the user does not have the required role.
    - 500: Internal server error.

    Behavior:
    - Calculates completion rates by analyzing submissions against the tasks in each milestone.
    """

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

    return response_data, 200


@teacher.route("/milestone_management", methods=["POST"])
@roles_required("Instructor")
def create_milestone():
    """
    API: Create a New Milestone
    ---------------------------
    Allows instructors to create a new milestone with tasks and a deadline.

    Role Required:
    - Instructor

    Request:
    - JSON object containing:
        - title (string): Title of the milestone.
        - description (string): Description of the milestone.
        - deadline (string): Deadline in GMT datetime format.
        - tasks (list of objects): Each object contains a "description" field for the task.

    Response:
    - 201: JSON message confirming successful creation of the milestone.
    - 400: If validation errors occur, such as:
        - Missing or invalid title, description, or deadline.
        - Invalid task structure.
    - 403: If the user does not have the required role.
    - 500: Internal server error.

    Behavior:
    - Validates input data and ensures the deadline is in the future.
    - Creates tasks and associates them with the milestone.
    """
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
    """
    API: Get Milestone Details
    ---------------------------
    Fetches detailed information about a specific milestone, including its tasks.

    Role Required:
    - Instructor

    Path Parameters:
    - milestone_id (int): ID of the milestone to fetch.

    Response:
    - 200: JSON object containing:
        - Title
        - Description
        - Deadline
        - List of tasks, each with:
            - Description.
    - 404: If the milestone is not found.
    - 403: If the user does not have the required role.
    - 500: Internal server error.

    Behavior:
    - Returns milestone details along with its associated tasks.
    """
    milestone_object = Milestones.query.filter_by(id=milestone_id).first()
    if not milestone_object:
        return abort(404, "Milestone not found.")

    milestone_data = {
        "title": milestone_object.title,
        "description": milestone_object.description,
        "deadline": milestone_object.deadline,
        "tasks": [
            {"description": task.description}
            for task in milestone_object.task_milestones
        ],
    }

    return milestone_data, 200


@teacher.route("/milestone_management/<int:milestone_id>", methods=["PUT"])
@roles_required("Instructor")
def update_milestone(milestone_id):
    """
    API: Update an Existing Milestone
    ----------------------------------
    Allows instructors to update the title, description, deadline, and tasks of a milestone.

    Role Required:
    - Instructor

    Path Parameters:
    - milestone_id (int): ID of the milestone to update.

    Request:
    - JSON object containing any of the following optional fields:
        - title (string): Updated title.
        - description (string): Updated description.
        - deadline (string): Updated deadline in GMT datetime format.
        - tasks (list of objects): Each object contains a "description" field for the task.

    Response:
    - 201: JSON message confirming successful update of the milestone.
    - 400: If validation errors occur, such as:
        - Invalid or missing fields.
        - Deadline not in the future.
    - 404: If the milestone is not found.
    - 403: If the user does not have the required role.
    - 500: Internal server error.

    Behavior:
    - Replaces existing tasks with the new task list if provided.
    - Validates all updated fields before committing changes.
    """
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
    """
    API: Delete a Milestone
    ------------------------
    Deletes a milestone along with its associated tasks.

    Role Required:
    - Instructor

    Path Parameters:
    - milestone_id (int): ID of the milestone to delete.

    Response:
    - 200: JSON message confirming the deletion of the milestone.
    - 404: If the milestone is not found.
    - 403: If the user does not have the required role.
    - 500: Internal server error.

    Behavior:
    - Removes the milestone and all its associated tasks from the database.
    """
    delete_object = Milestones.query.filter_by(id=milestone_id).first()
    if not delete_object:
        return abort(404, "Milestone not found.")

    db.session.delete(delete_object)
    db.session.commit()
    return {"message": "Milestone is deleted"}, 200
