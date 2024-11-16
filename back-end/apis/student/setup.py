from application.models import (
    team_students,
    db,
)
from flask import Blueprint
from application.models import db


student = Blueprint("student", __name__, url_prefix="/student")


def get_team_id(user):
    return (
        db.session.query(team_students.c.team_id)
        .filter(team_students.c.student_id == user.id)
        .scalar()
    )


from . import milestone_management, notifications
