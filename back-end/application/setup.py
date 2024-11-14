from flask import Flask, Response
from flask.sessions import SecureCookieSessionInterface, SessionMixin
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from application.models import Users, Roles, db
from application.initial_data import seed_database
from github import Github, Auth
import os


# instantiate the flask application
app = Flask("Tracky")

## for flask-sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///track.sqlite3"

# GitHub configuration
github_auth = Auth.Token(os.environ.get("GITHUB_ACCESS_TOKEN"))
github_client = Github(auth=github_auth)

## for flask-security-too
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
)
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get(
    "SECURITY_PASSWORD_SALT", "146585145368132386173505678016728509634"
)
app.config["SECURITY_TRACKABLE"] = True
app.config["SECURITY_USERNAME_ENABLE"] = True
app.config["SECURITY_USERNAME_REQUIRED"] = True
app.config["SECURITY_LOGOUT_METHODS"] = None
app.config["SECURITY_TOKEN_MAX_AGE"] = 60 * 60 * 24
app.config["WTF_CSRF_ENABLED"] = False

app.config["UPLOAD_FOLDER"] = "student_submissions"


# initializing flask-migrate
migrate = Migrate(app, db)

# initializing flask-security-too
user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)
app.security = Security(app, user_datastore)


with app.app_context():

    db.init_app(app)  # initializing flask-sqlalchemy

    db.create_all()  # create the tables if not created

    if not Users.query.first():  # if instructor role is not created
        seed_database(db)


## disabling sending of cookie
class CustomSessionInterface(SecureCookieSessionInterface):
    def should_set_cookie(self, app: Flask, session: SessionMixin) -> bool:
        return False


app.session_interface = CustomSessionInterface()


## adding the headers that allow cross-origin requests and jsonifying the response
class CustomResponse(Response):

    default_mimetype = "application/json"

    def __init__(self, response=None, *args, **kwargs):
        kwargs["headers"] = {
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Headers": "Authentication-Token,Content-Type",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Expose-Headers": "Content-Disposition",
        }
        return super(CustomResponse, self).__init__(response, *args, **kwargs)


app.response_class = CustomResponse
