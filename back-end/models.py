from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_security import UserMixin, RoleMixin
from enum import Enum

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

db = SQLAlchemy(metadata=MetaData(naming_convention=convention))

UsersRoles = db.Table(
    "UsersRoles",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id")),
)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean)
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String)
    current_login_ip = db.Column(db.String)
    login_count = db.Column(db.Integer)
    confirmed_at = db.Column(db.DateTime)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    roles = db.relationship(
        "Roles", secondary="UsersRoles", back_populates="users", lazy="subquery"
    )


class Roles(db.Model, RoleMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String, nullable=False)
    users = db.relationship(
        "Users", secondary="UsersRoles", back_populates="roles", lazy="subquery"
    )


class DocumentType(Enum):
    PDF = "pdf"
    DOC = "doc"
    MARKDOWN = "md"
    CODE = "code"
    OTHER = "other"


class Status(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    COMPLETED = "completed"


# Association Tables
TeamStudents = db.Table(
    "team_students",
    db.Model.metadata,
    db.Column("team_id", db.Integer, db.ForeignKey("teams.id")),
    db.Column("student_id", db.Integer, db.ForeignKey("users.id")),
)


class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    github_repo_url = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    members = db.relationship("Users", secondary=TeamStudents, backref="teams")
    instructor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    ta_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    submissions = db.relationship("Submissions", backref="team")
    milestones = db.relationship("Milestones", secondary="team_milestones")


class Milestones(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime, nullable=False)
    requirements = db.Column(db.JSON)
    status = db.Column(db.Enum(Status), default=Status.NOT_STARTED)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    submissions = db.relationship("Submissions", backref="milestone")


class TeamMilestones(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    milestone_id = db.Column(db.Integer, db.ForeignKey("milestones.id"))
    status = db.Column(db.Enum(Status), default=Status.NOT_STARTED)


class Submissions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    milestone_id = db.Column(db.Integer, db.ForeignKey("milestones.id"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    submission_time = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.Text)
    feedback_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    feedback_time = db.Column(db.DateTime)
    documents = db.relationship("Documents", backref="submission")


class Documents(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text)
    file_url = db.Column(db.String)
    type = db.Column(db.Enum(DocumentType))
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ai_analysis = db.Column(db.JSON)


class GitHubMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    commit_count = db.Column(db.Integer)
    lines_added = db.Column(db.Integer)
    lines_removed = db.Column(db.Integer)
    contributors = db.Column(db.JSON)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    user = db.relationship("Users", backref="notifications")
