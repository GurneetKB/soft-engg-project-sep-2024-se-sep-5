from application.setup import app, github_client
from flask_security import current_user, roles_accepted, roles_required
from application.models import Tasks, db, Submissions, Milestones, Teams, Documents
from flask import abort, request, send_file
from datetime import datetime, timezone
import os
import PyPDF2
from groq import Groq

milestone1 = {
    "deadline": "20th October 2024",
    "requirements": """
        MILESTONE:1
        Focus: Identify User Requirements
        Identify users of the application - primary, secondary and tertiary users.
        Write user stories for the requirements, based on the SMART guidelines discussed in the lectures  (You are not required to write user stories for existing functionalities; instead, you have to write them for the features and integrations you want to implement in the existing system)
        The user stories should be in the following format:
        As a [type of user],
        I want [an action],
        So that [a benefit/value]

        EVALUATION SEP’24

        EVALUATION QUESTIONS:

        1. Identify users (out of 5): All users identified - 5, Partially identified-3,     Absent - 0
        2. Write user stories (out of 15): Fully identified - 15, Partially identified (as per the SMART guidelines) - 10, Partially identified (but mostly not as per the SMART guidelines) - 5, Absent - 0 
        [Please check whether the user stories follow the SMART guidelines]
    """,
}

milestone2 = {
    "deadline": "20th October 2024",
    "requirements": """
        MILESTONE:2

        Focus: User Interfaces
        Create a storyboard for the application - it can be a ppt or even a video. Embed the ppt/video in the PDF submission of this week.
        Take each user story and create low-fidelity wireframes
        Apply usability design guidelines and heuristics discussed in lectures to come up with the wireframes.

        EVALUATION SEP’24

        1. Create a storyboard (out of 10): All criteria satisfied with drawing - 10, Some criteria satisfied - 5, Absent - 0

        2. Create low-fidelity wireframes for the identified user stories (out of 15): Fully available - 15, Mostly available - 10, A few available - 5, Absent - 0
    """,
}

milestone3 = {
    "deadline": "10th November 2024",
    "requirements": """
       MILESTONE:3

        Focus: Scheduling and Design
        Project Schedule - come up with a schedule of your overall project based on the user stories created in the previous milestones
        Create a schedule for your sprints and iterations, timings of your scrum meetings etc. Trello board, Gantt chart - specifying your tasks and contributions.
        Project Scheduling Tools - which tools are you using? E.g. Pivotal Tracker, Jira
        Design of Components - Describe different components of your system based on the user stories created in the previous milestones
        Software Design - Basic class diagrams of your proposed system
        Details/Minutes of a few scrum meetings
        Most of the pages in the UI (It may be modified (up to a certain limit) at a later time if necessary) - E.g.: HTML/CSS/Javascript (if you are using a framework like Vue.js or React.js, pages should be connected and redirection also implemented, have to submit the frontend folder without integration with backend API’s. Additionally provide a Readme file to run the frontend code).
        Milestone 3 PDF Report

        EVALUATION SEP’24


        1. Project Schedule (out of 7): Full Gantt diagram and description present - 7,Partially present - 4, Absent - 0

        2. Use of project scheduling tools (out of 5): Present - 5, Partially present - 3, Absent - 0

        3. Describe different components of your system (out of 8): Components are fully identified with description - 8, Partially present - 4, Absent - 0

        4. Basic class diagrams of your proposed system (out of 10): All classes with appropriate relationship - 10, Most classes with appropriate relationship - 7, A few classes with appropriate relationship - 5, A few classes with relationship which are not appropriate - 3, Absent - 0

        5. Details/Minutes of a few scrum meetings (out of 5): Fully present - 5, Partially present - 3, Absent - 0

        6. UI pages (out of 15): All important pages - 15, Most of the pages - 10, A few pages - 5, Absent - 0

        7. Overall milestone 1-3 (out of 5): Very impressive - 5, Impressive - 3, Poor - 0
    """,
}

milestone4 = {
    "deadline": "19th November 2024",
    "requirements": """
        MILESTONE:4

        Focus: API Endpoints
        For each user story, create new API endpoints or use appropriate API endpoints from libraries
        List of APIs integrated
        List of APIs created
        Description of API endpoints. (As per the problem statement)
        Submission of YAML (for the APIs created by dev-team)
        Code for the APIs (implementation)

        PEER EVALUATION QUESTIONS:

        1. API Creation and integration (out of 15):

        Provide a detailed description of the APIs in the YAML file, ensuring all API's are clearly listed.
        Explain how the developed API’s are linked with the user stories, specifying how each API helps to implement the different user stories provided in Milestone 1. If APIs (such as Github or GenAI API’s) have been integrated to create new ones, describe their usage in the next section.

        YAML contains all of the required API’s and they are mapped to all the user stories. Additionally , any integrated APIs from Github or GenAI (created by dev-team) are clearly listed - 15, YAML has some required APIs and some user stories are implemented, and integrated GitHub and GenAI Api’s listed- 8, YAML has some required API, but it is not formatted properly and the user stories not implemented, Github And GenAI API’s not listed - 3, Absent - 0


        2. Code for the APIs - Implementation (out of 20):

        Provide the complete code for the APIs that have been implemented.
        Ensure that the  code is well commented and with proper error handling, validation and responses. The implementation should match the YAML and User stories.
        Code for all APIs are present, well documented adheres the best practices (error handling, validation and responses), fully implements the user stories - 20, Code for all the APIs is according to YAML and user stories but best practices (error handling, validation and responses) not followed- 15, Code is incomplete, poorly formatted, lacks proper documentation, but according to User Stories - 10 Code is incomplete, poorly formatted, lacks proper documentation and failed to implement User Stories  - 5, Absent - 0
    """,
}

milestone5 = {
    "deadline": "27th November 2024",
    "requirements": """
        MILESTONE:5

        Focus: Test cases, test suite of the project
        For each API endpoint, design extensive test cases. Test cases should be in the following format:
                        [ API being tested,
                          Inputs,
                          Expected output,
                          Actual Output,
                          Result- Success/Fail ]

        EVALUATION QUESTIONS:

        Design and describe extensive test cases (out of 20):

        Test cases for APIs created.
        Test cases for other functionalities.

        Most of the important test cases with proper format - 20, Some of the important test

        cases with proper format - 15, Some of the important test cases (not formatted properly)- 10, Test cases are not correct - 5, Absent - 0


        Some basic unit tests using pytest (out of 5):

        pytest code/output present - 5, pytest code/output present, but error are not highlighted- 3, Absent - 0
    """,
}

milestone6 = {
    "deadline": "8th December 2024",
    "requirements": """
        MILESTONE:6

        Focus: Final Submission pdf
        Week-12 is completely focused on the project, and no new course content is released this week
        Complete implementation along with a working prototype.
        Final project report (consistent with intermediate milestone documents).
        Detailed report on work done from Milestone 1 through Milestone 5.
        Implementation details of your project
        1. Technologies and tools used
        2. And instructions to run your application.
        A section describing code review, issue reporting and tracking using screenshots.
        Recorded presentation and presentation slides of the working model of your system.

        EVALUATION QUESTIONS:


        1. Recorded presentation and presentation slides of the working model of your

        system (out of 5):

        Submitted - 5,

        Not submitted - 0


        2. Tool & Technology (Out of 15):

        All tools and technologies are presented - 15,

        Most of the tools and technologies are presented - 10,

        Some of the tools and technologies are presented- 5,

        Absent - 0


        3. Issue tracker (Out of 10):

        Issue trackers are present with regular updates- 10, Issue trackers are present with irregular updates - 5, Absent -0


        4. Instructions to run your application (Out of 5):

        Available in full details - 5, Some information available - 3, Absent - 0


        5. Overall milestone 4-6 (out of 5): Very impressive - 5, Impressive - 3, Poor - 0
    """,
}

milestone_req = {
    1: milestone1,
    2: milestone2,
    3: milestone3,
    4: milestone4,
    5: milestone5,
    6: milestone6,
}


def get_teams_under_user(user):
    if current_user.has_role("Instructor"):
        teams = Teams.query.filter(Teams.instructor_id == user.id).all()
    else:
        teams = Teams.query.filter(Teams.ta_id == user.id).all()
    return teams


def get_single_team_under_user(user, team_id):
    if current_user.has_role("Instructor"):
        team = Teams.query.filter(
            Teams.instructor_id == user.id, Teams.id == team_id
        ).first()
    else:
        team = Teams.query.filter(Teams.ta_id == user.id, Teams.id == team_id).first()
    return team


@app.route("/teacher/milestone_management", methods=["GET"])
@roles_accepted("Instructor", "TA")
def get_all_milestones():

    milestone_objects = Milestones.query.all()

    teams = get_teams_under_user(current_user)

    no_of_students = 0
    for team in teams:
        no_of_students += len(team.members)

    total_teams = len(teams)

    response_data = {
        "no_of_teams": total_teams,
        "no_of_students": no_of_students,
        "milestones": [],
    }

    for milestone in milestone_objects:
        tasks = milestone.task_milestones
        if not tasks:
            milestone.completion_rate = 0.0
            continue

        completed_teams = (
            db.session.query(Submissions.team_id)
            .join(Tasks, Tasks.id == Submissions.task_id)
            .filter(
                Tasks.milestone_id == milestone.id,
                Submissions.team_id.in_([team.id for team in teams]),
            )
            .group_by(Submissions.team_id)
            .having(db.func.count(db.distinct(Submissions.task_id)) == len(tasks))
            .count()
            or 0
        )

        response_data["milestones"].append(
            {
                "id": milestone.id,
                "title": milestone.title,
                "description": milestone.description,
                "deadline": milestone.deadline,
                "completion_rate": (
                    (completed_teams / total_teams) * 100 if total_teams != 0 else 0
                ),
            }
        )

    return response_data


@app.route("/teacher/milestone_management", methods=["POST"])
@roles_required("Instructor")
def create_milestone():
    data = request.get_json()

    # Extract fields
    title = data.get("title")
    description = data.get("description")
    deadline = data.get("deadline")
    tasks = data.get("tasks", [])

    # Basic validation checks
    errors = []
    if not title or not isinstance(title, str):
        errors.append("Title is required and must be a string.")
    if not description or not isinstance(description, str):
        errors.append("Description is required and must be a string.")
    if not deadline:
        errors.append("Deadline is required.")
    else:
        try:
            parsed_deadline = datetime.strptime(
                deadline, "%a, %d %b %Y %H:%M:%S %Z"
            ).replace(tzinfo=timezone.utc)
            if parsed_deadline <= datetime.now(timezone.utc):
                errors.append("Deadline must be set to a future date and time.")
        except ValueError:
            errors.append("Deadline must be a valid GMT format datetime.")

    # Validate tasks
    if not isinstance(tasks, list):
        errors.append("Tasks must be a list.")
    else:
        for i, task_data in enumerate(tasks, 1):
            if not isinstance(task_data, dict) or "description" not in task_data:
                errors.append(f"Task {i} must be an object with a 'description' field.")
            elif not isinstance(task_data["description"], str):
                errors.append(f"Description in Task {i} must be a string.")

    # If there are validation errors, return them
    if errors:
        return abort(400, errors)

    # Create milestone object
    milestone_object = Milestones(
        title=title,
        description=description,
        deadline=parsed_deadline,
        created_by=current_user.id,
        created_at=datetime.now(timezone.utc),
    )

    # Add milestone to session
    db.session.add(milestone_object)
    db.session.flush()  # Ensure milestone_object.id is available for tasks

    # Create tasks and associate with milestone
    for task_data in tasks:
        task_description = task_data["description"]
        task = Tasks(description=task_description, milestone_id=milestone_object.id)
        db.session.add(task)

    # Commit all changes
    db.session.commit()

    return {"message": "Milestone published successfully."}, 201


@app.route("/teacher/milestone_management/<int:milestone_id>", methods=["GET"])
@roles_required("Instructor")
def get_milestone(milestone_id):
    milestone_object = Milestones.query.filter_by(id=milestone_id).first()
    if not milestone_object:
        return abort(404, "Milestone not found.")

    milestone_data = {
        "title": milestone_object.title,
        "description": milestone_object.description,
        "deadline": milestone_object.deadline.strftime("%Y-%m-%dT%H:%M"),
        "tasks": [
            {"description": task.description}
            for task in milestone_object.task_milestones
        ],
    }

    return milestone_data


@app.route("/teacher/milestone_management/<int:milestone_id>", methods=["PUT"])
@roles_required("Instructor")
def update_milestone(milestone_id):
    # Fetch milestone
    milestone_object = Milestones.query.filter_by(id=milestone_id).first()
    if not milestone_object:
        return abort(404, "Milestone not found.")

    data = request.get_json()
    errors = []

    # Validate and update title
    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            errors.append("Title must be a non-empty string.")
        else:
            milestone_object.title = title

    # Validate and update description
    if "description" in data:
        description = data["description"]
        if not isinstance(description, str) or not description.strip():
            errors.append("Description must be a non-empty string.")
        else:
            milestone_object.description = description

    # Validate and update deadline
    if "deadline" in data:
        deadline = data["deadline"]
        try:
            # Parse the deadline and check if it is in the future
            parsed_deadline = datetime.strptime(
                deadline, "%a, %d %b %Y %H:%M:%S %Z"
            ).replace(tzinfo=timezone.utc)
            if parsed_deadline <= datetime.now(timezone.utc):
                errors.append("Deadline must be set to a future date and time.")
            else:
                milestone_object.deadline = parsed_deadline
        except ValueError:
            errors.append("Deadline must be a valid GMT format datetime.")

    # Validate tasks
    if "tasks" in data:
        tasks = data["tasks"]
        if not isinstance(tasks, list):
            errors.append("Tasks must be provided as a list.")
        else:
            # Remove existing tasks if tasks data is valid
            for task in milestone_object.task_milestones:
                db.session.delete(task)

            # Add new tasks with validation
            for i, task_data in enumerate(tasks, 1):
                task_description = task_data.get("description")
                if not isinstance(task_data, dict) or not task_description:
                    errors.append(
                        f"Task {i} must have a non-empty 'description' field."
                    )
                elif not isinstance(task_description, str):
                    errors.append(f"Description in Task {i} must be a string.")
                else:
                    new_task = Tasks(
                        description=task_description, milestone=milestone_object
                    )
                    db.session.add(new_task)

    # If validation errors exist, return them
    if errors:
        return abort(400, errors)

    # Commit changes
    db.session.commit()
    return {"message": "Milestone updated successfully."}, 201


@app.route("/teacher/milestone_management/<int:milestone_id>", methods=["DELETE"])
@roles_required("Instructor")
def delete_milestone(milestone_id):
    delete_object = Milestones.query.filter_by(id=milestone_id).first()
    if not delete_object:
        return abort(404, "Milestone not found.")

    db.session.delete(delete_object)
    db.session.commit()
    return {"message": "Milestone is deleted"}, 200


@app.route("/teacher/team_management/overall", methods=["GET"])
@roles_accepted("Instructor", "TA")
def get_overall_teams_progress():

    response_data = []
    milestones = db.session.query(Milestones).all()
    milestone_count = len(milestones)
    teams = get_teams_under_user(current_user)
    for team in teams:
        completion_rate = 0

        for milestone in milestones:
            # Get the number of tasks in the milestone
            task_count = (
                db.session.query(db.func.count(Tasks.id))
                .filter(Tasks.milestone_id == milestone.id)
                .scalar()
            )

            # Get the number of submissions associated with the milestone tasks
            submission_count = (
                db.session.query(db.func.count(Submissions.id))
                .join(Tasks, Submissions.task_id == Tasks.id)
                .filter(Submissions.team_id == team.id)
                .filter(Tasks.milestone_id == milestone.id)
                .scalar()
            )

            completion_rate += (
                (submission_count / (task_count * milestone_count))
                if task_count != 0
                else 0
            )

        # Prepare the response data
        response_data.append(
            {
                "name": team.name,
                "progress": round(completion_rate * 100),
            }
        )

    return response_data, 200


@app.route("/teacher/team_management/individual", methods=["GET"])
@roles_accepted("Instructor", "TA")
def get_teams():

    teams = get_teams_under_user(current_user)
    team_list = [
        {
            "id": team.id,
            "name": team.name,
        }
        for team in teams
    ]
    return {"teams": team_list}, 200


@app.route("/teacher/team_management/individual/detail/<int:team_id>", methods=["GET"])
@roles_accepted("Instructor", "TA")
def get_team_details(team_id):

    team = get_single_team_under_user(current_user, team_id)
    if not team:
        return abort(404, "Team not found")
    team = {
        "id": team.id,
        "name": team.name,
        "members": [
            {
                "id": member.id,
                "name": member.username,
                "email": member.email,
            }
            for member in team.members
        ],
        "github_repo_url": team.github_repo_url,
        "instructor": {"id": team.instructor.id, "username": team.instructor.username},
        "ta": {"id": team.ta.id, "username": team.ta.username},
    }
    return {"team": team}, 200


@app.route(
    "/teacher/team_management/individual/progress/<int:team_id>", methods=["GET"]
)
@roles_accepted("Instructor", "TA")
def get_team_progress(team_id):

    team = get_single_team_under_user(current_user, team_id)
    if not team:
        return abort(404, "Team not found")

    milestones = Milestones.query.all()
    team_submissions = db.session.query(Submissions).filter(
        Submissions.team_id == team_id
    )
    milestones_data = []

    for milestone in milestones:
        individual_milestone = {
            "id": milestone.id,
            "title": milestone.title,
            "description": milestone.description,
            "deadline": milestone.deadline.strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": milestone.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "tasks": [],
        }
        for task in milestone.task_milestones:
            task_submission = team_submissions.filter(
                Submissions.task_id == task.id
            ).first()
            individual_milestone["tasks"].append(
                {
                    "task_id": task.id,
                    "description": task.description,
                    "is_completed": True if task_submission else False,
                    "feedback": (task_submission.feedback if task_submission else None),
                    "feedback_time": (
                        task_submission.feedback_time if task_submission else None
                    ),
                }
            )

        milestones_data.append(individual_milestone)

    return milestones_data, 200


@app.route(
    "/teacher/team_management/individual/submission/<int:team_id>/<int:task_id>",
    methods=["GET"],
)
@roles_accepted("Instructor", "TA")
def view_submission(team_id, task_id):

    team = get_single_team_under_user(current_user, team_id)
    if not team:
        return abort(404, "Team not found")

    submission = Submissions.query.filter(
        Submissions.task_id == task_id, Submissions.team_id == team_id
    ).first()

    if not submission or not submission.documents:
        return abort(404, "Submission or document not found")

    document = submission.documents

    # Check file existence
    if not os.path.exists(document.file_url):
        return abort(404, "File not found")

    return send_file(document.file_url)


@app.route(
    "/teacher/team_management/individual/feedback/<int:team_id>/<int:task_id>",
    methods=["POST"],
)
@roles_accepted("Instructor", "TA")
def provide_feedback(team_id, task_id):

    team = get_single_team_under_user(current_user, team_id)
    if not team:
        return abort(404, "Team not found")

    data = request.get_json()
    if not data or "feedback" not in data:
        return abort(400, "Feedback data is required")

    feedback_content = data.get("feedback")
    if not isinstance(feedback_content, str) or not feedback_content.strip():
        return abort(400, "Feedback must be a non-empty string")

    # Find the relevant submission
    submission = Submissions.query.filter(
        Submissions.task_id == task_id, Submissions.team_id == team_id
    ).first()
    if not submission:
        return abort(404, "Submission not found")

    # Update feedback-related fields
    submission.feedback_by = current_user.id
    submission.feedback = feedback_content.strip()  # sanitize whitespace
    submission.feedback_time = datetime.now(timezone.utc)
    db.session.commit()
    return {"message": "The feedback is successfully provided."}, 201


@app.route(
    "/teacher/team_management/individual/github/<int:team_id>",
    methods=["POST"],
)
def get_github_details(team_id):
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        github_username = None
        team = get_single_team_under_user(current_user, team_id)

        if not team:
            return abort(404, "Team not found")

        if user_id:
            for member in team.members:
                if member.id == user_id:
                    github_username = member.github_username
            if not github_username:
                return abort(404, "Team member not found.")

        if not team.github_repo_url:
            return abort(404, "No GitHub repository URL found for this team")

        # Fetch commit details, passing in the username if provided
        commit_details = fetch_commit_details(team.github_repo_url, github_username)

        if "status" in commit_details:
            return abort(int(commit_details["status"]), commit_details["message"])

        return {
            "name": github_username or team.name,
            "githubRepoUrl": team.github_repo_url,
            "totalCommits": commit_details["totalCommits"],
            "linesOfCodeAdded": commit_details["linesOfCodeAdded"],
            "linesOfCodeDeleted": commit_details["linesOfCodeDeleted"],
            "milestones": commit_details["milestones"],
        }

    except ValueError as e:
        return abort(500, str(e))


def fetch_commit_details(repo_url, username=None):
    # Extract owner and repo name from the URL
    repo_url = repo_url.rstrip("/")  # Remove trailing slash if any
    if repo_url.startswith("https://"):
        parts = repo_url.split("/")
        owner = parts[-2]
        repo_name = parts[-1].replace(".git", "")
    elif repo_url.startswith("git@"):
        repo_part = repo_url.split(":")[1]
        owner, repo_name = repo_part.replace(".git", "").split("/")
    else:
        raise ValueError(f"Invalid GitHub URL format: {repo_url}")

    # Get all milestone names and IDs from the database
    milestone_names = {
        milestone.id: milestone.title
        for milestone in db.session.query(Milestones.id, Milestones.title).all()
    }

    # Get the repository
    try:
        repo = github_client.get_repo(f"{owner}/{repo_name}")

        # Initialize general statistics
        commits = repo.get_commits(author=username) if username else repo.get_commits()

        total_commits = 0
        lines_added = 0
        lines_deleted = 0
        milestones_stats = {}

        # Process each commit to collect milestone-related stats
        for commit in commits:
            total_commits += 1
            detailed_commit = repo.get_commit(commit.sha)
            commit_message = commit.commit.message

            # Update general stats
            lines_added += detailed_commit.stats.additions
            lines_deleted += detailed_commit.stats.deletions

            # Check for milestone in commit message in the format "Milestone-<id> <message>"
            if commit_message.lower().startswith("milestone-"):
                try:
                    # Extract milestone ID and fetch the corresponding name
                    milestone_id_str = commit_message.split()[0].split("-")[1]
                    milestone_id = int(milestone_id_str)

                    # Look up the milestone name in the dictionary
                    milestone_name = milestone_names.get(milestone_id)

                    # ignore the milestone whose ids are not present in the database
                    if not milestone_name:
                        continue

                    # Initialize milestone stats if it doesn't exist
                    if milestone_name not in milestones_stats:
                        milestones_stats[milestone_name] = {
                            "name": milestone_name,
                            "commits": 0,
                            "linesOfCodeAdded": 0,
                            "linesOfCodeDeleted": 0,
                        }

                    # Update milestone-specific stats
                    milestones_stats[milestone_name]["commits"] += 1
                    milestones_stats[milestone_name][
                        "linesOfCodeAdded"
                    ] += detailed_commit.stats.additions
                    milestones_stats[milestone_name][
                        "linesOfCodeDeleted"
                    ] += detailed_commit.stats.deletions

                except (IndexError, ValueError):
                    # Skip commits that don't follow the milestone format strictly
                    continue

        # Prepare final milestone list sorted by milestone ID
        milestones = list(milestones_stats.values())

        return {
            "totalCommits": total_commits,
            "linesOfCodeAdded": lines_added,
            "linesOfCodeDeleted": lines_deleted,
            "milestones": milestones,
        }
    except Exception as e:
        return e.data


@app.route(
    "/teacher/team_management/individual/ai_analysis/<int:team_id>/<int:milestone_id>",
    methods=["GET"],
)
def get_ai_analysis(team_id, milestone_id):
    team = get_single_team_under_user(current_user, team_id)
    if not team:
        return abort(404, "Team not found")

    submission = Submissions.query.filter_by(
        team_id=team_id, task_id=milestone_id
    ).first()

    if not submission:
        return abort(
            404, "Document not found. Please submit the report for AI analysis."
        )

    document = Documents.query.filter_by(submission_id=submission.id).first()

    try:
        with open(document.file_url, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            scraped_content = "".join(page.extract_text() for page in pdf_reader.pages)
    except Exception as e:
        return abort(500, f"Error reading document: {str(e)}")

    if milestone_id not in milestone_req:
        return abort(400, "Invalid milestone ID.")

    try:
        client = Groq(api_key=os.environ.get("AI_ACCESS_TOKEN"))

        prompt_template = """
        You are an AI expert specializing in analyzing document submissions for quality and clarity.  

        ### Inputs:  
        1. **Submission Details**:   
        - Content: {content}  

        2. **Milestone Requirements**:  
           {requirements} 

        3. **Milestone Deadline**:  
        - {deadline}

        4. **Report Submission Time**:  
        - {submission_time}
        ---

        ### Tasks:  

        1. **Content Review**:  
        - Analyze the grammar, structure, and clarity of the submission.  
        - Identify areas where the submission does not meet professional or academic standards.  
        - Suggest specific improvements for each issue.  

        2. **Milestone Requirements Check**:  
        - Cross-verify the content against the listed milestone requirements.  
        - Indicate which requirements are met and which are missing or incomplete.  

        3. **Deadline Comparison**:  
        - Calculate how far ahead or behind the team is in meeting the milestone deadline based on the report submission time.  
        - Provide the difference in days.  
        """

        prompt = prompt_template.format(
            content=scraped_content,
            requirements=milestone_req[milestone_id]["requirements"],
            deadline=milestone_req[milestone_id]["deadline"],
            submission_time=submission.submission_time,
        )

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )

        response = chat_completion.choices[0].message.content
        return {"analysis": response}, 200

    except Exception as e:
        return abort(500, f"AI analysis error: {str(e)}")
