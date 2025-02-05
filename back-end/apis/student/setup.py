"""
Module: Student Blueprint Setup
--------------------------------
This module sets up the Flask Blueprint for student-related APIs and provides helper functions 
for retrieving data related to teams and students. It also imports submodules for specific functionalities 
like milestone management and notifications.

Dependencies:
- Flask: For creating a Blueprint.
- SQLAlchemy ORM: For database operations.
- os: For getting environment variables.
- Groq: For AI tool integration.

Blueprint:
----------
- Name: student
- URL Prefix: /student

Global Variables:
-----------------
1. `ai_client`: Configured AI client using an API key.

Submodules:
-----------
1. milestone_management: Handles milestone-related functionalities.
2. notifications: Manages notifications for students.

Functions:
----------
1. get_team_id(user)
"""

from application.models import (
    team_students,
    db,
)
from flask import Blueprint
from groq import Groq
import os


student = Blueprint("student", __name__, url_prefix="/student")

# AI configuration
ai_client = Groq(api_key=os.environ.get("AI_ACCESS_TOKEN"))


def get_team_id(user):
    """
    Function: Get Team ID
    ----------------------
    Fetches the team ID for a given user by querying the association table `team_students`.

    Parameters:
    - user: The current user object whose team ID needs to be retrieved.

    Returns:
    - team_id (int): The ID of the team associated with the user.
    - None: If the user is not associated with any team.

    Database Interaction:
    - Queries the `team_students` table for the `team_id` corresponding to the `student_id` of the given user.
    """
    return (
        db.session.query(team_students.c.team_id)
        .filter(team_students.c.student_id == user.id)
        .scalar()
    )


from . import milestone_management, notifications
