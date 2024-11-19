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
