from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin, AsaList
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime
from enum import Enum
from sqlalchemy import MetaData

# Define naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Initialize SQLAlchemy with naming convention
db = SQLAlchemy(metadata=MetaData(naming_convention=convention))

# Association Tables
roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("users.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("roles.id")),
)

team_students = db.Table(
    "team_students",
    db.Column("team_id", db.Integer(), db.ForeignKey("teams.id", ondelete="CASCADE")),
    db.Column(
        "student_id", db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE")
    ),
)


# Enums
class DocumentType(str, Enum):
    PDF = "pdf"
    DOC = "doc"
    MARKDOWN = "md"
    CODE = "code"
    OTHER = "other"


class Status(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    COMPLETED = "completed"


class Users(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())

    # Security tracking
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer, default=0)

    # Relationships
    roles = db.relationship(
        "Roles",
        secondary=roles_users,
        backref=db.backref("users", lazy="dynamic"),
    )
    teams_as_instructor = db.relationship(
        "Teams",
        backref="instructor",
        foreign_keys="Teams.instructor_id",
        lazy="dynamic",
    )
    teams_as_ta = db.relationship(
        "Teams", backref="ta", foreign_keys="Teams.ta_id", lazy="dynamic"
    )
    created_milestones = db.relationship(
        "Milestones",
        backref="creator",
        foreign_keys="Milestones.created_by",
        lazy="dynamic",
    )


class Roles(db.Model, RoleMixin):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    permissions = db.Column(MutableList.as_mutable(AsaList()), nullable=True)


class Teams(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    github_repo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Keys
    instructor_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    ta_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))

    # Relationships
    members = db.relationship(
        "Users",
        secondary=team_students,
        backref=db.backref("teams_as_member", lazy="dynamic"),
    )
    submissions = db.relationship(
        "Submissions", backref="team", lazy="dynamic", cascade="all, delete-orphan"
    )
    github_metrics = db.relationship(
        "GitHubMetrics", backref="team", lazy="dynamic", cascade="all, delete-orphan"
    )


class Milestones(db.Model):
    __tablename__ = "milestones"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime, nullable=False)
    requirements = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))

    # Relationships
    team_milestones = db.relationship(
        "TeamMilestones",
        backref="milestone",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class TeamMilestones(db.Model):
    __tablename__ = "team_milestones"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"))
    milestone_id = db.Column(
        db.Integer, db.ForeignKey("milestones.id", ondelete="CASCADE")
    )
    status = db.Column(db.Enum(Status), default=Status.NOT_STARTED)

    team = db.relationship(
        "Teams", backref=db.backref("milestone_status", lazy="dynamic")
    )


class Submissions(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    milestone_id = db.Column(
        db.Integer, db.ForeignKey("milestones.id", ondelete="CASCADE")
    )
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"))
    submission_time = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.Text)
    feedback_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    feedback_time = db.Column(db.DateTime)

    # Relationships
    documents = db.relationship(
        "Documents", backref="submission", lazy="dynamic", cascade="all, delete-orphan"
    )
    reviewer = db.relationship("Users", foreign_keys=[feedback_by])


class Documents(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    file_url = db.Column(db.String(255))
    type = db.Column(db.Enum(DocumentType))
    submission_id = db.Column(
        db.Integer, db.ForeignKey("submissions.id", ondelete="CASCADE")
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ai_analysis = db.Column(db.JSON)


class GitHubMetrics(db.Model):
    __tablename__ = "github_metrics"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"))
    commit_count = db.Column(db.Integer, default=0)
    lines_added = db.Column(db.Integer, default=0)
    lines_removed = db.Column(db.Integer, default=0)
    contributors = db.Column(db.JSON)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notifications(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)

    user = db.relationship("Users", backref=db.backref("notifications", lazy="dynamic"))
