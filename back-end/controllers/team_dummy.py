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
