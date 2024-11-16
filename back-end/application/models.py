from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from sqlalchemy import MetaData
from enum import Enum


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


class NotificationType(str, Enum):
    DEADLINE = "DEADLINE"
    FEEDBACK = "FEEDBACK"
    MILESTONE_UPDATE = "MILESTONE_UPDATE"


team_students = db.Table(
    "team_students",
    db.Column("team_id", db.Integer(), db.ForeignKey("teams.id", ondelete="CASCADE")),
    db.Column(
        "student_id", db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE")
    ),
)

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
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    github_username = db.Column(db.String)
    roles = db.relationship(
        "Roles", secondary="UsersRoles", back_populates="users", lazy="subquery"
    )
    teams_as_instructor = db.relationship(
        "Teams",
        back_populates="instructor",
        foreign_keys="Teams.instructor_id",
        lazy="subquery",
    )
    teams_as_ta = db.relationship(
        "Teams", back_populates="ta", foreign_keys="Teams.ta_id", lazy="subquery"
    )
    created_milestones = db.relationship(
        "Milestones",
        back_populates="creator",
        foreign_keys="Milestones.created_by",
        lazy="subquery",
    )
    teams_as_member = db.relationship(
        "Teams",
        secondary=team_students,
        back_populates="members",
        lazy="subquery",
    )
    notification_preferences = db.relationship(
        "NotificationPreferences",
        back_populates="user",
        uselist=False,
        cascade="all, delete",
    )
    notifications = db.relationship(
        "UserNotifications",
        back_populates="user",
        lazy="subquery",
        cascade="all, delete",
    )


class Roles(db.Model, RoleMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String, nullable=False)
    users = db.relationship(
        "Users", secondary="UsersRoles", back_populates="roles", lazy="subquery"
    )


class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    github_repo_url = db.Column(db.String)
    instructor_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    ta_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    members = db.relationship(
        "Users",
        secondary=team_students,
        back_populates="teams_as_member",
        lazy="subquery",
    )
    submissions = db.relationship(
        "Submissions", back_populates="team", lazy="subquery", cascade="all, delete"
    )
    instructor = db.relationship(
        "Users",
        back_populates="teams_as_instructor",
        foreign_keys=[instructor_id],
        lazy="subquery",
        uselist=False,
    )
    ta = db.relationship(
        "Users",
        back_populates="teams_as_ta",
        foreign_keys=[ta_id],
        lazy="subquery",
        uselist=False,
    )


class Milestones(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    creator = db.relationship(
        "Users", back_populates="created_milestones", lazy="subquery"
    )
    task_milestones = db.relationship(
        "Tasks",
        back_populates="milestone",
        lazy="subquery",
        cascade="all, delete",
    )


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    milestone_id = db.Column(
        db.Integer,
        db.ForeignKey("milestones.id", ondelete="CASCADE"),
        nullable=False,
    )
    description = db.Column(db.Text, nullable=False)
    milestone = db.relationship(
        "Milestones", back_populates="task_milestones", lazy="subquery", uselist=False
    )
    submissions = db.relationship(
        "Submissions",
        back_populates="task",
        lazy="subquery",
        cascade="all, delete",
    )


class Submissions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id", ondelete="CASCADE"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"))
    submission_time = db.Column(db.DateTime)
    feedback = db.Column(db.Text)
    feedback_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    feedback_time = db.Column(db.DateTime)
    documents = db.relationship(
        "Documents",
        back_populates="submission",
        lazy="subquery",
        cascade="all, delete",
        uselist=False,
    )
    team = db.relationship("Teams", back_populates="submissions", lazy="subquery")
    task = db.relationship(
        "Tasks", back_populates="submissions", lazy="subquery", uselist=False
    )


class Documents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    file_url = db.Column(db.String)
    submission_id = db.Column(
        db.Integer, db.ForeignKey("submissions.id", ondelete="CASCADE")
    )
    submission = db.relationship(
        "Submissions",
        back_populates="documents",
        lazy="subquery",
        uselist=False,
    )


class AIProgressText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    generated_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    text = db.Column(db.JSON, nullable=False)


class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum(NotificationType), nullable=False)
    created_at = db.Column(db.DateTime)
    user_notifications = db.relationship(
        "UserNotifications",
        back_populates="notifications",
        lazy="subquery",
        uselist=False,
    )


class UserNotifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(
        db.Integer,
        db.ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    read_at = db.Column(db.DateTime)
    user = db.relationship(
        "Users", back_populates="notifications", lazy="subquery", uselist=False
    )
    notifications = db.relationship(
        "Notifications",
        back_populates="user_notifications",
        lazy="subquery",
        uselist=False,
    )


class NotificationPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    email_deadline_notifications = db.Column(db.Boolean, default=True, nullable=False)
    in_app_deadline_notifications = db.Column(db.Boolean, default=True, nullable=False)
    email_feedback_notifications = db.Column(db.Boolean, default=True, nullable=False)
    in_app_feedback_notifications = db.Column(db.Boolean, default=True, nullable=False)
    deadline_advance_days = db.Column(db.Integer, default=1)
    user = db.relationship(
        "Users",
        back_populates="notification_preferences",
        uselist=False,
    )
