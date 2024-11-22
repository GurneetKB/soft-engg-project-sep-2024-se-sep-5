"""
Module: User Authentication and Role Management
-------------------------------------------------
This module provides APIs for user role management and logging out. It includes functionality for fetching 
user roles and logging out users securely, invalidating authentication tokens to ensure session termination.

Dependencies:
-------------
- Flask: For routing and handling HTTP requests.
- Flask-Security: For user authentication and role management.
- SQLAlchemy ORM: For database operations.
- random: For generating random strings.
- string: For character sets.
- SystemRandom: For secure random number generation.

Routes:
-------
1. GET /user/role
2. GET /logout
"""

from application.setup import (
    app,
)
from application.models import db
from flask import abort
from string import digits, ascii_letters
from random import SystemRandom
from flask_security import (
    current_user,
    logout_user,
)


@app.route("/user/role")
def userroleassign():
    """
    API: Get User Roles
    -------------------
    Fetches the list of roles assigned to the currently authenticated user.

    Authentication:
    - Requires the user to be authenticated.

    Response:
    - 200: JSON array containing role names assigned to the current user.
    - 401: If the user is not authenticated.

    Behavior:
    - Checks if the current user is authenticated and returns their roles.
    """
    if current_user.is_authenticated:
        return [r.name for r in current_user.roles], 200
    else:
        abort(401)


@app.route("/logout")
def logout():
    """
    API: Log Out User
    -------------------
    Logs out the currently authenticated user and invalidates all their authentication tokens by changing the
    `fs_uniquifier` value.

    Authentication:
    - Requires the user to be authenticated.

    Response:
    - 200: JSON message confirming the successful logout.
    - 401: If the user is not authenticated.

    Behavior:
    - Changes the `fs_uniquifier` to a random string to invalidate authentication tokens.
    - Logs out the user by calling `logout_user()`.
    """
    if current_user.is_authenticated:
        # changing the fs_uniquifier so that all the authentication tokens of the current user gets invalidated
        current_user.fs_uniquifier = "".join(
            SystemRandom().choice(ascii_letters + digits) for _ in range(64)
        )
        db.session.commit()
        logout_user()
        return {"message": "You have successfully logged out."}, 200
    else:
        abort(401)
