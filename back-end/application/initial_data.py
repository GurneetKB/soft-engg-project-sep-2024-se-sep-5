"""
Module: Database Seeding for Roles, Users, Teams, Milestones, and Notifications
------------------------------------------------------------------------------
This module seeds the database with initial data for roles, users, teams, milestones, tasks, and notifications.

Dependencies:
-------------
- SQLAlchemy ORM: For database operations.
- Flask-Security: For user authentication and role management.
- datetime: For handling time-related operations.
- random: For generating random strings.
- string: For character sets.
- SystemRandom: For secure random number generation.

Function:
---------
1. seed_database(db)
"""

from application.models import (
    Roles,
    Users,
    NotificationPreferences,
    Teams,
    Milestones,
    Tasks,
    Notifications,
    UserNotifications,
)
from flask_security import hash_password
from datetime import datetime, timedelta, timezone


def seed_database(db):
    """
    Function: Seed Database
    ------------------------
    Seeds the database with predefined roles, users, teams, milestones, tasks, and notifications. This function
    sets up an initial dataset for the application, providing the necessary structure and relationships for roles, users,
    teams, and milestones.

    Parameters:
    - db (SQLAlchemy object): The database session object used to interact with the database.

    Process:
    1. Creates and adds predefined roles (Instructor, TA, Student) to the database.
    2. Creates users (Instructor, TAs, and 12 students) and assigns roles to them.
    3. Sets up default notification preferences for students.
    4. Creates teams, linking them with users and assigning each team members (students), instructors, and TAs.
    5. Defines and adds milestones and tasks for the project, with specific deadlines and descriptions.
    6. Creates and associates notifications (Deadline, Feedback, Milestone Update) with students for each milestone.

    Behavior:
    - The function creates roles and users (instructor, TAs, and students) with the appropriate roles and notification preferences.
    - It creates four teams and assigns them to instructors and TAs, with team members being students.
    - Milestones and associated tasks are created, followed by notification creation for each student to keep track of deadlines, feedback, and updates.
    - All changes are committed to the database.

    Return:
    - None (Directly modifies the database).
    """

    # Create roles
    roles = {
        "instructor": Roles(name="Instructor", description="Course instructor role"),
        "ta": Roles(name="TA", description="Teaching assistant role"),
        "student": Roles(name="Student", description="Student role"),
    }
    github_username = ["areebafarooqui0001", "shrasinh", "Matrixmang0"]
    milestone_data = [
        {
            "title": "User Requirements and Stories Submission",
            "description": """
            Focus: Identify and document user requirements and write user stories.
            Deliverables:
            - Identify primary, secondary, and tertiary users of the application.
            - Write user stories following SMART guidelines.
            - Submit a PDF document containing user identifications and user stories.
        """,
            "deadline": datetime.now(timezone.utc) + timedelta(days=7),
            "task_description": "Submit User Requirements and Stories document.",
        },
        {
            "title": "Wireframes and Storyboard Submission",
            "description": """
            Focus: Design low-fidelity wireframes and create a storyboard.
            Deliverables:
            - A storyboard (PPT or video) embedded in the PDF submission.
            - Low-fidelity wireframes for user stories applying usability design guidelines.
            - Submit a PDF document containing the storyboard and wireframes.
        """,
            "deadline": datetime.now(timezone.utc) + timedelta(days=14),
            "task_description": "Submit Wireframes and Storyboard document.",
        },
        {
            "title": "Project Design and Scheduling Submission",
            "description": """
            Focus: Define project schedules, design system components, and implement basic UI pages.
            Deliverables:
            - Gantt chart and sprint schedule (tools like Trello or Jira can be used).
            - Basic class diagrams and system component descriptions.
            - Implementation of most UI pages (HTML/CSS/JavaScript or frameworks like Vue.js).
            - Submit a PDF document with schedules, designs, and details of UI implementation.
        """,
            "deadline": datetime.now(timezone.utc) + timedelta(days=21),
            "task_description": "Submit Project Design and Scheduling document.",
        },
        {
            "title": "API Documentation and Implementation Submission",
            "description": """
            Focus: Develop and document API endpoints.
            Deliverables:
            - YAML file listing APIs mapped to user stories and integrations.
            - Well-commented code for APIs with error handling, validation, and responses.
            - Submit a PDF document detailing the API endpoints, their usage, and the YAML file.
        """,
            "deadline": datetime.now(timezone.utc) + timedelta(days=28),
            "task_description": "Submit API Documentation and Implementation document.",
        },
        {
            "title": "Testing Suite Submission",
            "description": """
            Focus: Create and submit test cases for API endpoints and system functionality.
            Deliverables:
            - Test cases in the specified format (API, inputs, expected output, actual output, result).
            - Basic unit tests using pytest.
            - Submit a PDF document containing test cases and pytest output.
        """,
            "deadline": datetime.now(timezone.utc) + timedelta(days=35),
            "task_description": "Submit Testing Suite document.",
        },
        {
            "title": "Final Project Report and Submission",
            "description": """
            Focus: Finalize and submit the complete project along with the final report.
            Deliverables:
            - A detailed report summarizing all milestones (1-5).
            - Complete implementation of the system.
            - Instructions to run the application.
            - Recorded presentation and slides of the working prototype.
            - Submit a PDF document containing the final report, instructions, and presentation materials.
        """,
            "deadline": datetime.now(timezone.utc) + timedelta(days=42),
            "task_description": "Submit Final Project Report and Presentation document.",
        },
    ]
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
                github_username=github_username[i % 3],
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

    # Add milestones and tasks to the database
    for milestone_info in milestone_data:
        milestone = Milestones(
            title=milestone_info["title"],
            description=milestone_info["description"].strip(),
            deadline=milestone_info["deadline"],
            created_at=datetime.now(timezone.utc),
            created_by=users["instructor"].id,  # Replace with the actual instructor ID
        )
        db.session.add(milestone)

        task = Tasks(
            milestone=milestone,
            description=milestone_info["task_description"],
        )
        db.session.add(task)

    # Create notifications for each student
    for team in teams:
        for student in team.members:
            for milestone in milestone_data:
                # Deadline notification
                deadline_notification = Notifications(
                    title="Deadline Notification",
                    message=f"The milestone {milestone['title']} is due on {milestone['deadline'].strftime('%Y-%m-%d')}.",
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
                    message=f"You have received feedback on {milestone['title']}.",
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
                    message=f"The milestone {milestone['title']} has been updated.",
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
