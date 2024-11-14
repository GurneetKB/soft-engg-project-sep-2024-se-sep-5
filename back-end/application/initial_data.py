from application.models import (
    Roles,
    Users,
    NotificationPreferences,
    Teams,
    Milestones,
    Tasks,
    Submissions,
    Documents,
    Notifications,
    UserNotifications,
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
            github_repo_url="https://github.com/shrasinh/team_alpha",
            instructor=users["instructor"],
            ta=users["ta1"],
            members=[users["student1"], users["student2"], users["student3"]],
        ),
        Teams(
            name="Team Beta",
            github_repo_url="https://github.com/Matrixmang0/team_beta",
            instructor=users["instructor"],
            ta=users["ta1"],
            members=[users["student4"], users["student5"], users["student6"]],
        ),
        Teams(
            name="Team Gamma",
            github_repo_url="https://github.com/shrasinh/team_gamma",
            instructor=users["instructor"],
            ta=users["ta2"],
            members=[users["student7"], users["student8"], users["student9"]],
        ),
        Teams(
            name="Team Delta",
            github_repo_url="https://github.com/Matrixmang0/team-delta",
            instructor=users["instructor"],
            ta=users["ta2"],
            members=[users["student10"], users["student11"], users["student12"]],
        ),
    ]
    for team in teams:
        db.session.add(team)

    # Create milestones and tasks within milestones
    milestones = [
        Milestones(
            title="Project Proposal Due",
            description="Submit your project proposal for approval.",
            deadline=datetime.now(timezone.utc) + timedelta(days=7),
            created_at=datetime.now(timezone.utc),
            created_by=users["instructor"].id,
        ),
        Milestones(
            title="First Prototype Submission",
            description="Submit the first working prototype of your project.",
            deadline=datetime.now(timezone.utc) + timedelta(days=14),
            created_at=datetime.now(timezone.utc),
            created_by=users["instructor"].id,
        ),
        Milestones(
            title="Final Project Presentation",
            description="Prepare for the final presentation of your project.",
            deadline=datetime.now(timezone.utc) + timedelta(days=21),
            created_at=datetime.now(timezone.utc),
            created_by=users["instructor"].id,
        ),
    ]
    for milestone in milestones:
        db.session.add(milestone)

        # Add tasks for each milestone
        tasks = [
            Tasks(
                milestone=milestone,
                description=f"Complete task for {milestone.title}",
            )
        ]
        for task in tasks:
            db.session.add(task)

    # Create sample submissions with documents
    for team in teams:
        for task in tasks:
            submission = Submissions(
                team=team,
                tasks=task,
                submission_time=datetime.now(timezone.utc),
                feedback="Good job on initial submission",
                feedback_by=users["instructor"].id,
                feedback_time=datetime.now(timezone.utc) + timedelta(days=1),
            )
            db.session.add(submission)

            # Add a document to each submission
            document = Documents(
                title=f"{task.description} document",
                file_url="https://example.com/doc.pdf",
                submission=submission,
            )
            db.session.add(document)

    # Create notifications for each student
    for team in teams:
        for student in team.members:
            for milestone in milestones:
                # Deadline notification
                deadline_notification = Notifications(
                    title="Deadline Notification",
                    message=f"The milestone '{milestone.title}' is due on {milestone.deadline.strftime('%Y-%m-%d')}.",
                    type="DEADLINE",
                    created_at=datetime.now(timezone.utc),
                )
                db.session.add(deadline_notification)
                db.session.add(
                    UserNotifications(user=student, notifications=deadline_notification)
                )

                # Feedback notification
                feedback_notification = Notifications(
                    title="Feedback Notification",
                    message=f"You have received feedback on '{milestone.title}'.",
                    type="FEEDBACK",
                    created_at=datetime.now(timezone.utc),
                )
                db.session.add(feedback_notification)
                db.session.add(
                    UserNotifications(user=student, notifications=feedback_notification)
                )

                # Milestone update notification
                milestone_update_notification = Notifications(
                    title="Milestone Update Notification",
                    message=f"The milestone '{milestone.title}' has been updated.",
                    type="MILESTONE_UPDATE",
                    created_at=datetime.now(timezone.utc),
                )
                db.session.add(milestone_update_notification)
                db.session.add(
                    UserNotifications(
                        user=student, notifications=milestone_update_notification
                    )
                )

    # Commit all changes
    db.session.commit()
