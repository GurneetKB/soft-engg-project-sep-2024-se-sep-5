from apis.teacher.setup import (
    teacher,
    get_teams_under_user,
    get_single_team_under_user,
    fetch_commit_details,
    ai_client,
)
from flask_security import current_user, roles_accepted
from application.models import (
    Tasks,
    db,
    Submissions,
    Milestones,
    AIProgressText,
)
from flask import abort, request, send_file
from datetime import datetime, timezone
import os
from PyPDF2 import PdfReader
from typing import List
from pydantic import BaseModel
import json
from datetime import datetime

"""
Module: Teacher Team Management and Analysis APIs
--------------------------------------------------
This module provides APIs for instructors and teaching assistants to manage team-related operations. It includes 
functionality to fetch team progress, view submissions, provide feedback, analyze submissions using AI, 
and retrieve GitHub commit details.

Dependencies:
-------------
- Flask: For creating API routes and handling requests.
- Flask-Security: For role-based access control.
- SQLAlchemy ORM: For database operations.
- PyPDF2: For extracting text from PDF submissions.
- Pydantic: For defining and validating data models.
- PyGithub: For interacting with the GitHub API.
- Groq: For AI tool integration.
- os, datetime, typing: For general utilities.

Roles Accepted:
---------------
- Instructor: Full access to all endpoints.
- TA (Teaching Assistant): Access to specific endpoints for monitoring and analysis.

Endpoints:
----------
1. GET /team_management/overall
2. GET /team_management/individual
3. GET /team_management/individual/detail/<int:team_id>
4. GET /team_management/individual/progress/<int:team_id>
5. GET /team_management/individual/submission/<int:team_id>/<int:task_id>
6. POST /team_management/individual/feedback/<int:team_id>/<int:task_id>
7. GET /team_management/individual/github/<int:team_id>
8. GET /team_management/individual/ai_analysis/<int:team_id>/<int:task_id>
"""


class TeamAnalysis(BaseModel):
    team_name: str
    rank: int
    status: str
    reason: str


class AIResponse(BaseModel):
    teams: List[TeamAnalysis]


"""
API: Get Overall Team Progress
-------------------------------
Analyzes and retrieves the progress of all teams under the current user. Progress is calculated based on 
milestones, tasks, and GitHub activity.

Roles Accepted:
- Instructor
- TA

Response:
- 200: JSON array of team progress, including:
    - Team name
    - Progress percentage
    - AI-generated analysis including ranks, statuses, and reasons for progress.

Behavior:
- Uses AI to generate a detailed ranking and analysis based on task completion, GitHub activity, and feedback.
- Stores the AI-generated analysis in the database.
"""
@teacher.route("/team_management/overall", methods=["GET"])
@roles_accepted("Instructor", "TA")
def get_overall_teams_progress():
    response_data = []
    milestones = db.session.query(Milestones).all()
    milestone_count = len(milestones)
    teams = get_teams_under_user(current_user)
    ai_prompt = []

    for team in teams:
        completion_rate = 0
        team_data = {
            "team_name": team.name,
            "progress": 0,
        }
        team_ai_prompt = f"Team: {team.name}\n"

        for milestone in milestones:
            tasks = (
                db.session.query(Tasks).filter(Tasks.milestone_id == milestone.id).all()
            )
            task_count = len(tasks)
            submissions = (
                db.session.query(Submissions)
                .join(Tasks, Submissions.task_id == Tasks.id)
                .filter(Submissions.team_id == team.id)
                .filter(Tasks.milestone_id == milestone.id)
                .all()
            )
            submission_count = len(submissions)

            milestone_completion = (
                submission_count / task_count if task_count > 0 else 0
            )
            completion_rate += milestone_completion / milestone_count

            team_ai_prompt += f"\nMilestone: {milestone.title}\n"
            team_ai_prompt += f"Deadline: {milestone.deadline.strftime('%Y-%m-%d')}\n"
            team_ai_prompt += f"Tasks completed: {submission_count}/{task_count}\n"

            for task in tasks:
                submission = next(
                    (s for s in submissions if s.task_id == task.id), None
                )
                team_ai_prompt += f"Task: {task.description}\n"
                team_ai_prompt += f"Submitted: {'Yes' if submission else 'No'}\n"
                if submission:
                    team_ai_prompt += f"Submission time: {submission.submission_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    if submission.feedback:
                        team_ai_prompt += f"Feedback: {submission.feedback}\n"

        team_data["progress"] = round(completion_rate * 100)

        if team.github_repo_url:
            github_stats = fetch_commit_details(team.github_repo_url)
            team_ai_prompt += f"\nGitHub Stats:\n"
            team_ai_prompt += f"Total Commits: {github_stats['total_commits']}\n"
            team_ai_prompt += f"Lines Added: {github_stats['lines_of_code_added']}\n"
            team_ai_prompt += (
                f"Lines Deleted: {github_stats['lines_of_code_deleted']}\n"
            )

            for milestone_stat in github_stats["milestones"]:
                team_ai_prompt += f"Milestone: {milestone_stat['name']}\n"
                team_ai_prompt += f"Commits: {milestone_stat['commits']}\n"
                team_ai_prompt += (
                    f"    Lines Added: {milestone_stat['lines_of_code_added']}\n"
                )
                team_ai_prompt += (
                    f"    Lines Deleted: {milestone_stat['lines_of_code_deleted']}\n"
                )

        team_ai_prompt += f"\nOverall Progress: {team_data['progress']}%\n"
        ai_prompt.append(team_ai_prompt)
        response_data.append(team_data)

    try:
        chat_completion = ai_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""Analyze the progress of each team and provide a JSON response using the following schema:
                            {json.dumps(AIResponse.model_json_schema(), indent=2)}
                            
                            Ranking Rules:
                            1. Consider multiple factors for ranking in this priority order:
                               - Progress percentage (higher is better)
                               - Task completion relative to deadlines
                               - GitHub activity (commit frequency and code changes)
                               - Quality of submissions (based on feedback)
                            
                            2. Status Assignment Rules:
                               - 'on_track': Teams that have completed tasks on time and show consistent progress
                               - 'at_risk': Teams showing some progress but falling behind schedule
                               - 'off_track': Teams with minimal progress or significant delays
                            
                            3. Rank Assignment Rules:
                               - The ranks should be assigned from 1 to {len(teams)} consecutively
                               - No teams should have same ranks assigned
                               - Lower rank (closer to 1) indicates better performance
                               - Teams with same status should be ranked based on their relative progress
                               - Generally, 'on_track' teams should rank better than 'at_risk' teams
                               - 'at_risk' teams should rank better than 'off_track' teams
                            
                            4. Reason Format:
                               - Start with the primary factor affecting the ranking
                               - Include both positive and areas of concern
                               - Mention specific metrics (progress %, commit counts, etc.)
                               - Keep it concise but informative (2-3 sentences)
                            
                            Important: Ensure the ranking is consistent with the actual progress metrics and status assignments. Significant rank differences should be justified by clear metric differences.""",
                },
                {
                    "role": "user",
                    "content": str(ai_prompt),
                },
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
        )

        ai_response = AIResponse.model_validate_json(
            chat_completion.choices[0].message.content
        )
    except Exception as e:
        return abort(500, str(e))

    for team_analysis in ai_response.teams:
        for team in response_data:
            if team["team_name"] == team_analysis.team_name:
                team.update(
                    {
                        "rank": team_analysis.rank,
                        "status": team_analysis.status,
                        "reason": team_analysis.reason,
                    }
                )
                break

    ai_progress_entry = AIProgressText(
        generated_by=current_user.id,
        text=json.dumps(ai_response.dict(), indent=2),
    )
    db.session.add(ai_progress_entry)
    db.session.commit()

    return response_data, 200


"""
API: Get All Teams
-------------------
Fetches a list of all teams managed by the current user.

Roles Accepted:
- Instructor
- TA

Response:
- 200: JSON array of teams, each with:
    - ID
    - Name
"""
@teacher.route("/team_management/individual", methods=["GET"])
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


"""
API: Get Team Details
----------------------
Retrieves detailed information about a specific team, including team members, GitHub repository, and assigned roles.

Roles Accepted:
- Instructor
- TA

Path Parameters:
- team_id (int): ID of the team to fetch details for.

Response:
- 200: JSON object containing:
    - Team ID
    - Team name
    - Members with their details
    - GitHub repository URL
    - Instructor and TA details.
- 404: If the team is not found.
"""
@teacher.route("/team_management/individual/detail/<int:team_id>", methods=["GET"])
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
                "github_username": member.github_username,
            }
            for member in team.members
        ],
        "github_repo_url": team.github_repo_url,
        "instructor": {"id": team.instructor.id, "name": team.instructor.username},
        "ta": {"id": team.ta.id, "name": team.ta.username},
    }
    return {"team": team}, 200


"""
API: Get Team Progress
-----------------------
Retrieves milestone-wise progress for a specific team, including task-level details.

Roles Accepted:
- Instructor
- TA

Path Parameters:
- team_id (int): ID of the team to fetch progress for.

Response:
- 200: JSON array of milestones, each with:
    - ID
    - Title
    - Description
    - Deadline
    - List of tasks, each with:
        - Task ID
        - Description
        - Completion status
        - Submission time
        - Feedback and feedback time.
- 404: If the team is not found.
"""
@teacher.route("/team_management/individual/progress/<int:team_id>", methods=["GET"])
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
            "deadline": milestone.deadline,
            "created_at": milestone.created_at,
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
                    "submission_time": (
                        task_submission.submission_time if task_submission else None
                    ),
                    "feedback": (task_submission.feedback if task_submission else None),
                    "feedback_time": (
                        task_submission.feedback_time if task_submission else None
                    ),
                }
            )

        milestones_data.append(individual_milestone)

    return milestones_data, 200


"""
API: View Submission
---------------------
Retrieves the submission file for a specific task by a specific team.

Roles Accepted:
- Instructor
- TA

Path Parameters:
- team_id (int): ID of the team.
- task_id (int): ID of the task.

Response:
- 200: File download of the submission.
- 404: If the team, submission, or document is not found.
"""
@teacher.route(
    "/team_management/individual/submission/<int:team_id>/<int:task_id>",
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

    return send_file(document.file_url), 200


"""
API: Provide Feedback
----------------------
Allows the instructor or TA to provide feedback on a specific submission.

Roles Accepted:
- Instructor
- TA

Path Parameters:
- team_id (int): ID of the team.
- task_id (int): ID of the task.

Request:
- JSON object with:
    - feedback (string): The feedback content.

Response:
- 201: Confirmation message of successful feedback submission.
- 400: If feedback data is missing or invalid.
- 404: If the team or submission is not found.
"""
@teacher.route(
    "/team_management/individual/feedback/<int:team_id>/<int:task_id>",
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


"""
API: Get GitHub Details
------------------------
Fetches GitHub activity details for a team's repository, including commit statistics and milestone-specific details.

Roles Accepted:
- Instructor
- TA

Path Parameters:
- team_id (int): ID of the team.

Query Parameters:
- user_id (int, optional): ID of a specific team member to filter GitHub activity.

Response:
- 200: JSON object containing:
    - Repository details
    - Total commits
    - Lines of code added/deleted
    - Milestone-specific GitHub stats.
- 404: If the team, GitHub repository, or team member is not found.
"""
@teacher.route(
    "/team_management/individual/github/<int:team_id>",
    methods=["GET"],
)
def get_github_details(team_id):
    try:
        user_id = request.args.get("user_id")

        if user_id:
            try:
                user_id = int(user_id)
            except ValueError:
                return abort(400, "User id must be integer.")

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
            return abort(502, commit_details["message"])

        return {
            "name": github_username or team.name,
            "github_repo_url": team.github_repo_url,
            "total_commits": commit_details["total_commits"],
            "lines_of_code_added": commit_details["lines_of_code_added"],
            "lines_of_code_deleted": commit_details["lines_of_code_deleted"],
            "milestones": commit_details["milestones"],
        }, 200

    except ValueError as e:
        return abort(500, str(e))


"""
API: Get AI Analysis
---------------------
Uses AI to analyze the quality and completeness of a team's submission for a specific task.

Roles Accepted:
- Instructor
- TA

Path Parameters:
- team_id (int): ID of the team.
- task_id (int): ID of the task.

Response:
- 200: JSON object containing the AI-generated analysis, including:
    - Content review
    - Task requirement checks.
- 404: If the team, submission, or document is not found.
- 500: If the document cannot be read or the AI analysis fails.
"""
@teacher.route(
    "/team_management/individual/ai_analysis/<int:team_id>/<int:task_id>",
    methods=["GET"],
)
def get_ai_analysis(team_id, task_id):
    team = get_single_team_under_user(current_user, team_id)
    if not team:
        return abort(404, "Team not found")

    submission = Submissions.query.filter_by(team_id=team_id, task_id=task_id).first()

    if not submission or not submission.documents:
        return abort(404, "Submission or document not found")

    document = submission.documents

    # Check file existence
    if not os.path.exists(document.file_url):
        return abort(404, "File not found")

    try:
        with open(document.file_url, "rb") as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + " "
            text = text.replace("\n", " ")
    except Exception as e:
        return abort(500, f"Error reading document: {str(e)}")

    try:
        chat_completion = ai_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """
        You are an AI expert specializing in analyzing document submissions for quality and clarity.  

        ### Tasks:  

        1. **Content Review**:  
        - Analyze the grammar, structure, and clarity of the submission.  
        - Identify areas where the submission does not meet professional or academic standards.  
        - Suggest specific improvements for each issue.  

        2. **Task Requirements Check**:  
        - Cross-verify the content against the listed task which is the part of the milestone.  
        - Indicate which requirements are met and which are missing or incomplete.   
        """,
                },
                {
                    "role": "user",
                    "content": f"""
        ### Inputs:  
        1. **Submission Details**:   
        - Content: {text}  
        2. **Milestone Description**:  
           {submission.task.description} 
        3. **Task Description**:  
           {submission.task.milestone.description} 
        """,
                },
            ],
            model="llama-3.1-8b-instant",
        )

        response = chat_completion.choices[0].message.content
        return {"analysis": response}, 200

    except Exception as e:
        return abort(500, f"AI analysis error: {str(e)}")
