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
    Documents,
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


class TeamAnalysis(BaseModel):
    team_name: str
    rank: int
    status: str
    reason: str


class AIResponse(BaseModel):
    teams: List[TeamAnalysis]


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
            team_ai_prompt += f"Total Commits: {github_stats['totalCommits']}\n"
            team_ai_prompt += f"Lines Added: {github_stats['linesOfCodeAdded']}\n"
            team_ai_prompt += f"Lines Deleted: {github_stats['linesOfCodeDeleted']}\n"

            for milestone_stat in github_stats["milestones"]:
                team_ai_prompt += f"Milestone: {milestone_stat['name']}\n"
                team_ai_prompt += f"Commits: {milestone_stat['commits']}\n"
                team_ai_prompt += (
                    f"    Lines Added: {milestone_stat['linesOfCodeAdded']}\n"
                )
                team_ai_prompt += (
                    f"    Lines Deleted: {milestone_stat['linesOfCodeDeleted']}\n"
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

    return send_file(document.file_url)


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


@teacher.route(
    "/team_management/individual/github/<int:team_id>",
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


@teacher.route(
    "/team_management/individual/ai_analysis/<int:team_id>/<int:task_id>",
    methods=["GET"],
)
def get_ai_analysis(team_id, task_id):
    team = get_single_team_under_user(current_user, team_id)
    if not team:
        return abort(404, "Team not found")

    submission = Submissions.query.filter_by(team_id=team_id, task_id=task_id).first()

    if not submission:
        return abort(404, "Document not found.")

    document = Documents.query.filter_by(submission_id=submission.id).first()

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
        prompt_template = """
        You are an AI expert specializing in analyzing document submissions for quality and clarity.  

        ### Inputs:  
        1. **Submission Details**:   
        - Content: {content}  
        2. **Milestone Description**:  
           {milestone_description} 
        3. **Task Description**:  
           {task_description} 
        ---

        ### Tasks:  

        1. **Content Review**:  
        - Analyze the grammar, structure, and clarity of the submission.  
        - Identify areas where the submission does not meet professional or academic standards.  
        - Suggest specific improvements for each issue.  

        2. **Task Requirements Check**:  
        - Cross-verify the content against the listed task which is the part of the milestone.  
        - Indicate which requirements are met and which are missing or incomplete.   
        """

        prompt = prompt_template.format(
            content=text,
            milestone_description=submission.task.description,
            task_description=submission.task.milestone.description,
        )

        chat_completion = ai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )

        response = chat_completion.choices[0].message.content
        return {"analysis": response}, 200

    except Exception as e:
        return abort(500, f"AI analysis error: {str(e)}")
