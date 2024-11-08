from application.setup import app
from flask_security import current_user, roles_accepted
from application.models import (
    Notifications,
    NotificationPreferences,
    db,
    Milestones,
    Teams,
)
from flask import abort, request
from datetime import datetime, timezone


@app.route("/instructor/milestone/publish", methods=["POST"])
@roles_accepted("Instructor", "TA")
def publishMilestones():
    # Parse the request JSON for preference settings
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    deadline = data.get("deadline")
    deadline = datetime.fromisoformat(deadline)

    milestoneToUpload = Milestones(
        title=title,
        description=description,
        deadline=deadline,
        created_by=current_user.id if current_user.is_authenticated else None,
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(milestoneToUpload)
    db.session.commit()

    return {"message": "milestone  published successfully."}, 200


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
