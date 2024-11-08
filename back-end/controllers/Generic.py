from application.setup import (
    app,
    CustomResponse,
)
from application.models import db, UsersRoles
from flask import abort, json, jsonify
from werkzeug.exceptions import HTTPException
from string import digits, ascii_letters
from random import SystemRandom
from flask_security import (
    current_user,
    logout_user,
)
from sqlalchemy import select


@app.errorhandler(HTTPException)
def handle_exception(error):
    data = json.dumps(
        {
            "response": {
                "errors": (
                    [error.description]
                    if isinstance(error.description, str)
                    else error.description
                )
            }
        }
    )
    return CustomResponse(data, status=error.code)


@app.route("/user/role")
def userroleassign():
    if current_user.is_authenticated:
        return [r.name for r in current_user.roles], 200
    else:
        abort(401)


@app.route("/logout")
def logout():
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



@app.route("/student/all", methods=["GET"])
def get_all_students():
    print("Fetching all students...")

    try:
        # Corrected select statement without square brackets
        stmt = select(UsersRoles).where(UsersRoles.c.role_id == 3)
        result = db.session.execute(stmt)
        
        # Convert each row to a dictionary for JSON serialization
        students = [{"id": row.id, "user_id": row.user_id, "role_id": row.role_id} for row in result]
        
        print("Students fetched successfully:", students)
        return jsonify(students), 200

    except Exception as e:
        print("Error fetching students:", str(e))
        return jsonify({"error": "An error occurred while fetching students"}), 500