import os
from flask import Flask, Response, json
from flask.sessions import SecureCookieSessionInterface, SessionMixin
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from werkzeug.datastructures import Headers
from werkzeug.exceptions import HTTPException

from application.models import Users, Roles, db
from application.initial_data import seed_database
from apis.student.setup import student
from apis.teacher.setup import teacher


class CustomSessionInterface(SecureCookieSessionInterface):
    def should_set_cookie(self, app: Flask, session: SessionMixin) -> bool:
        return False


class CustomResponse(Response):
    default_mimetype = "application/json"

    def __init__(
        self,
        response=None,
        status=None,
        headers=None,
        mimetype=None,
        content_type=None,
        direct_passthrough=False,
    ):
        default_cors_headers = {
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Headers": "Authentication-Token,Content-Type",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Expose-Headers": "Content-Disposition",
        }

        if headers is None:
            headers = {}

        if isinstance(headers, dict):
            headers = Headers(headers)

        for key, value in default_cors_headers.items():
            if key not in headers:
                headers.add(key, value)

        super().__init__(
            response=response,
            status=status,
            headers=headers,
            mimetype=mimetype,
            content_type=content_type,
            direct_passthrough=direct_passthrough,
        )


def configure_app(app, database_uri, testing):
    app.config.update(
        TESTING=testing,
        SQLALCHEMY_DATABASE_URI=database_uri,
        SECRET_KEY=os.environ.get(
            "SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
        ),
        SECURITY_PASSWORD_SALT=os.environ.get(
            "SECURITY_PASSWORD_SALT", "146585145368132386173505678016728509634"
        ),
        SECURITY_TRACKABLE=True,
        SECURITY_USERNAME_ENABLE=True,
        SECURITY_USERNAME_REQUIRED=True,
        SECURITY_LOGOUT_METHODS=None,
        SECURITY_TOKEN_MAX_AGE=60 * 60 * 24,
        WTF_CSRF_ENABLED=False,
        UPLOAD_FOLDER="student_submissions",
    )


def init_extensions(app):
    db.init_app(app)
    Migrate(app, db)

    user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)
    app.security = Security(app, user_datastore)

    with app.app_context():
        db.create_all()
        if not Users.query.first():
            seed_database(db)

    app.session_interface = CustomSessionInterface()
    app.response_class = CustomResponse


def register_blueprints(app):
    app.register_blueprint(student)
    app.register_blueprint(teacher)


def setup_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_exception(error):
        response_data = {
            "meta": {"code": error.code},
            "response": {
                "errors": (
                    [error.description]
                    if isinstance(error.description, str)
                    else error.description
                )
            },
        }
        return app.response_class(response=json.dumps(response_data), status=error.code)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.error(f"Unexpected error: {str(error)}")
        response_data = {
            "meta": {"code": 500},
            "response": {"errors": [str(error)]},
        }
        return app.response_class(response=json.dumps(response_data), status=500)


def create_app(database_uri, testing=False):
    app = Flask("Tracky")

    configure_app(app, database_uri, testing)
    init_extensions(app)
    register_blueprints(app)
    setup_error_handlers(app)

    return app


app = create_app("sqlite:///track.sqlite3")
