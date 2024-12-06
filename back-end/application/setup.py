"""
Module: Application Setup and Configuration
-------------------------------------------
This module sets up and configures the Flask application, including the initialization of extensions, 
blueprints, error handling, and session management.

Dependencies:
-------------
- Flask: For application setup and routing.
- Flask-Migrate: For handling database migrations.
- Flask-Security: For user authentication and role management.
- SQLAlchemy: For ORM-based database interactions.
- Werkzeug: For handling HTTP-related tasks, including exceptions and headers.
- application.models: For interacting with the database models (Users, Roles, etc.).
- application.initial_data: For seeding the database with initial data.
- apis.student.setup and apis.teacher.setup: For registering student and teacher APIs.

Functions:
----------
1. configure_app(app, database_uri, testing)
2. init_extensions(app)
3. register_blueprints(app)
4. setup_error_handlers(app)
5. configure_logging(app)
5. create_app(database_uri, testing=False)

Classes:
--------
1. CustomSessionInterface: Custom session handling for the application.
2. CustomResponse: Custom response handling with CORS headers.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
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
    """
    Class: CustomSessionInterface
    ------------------------------
    Custom session interface for Flask that overrides the default session behavior. This class disables
    setting the session cookie for the application.

    Methods:
    - should_set_cookie(app: Flask, session: SessionMixin) -> bool: Always returns False to prevent
      the session cookie from being set.
    """

    def should_set_cookie(self, app: Flask, session: SessionMixin) -> bool:
        return False


class CustomResponse(Response):
    """
    Class: CustomResponse
    ----------------------
    Custom response class for Flask that sets the default response type to JSON and adds CORS headers
    to the response.

    Attributes:
    - default_mimetype (str): The default mimetype for the response, set to "application/json".

    Methods:
    - __init__(response=None, status=None, headers=None, mimetype=None, content_type=None, direct_passthrough=False):
      Custom constructor that sets CORS headers and initializes the response with the provided parameters.
    """

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
    """
    Function: Configure Application
    -------------------------------
    Configures the Flask application with necessary settings such as the database URI, security settings,
    and other application-specific configurations.

    Parameters:
    - app (Flask): The Flask application instance.
    - database_uri (str): URI for connecting to the database.
    - testing (bool): A flag indicating whether the app is in testing mode.

    Configures the following settings:
    - TESTING: Set based on the `testing` argument.
    - SQLALCHEMY_DATABASE_URI: URI for the database connection.
    - SECRET_KEY: Secret key for sessions and cookies.
    - SECURITY_PASSWORD_SALT: Salt for password hashing.
    - Various other Flask-Security and app-specific configurations.
    """

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
    """
    Function: Initialize Extensions
    ------------------------------
    Initializes the necessary Flask extensions such as SQLAlchemy, Migrate, Flask-Security, and custom session
    and response classes. It also sets up the database and runs the database migrations.

    Parameters:
    - app (Flask): The Flask application instance.

    Behavior:
    - Initializes the database and sets up the migration system.
    - Creates the necessary tables in the database if they do not already exist.
    - Seeds the database with initial data if no users are present.
    - Configures the custom session interface and response class.
    """
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
    """
    Function: Register Blueprints
    -----------------------------
    Registers the student and teacher blueprints with the Flask application.

    Parameters:
    - app (Flask): The Flask application instance.

    Behavior:
    - Registers the `student` and `teacher` blueprints, enabling the respective routes for each.
    """
    app.register_blueprint(student)
    app.register_blueprint(teacher)


def setup_error_handlers(app):
    """
    Function: Set Up Error Handlers
    -------------------------------
    Sets up error handling for HTTP exceptions and unexpected errors.

    Parameters:
    - app (Flask): The Flask application instance.

    Behavior:
    - Registers a handler for HTTP exceptions (e.g., 404 errors) that returns a custom error response.
    - Registers a handler for unexpected exceptions that logs the error and returns a 500 response.
    """

    @app.errorhandler(HTTPException)
    def handle_exception(error):

        app.logger.error(f"An HTTP exception occurred:\n{error}")

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

        app.logger.error(f"An unexpected error occurred:\n{error}")

        response_data = {
            "meta": {"code": 500},
            "response": {"errors": ["An unexpected error occurred. Try again later."]},
        }
        return app.response_class(response=json.dumps(response_data), status=500)


def configure_logging(app):
    """
    Configure logging for the Flask application.

    :param app: Flask application instance
    """

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Create file handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "Tracky.log"),
        maxBytes=10240,
        backupCount=10,
    )

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Set log levels
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)


def create_app(database_uri, testing=False):
    """
    Function: Create Flask Application
    -----------------------------------
    Creates and configures the Flask application, initializes necessary extensions, and registers blueprints.

    :param database_uri (str): URI for the database connection.
    :param testing (bool): A flag indicating whether the app is in testing mode (default is False).

    :returns app (Flask): The configured Flask application instance.
    """
    app = Flask("Tracky")

    configure_app(app, database_uri, testing)
    init_extensions(app)
    register_blueprints(app)
    setup_error_handlers(app)
    if not testing:
        configure_logging(app)

    return app


app = create_app("sqlite:///track.sqlite3")
