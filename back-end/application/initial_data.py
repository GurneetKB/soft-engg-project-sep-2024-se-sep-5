from application.models import (
    Roles,
    Users,
    NotificationPreferences,
    Teams,
    Milestones,
    Notifications,
    TeamMilestones,
)
from flask_security import hash_password
from datetime import datetime, timedelta, timezone


def seed_database(db):
    # Create roles
    roles = {
        "instructor": Roles(name="Instructor", description="Course instructor role"),
        "ta": Roles(name="TA", description="Teaching assistant role"),
        "student": Roles(name="Student", description="Student role"),
    }
    for role in roles.values():
        db.session.add(role)

    # Create users
    users = {
        # Instructor
        "instructor": Users(
            username="profsmith",
            email="smith@university.edu",
            password=hash_password("password123"),
            active=True,
            fs_uniquifier="instructor1",
            roles=[roles["instructor"]],
        ),
        # TAs
        "ta1": Users(
            username="tajones",
            email="jones@university.edu",
            password=hash_password("password123"),
            active=True,
            fs_uniquifier="ta1",
            roles=[roles["ta"]],
        ),
        "ta2": Users(
            username="tabrown",
            email="brown@university.edu",
            password=hash_password("password123"),
            active=True,
            fs_uniquifier="ta2",
            roles=[roles["ta"]],
        ),
        # Students (12)
        **{
            f"student{i}": Users(
                username=f"student{i}",
                email=f"student{i}@university.edu",
                password=hash_password("password123"),
                active=True,
                fs_uniquifier=f"student{i}",
                roles=[roles["student"]],
            )
            for i in range(1, 13)
        },
    }

    for user in users.values():
        db.session.add(user)

    # Create notification preferences only for students
    for user in users.values():
        if "student" in user.username:
            db.session.add(NotificationPreferences(user=user))

    # Create teams
    teams = [
        Teams(
            name="Team Alpha",
            github_repo_url="https://github.com/team-alpha/project",
            instructor=users["instructor"],
            ta=users["ta1"],
            members=[users["student1"], users["student2"], users["student3"]],
        ),
        Teams(
            name="Team Beta",
            github_repo_url="https://github.com/team-beta/project",
            instructor=users["instructor"],
            ta=users["ta1"],
            members=[users["student4"], users["student5"], users["student6"]],
        ),
        Teams(
            name="Team Gamma",
            github_repo_url="https://github.com/team-gamma/project",
            instructor=users["instructor"],
            ta=users["ta2"],
            members=[users["student7"], users["student8"], users["student9"]],
        ),
        Teams(
            name="Team Delta",
            github_repo_url="https://github.com/team-delta/project",
            instructor=users["instructor"],
            ta=users["ta2"],
            members=[users["student10"], users["student11"], users["student12"]],
        ),
    ]

    for team in teams:
        db.session.add(team)

    # Create milestones
    milestones = [
        Milestones(
            title="Project Proposal Due",
            description="Submit your project proposal for approval.",
            deadline=datetime.now(timezone.utc) + timedelta(days=7),  # 1 week from now
            created_at=datetime.now(timezone.utc),
            created_by=users["instructor"].id,
            requirements={"format": "PDF", "length": "2-3 pages"},
        ),
        Milestones(
            title="First Prototype Submission",
            description="Submit the first working prototype of your project.",
            deadline=datetime.now(timezone.utc)
            + timedelta(days=14),  # 2 weeks from now
            created_at=datetime.now(timezone.utc),
            created_by=users["instructor"].id,
            requirements={"format": "GitHub repo link"},
        ),
        Milestones(
            title="Final Project Presentation",
            description="Prepare for the final presentation of your project.",
            deadline=datetime.now(timezone.utc)
            + timedelta(days=21),  # 3 weeks from now
            created_at=datetime.now(timezone.utc),
            created_by=users["instructor"].id,
            requirements={"format": "Slide deck"},
        ),
    ]

    for milestone in milestones:
        db.session.add(milestone)
        # Associate milestones with teams
        for team in teams:
            team_milestone = TeamMilestones(team=team, milestone=milestone)
            db.session.add(team_milestone)

    # Create notifications only for students
    notification_types = ["DEADLINE", "FEEDBACK", "MILESTONE_UPDATE"]
    for team in teams:
        for student in team.members:
            for milestone in milestones:
                # Deadline notifications
                notification = Notifications(
                    user=student,  # Send notification to each student
                    title=f"{notification_types[0].capitalize()} Notification",
                    message=f"The milestone '{milestone.title}' is due on {milestone.deadline.strftime('%Y-%m-%d')}.",
                    type=notification_types[0],
                    created_at=datetime.now(timezone.utc),
                    read_at=None,
                )
                db.session.add(notification)

                # Feedback notifications
                feedback_notification = Notifications(
                    user=student,  # Send to the same student
                    title=f"{notification_types[1].capitalize()} Notification",
                    message=f"You have received feedback on your submission for '{milestone.title}'.",
                    type=notification_types[1],
                    created_at=datetime.now(timezone.utc),
                    read_at=None,
                )
                db.session.add(feedback_notification)

                # Milestone update notifications
                milestone_update_notification = Notifications(
                    user=student,  # Send to the same student
                    title=f"{notification_types[2].capitalize()} Notification",
                    message=f"The milestone '{milestone.title}' has been updated.",
                    type=notification_types[2],
                    created_at=datetime.now(timezone.utc),
                    read_at=None,
                )
                db.session.add(milestone_update_notification)

    # Commit all changes
    db.session.commit()
