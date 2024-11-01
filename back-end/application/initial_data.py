from application.models import Roles, Users, NotificationPreferences, Teams
from flask_security import hash_password


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

    # Commit all changes
    db.session.commit()
