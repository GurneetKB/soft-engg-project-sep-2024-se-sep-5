from flask_restful import Resource, reqparse, fields, marshal
from application.models import Submissions, Tasks, Teams, db, Milestones
from datetime import datetime
from flask import request, jsonify
from flask_security import current_user, roles_accepted


milestone_fields = {
    "id": fields.Integer,
    "title": fields.String,
    "description": fields.String,
    "deadline": fields.DateTime,
    "completion_rate": fields.Float,
}

milestone_update = reqparse.RequestParser()

milestone_update.add_argument(
    "title",
    type=str,
    help="title is required and should be a string",
    required=True,
)
milestone_update.add_argument(
    "description",
    type=str,
    help="description is required and should be a string",
    required=True,
)


class MilestoneAPI(Resource):

    @roles_accepted("Instructor")
    def post(self):
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        deadline = data.get("deadline")
        deadline = datetime.fromisoformat(deadline)

        # requirements = data.get("requirements")
        milestone_object = Milestones(
            title=title,
            description=description,
            deadline=deadline,
            created_by=current_user.id if current_user.is_authenticated else None,
            created_at=datetime.utcnow(),
        )
        db.session.add(milestone_object)
        db.session.commit()

        return {"message": "milestone  published successfully."}, 200

    @roles_accepted("Instructor", "TA")
    def get(self, milestone_id):
        milestone_object = Milestones.query.filter_by(id=milestone_id).first()
        return marshal(milestone_object, milestone_fields)

    @roles_accepted("Instructor")
    def put(self, milestone_id):
        # Fetch the milestone by ID
        milestone_object = Milestones.query.filter_by(id=milestone_id).first()

        # Check if the milestone exists
        if not milestone_object:
            return {"message": "Milestone not found."}, 404

        # Parse arguments
        args = milestone_update.parse_args()

        # Check for required fields and update milestone fields
        if "title" in args and args["title"]:
            milestone_object.title = args["title"]
        if "description" in args and args["description"]:
            milestone_object.description = args["description"]

        # Commit changes
        try:
            db.session.commit()
            return {"message": "Milestone updated successfully."}, 200
        except Exception as e:
            db.session.rollback()  # Roll back in case of any error
            return {"message": "An error occurred while updating the milestone."}, 500

    @roles_accepted("Instructor")
    def delete(self, milestone_id):
        delete_object = Milestones.query.filter_by(id=milestone_id).first()
        db.session.delete(delete_object)
        db.session.commit()
        return jsonify({"status": "deleted", "message": "Milestone is deleted"})


class MilestoneAllAPI(Resource):

    @roles_accepted("Instructor", "TA")
    def get(self):
        # Get all milestones
        milestone_objects = Milestones.query.all()

        # Get teams based on user role
        teams_query = Teams.query
        if current_user.has_role("TA"):
            teams_query = teams_query.filter(Teams.ta_id == current_user.id)
        elif current_user.has_role("Instructor"):
            teams_query = teams_query.filter(Teams.instructor_id == current_user.id)

        # Get total number of teams for this user
        total_teams = teams_query.count()

        # If there are no teams, avoid division by zero
        if total_teams == 0:
            return marshal(milestone_objects, milestone_fields)

        for milestone in milestone_objects:
            # Get all tasks for this milestone
            tasks = milestone.task_milestones

            if not tasks:
                milestone.completion_rate = 0.0
                continue

            # Count teams under this TA/instructor that completed all tasks
            completed_teams = (
                db.session.query(Submissions.team_id)
                .join(Tasks, Tasks.id == Submissions.task_id)
                .join(Teams, Teams.id == Submissions.team_id)
                .filter(
                    Tasks.milestone_id == milestone.id,
                    Teams.id.in_(teams_query.with_entities(Teams.id)),
                )
                .group_by(Submissions.team_id)
                .having(db.func.count(db.distinct(Submissions.task_id)) == len(tasks))
                .count()
                or 0
            )

            # Calculate completion rate as percentage
            milestone.completion_rate = (completed_teams / total_teams) * 100

        return marshal(milestone_objects, milestone_fields)
