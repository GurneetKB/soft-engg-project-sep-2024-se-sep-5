
from flask_restful import Resource, Api, reqparse, fields, marshal, abort
from application.models import db, Milestones
from datetime import datetime, timezone
from flask import abort, request, jsonify
from flask_security import current_user, roles_required



milestone_fields = {
    "id": fields.Integer,
    "title": fields.String,
    "description": fields.String,
    "deadline": fields.DateTime,

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
    required=True
)

class MilestoneAPI(Resource):
    def post(self):
        print("inside api")
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        deadline = data.get("deadline")
        deadline = datetime.fromisoformat(deadline)

        #requirements = data.get("requirements")
        milestone_object = Milestones(title = title, description = description, deadline = deadline,created_by=current_user.id if current_user.is_authenticated else None, created_at =datetime.utcnow())
        db.session.add(milestone_object)
        db.session.commit()

        return {"message": "milestone  published successfully."}, 200
    
    def get(self, milestone_id):
        print("inside get api")
        milestone_object = Milestones.query.filter_by(id=milestone_id).first()
        return marshal(milestone_object, milestone_fields)
    

    def put(self, milestone_id):
        print("Inside edit API")

        # Fetch the milestone by ID
        milestone_object = Milestones.query.filter_by(id=milestone_id).first()

        # Check if the milestone exists
        if not milestone_object:
            return {"message": "Milestone not found."}, 404

        # Parse arguments
        args = milestone_update.parse_args()
        print(args)

        # Check for required fields and update milestone fields
        if "title" in args and args["title"]:
            milestone_object.title = args["title"]
        if "description" in args and args["description"]:
            milestone_object.description = args["description"]

        # Commit changes
        try:
            db.session.commit()
            print("Milestone updated:", milestone_object)
            return {"message": "Milestone updated successfully."}, 200
        except Exception as e:
            db.session.rollback()  # Roll back in case of any error
            print("Error updating milestone:", e)
            return {"message": "An error occurred while updating the milestone."}, 500
    
    


class MilestoneAllAPI(Resource):    
    def get(self):
        print("inside get api")
        milestone_object = Milestones.query.all()
        return marshal(milestone_object, milestone_fields)
    

  
    

