"""
Module: Student Milestone Management APIs
------------------------------------------
This module provides APIs for managing milestones and tasks for students in a team-based project system.
It supports functionalities like retrieving milestone data, submitting milestone documents, and downloading submissions.

Dependencies:
- Flask, Flask-Security: For routing and authentication.
- SQLAlchemy ORM: For database operations.
- os, datetime: For file handling and date-time processing.

Roles Required:
- Student: All endpoints require the current user to have the "Student" role.

Endpoints:
----------
1. GET /student/milestone_management/overall
2. GET /student/milestone_management/individual
3. GET /student/milestone_management/individual/<int:milestone_id>
4. POST /student/milestone_management/individual/<int:milestone_id>
5. GET /student/milestone_management/individual/ai_analysis/<int:task_id>
6. GET /student/download_submission/<int:task_id>
7. POST /student/chat
"""

from apis.student.setup import student, get_team_id, ai_client
from flask_security import current_user, roles_required
from application.models import (
    Documents,
    Milestones,
    Submissions,
    Tasks,
    Teams,
    db,
)
from apis.teacher.setup import ai_client
from flask import abort, make_response, request, send_file, current_app
from datetime import datetime, timezone
import os
from PyPDF2 import PdfReader


"""
    API: Get Team Milestones Overview
    ----------------------------------
    Retrieves an overview of milestones for the current student's team, including task completion percentages.

    Role Required:
    - Student

    Response:
    - 200: JSON object with team name and milestone details (ID, title, completion percentage).
    - 400: If the student does not belong to a team.
    - 403: If the user does not have the required role.
    - 500: Internal server error.
"""


@student.route("/milestone_management/overall", methods=["GET"])
@roles_required("Student")
def get_team_milestones():

    # Get the team ID associated with the current student
    team_id = get_team_id(current_user)

    if not team_id:
        abort(400, "No team is assigned to you yet.")

    # Retrieve the team along with its milestones, tasks, and submissions
    team = db.session.query(Teams).filter(Teams.id == team_id).first()

    # Prepare milestone data
    team_milestone_for_user = []

    milestones = db.session.query(Milestones).all()

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
            .filter(Submissions.team_id == team_id)
            .filter(Tasks.milestone_id == milestone.id)
            .scalar()
        )

        team_milestone_for_user.append(
            {
                "milestone_id": milestone.id,
                "title": milestone.title,
                "completion_percentage": (
                    (submission_count / task_count) * 100 if task_count != 0 else 0
                ),
            }
        )

    # Prepare the response data
    response_data = {
        "team_name": team.name,
        "milestones": team_milestone_for_user,
    }

    return response_data, 200


"""
    API: Get All Milestones
    ------------------------
    Fetches a list of all available milestones with their IDs and titles.

    Role Required:
    - Student

    Response:
    - 200: JSON array of milestone objects (ID, title).
    - 403: If the user does not have the required role.
    - 500: Internal server error.
"""


@student.route("/milestone_management/individual", methods=["GET"])
@roles_required("Student")
def get_milestones():

    # Fetch all milestones for the student
    milestones = Milestones.query.all()
    milestone_list = [
        {
            "id": milestone.id,
            "title": milestone.title,
        }
        for milestone in milestones
    ]
    return {"milestones": milestone_list}, 200


"""
    API: Get Milestone Details
    ---------------------------
    Retrieves detailed information about a specific milestone for the student's team, including tasks and submission status.

    Role Required:
    - Student

    Path Parameters:
    - milestone_id: The ID of the milestone to fetch details for.

    Response:
    - 200: JSON object with milestone details (ID, title, description, tasks, etc.).
    - 404: If the milestone or team does not exist.
    - 403: If the user does not have the required role.
    - 500: Internal server error.
"""


@student.route("/milestone_management/individual/<int:milestone_id>", methods=["GET"])
@roles_required("Student")
def get_milestone_details(milestone_id):

    team_id = get_team_id(current_user)
    milestone = Milestones.query.get(milestone_id)
    team_submissions = db.session.query(Submissions).filter(
        Submissions.team_id == team_id
    )
    if milestone and team_id:
        # Prepare a dictionary with the milestone details
        milestone_data = {
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
            milestone_data["tasks"].append(
                {
                    "task_id": task.id,
                    "description": task.description,
                    "is_completed": True if task_submission else False,
                    "feedback": task_submission.feedback if task_submission else None,
                    "feedback_time": (
                        task_submission.feedback_time if task_submission else None
                    ),
                }
            )
        return milestone_data, 200
    else:
        return abort(404, "Milestone or team not found.")


"""
    API: Submit Milestone Documents
    --------------------------------
    Allows students to submit task documents for a specific milestone, validating the deadline and task association.

    Role Required:
    - Student

    Path Parameters:
    - milestone_id: The ID of the milestone for which the submission is being made.

    Request:
    - Form data with file attachments, where keys are task IDs and files are PDF documents.

    Response:
    - 201: JSON message confirming successful submission.
    - 400: If the milestone deadline has passed, task ID is invalid, or file is not a PDF.
    - 404: If the milestone or team does not exist.
    - 403: If the user does not have the required role.
    - 500: Internal server error.
"""


@student.route("/milestone_management/individual/<int:milestone_id>", methods=["POST"])
@roles_required("Student")
def submit_milestone(milestone_id):
    team_id = get_team_id(current_user)
    saved_files = []
    tasks = []
    # Fetch the milestone and team details
    milestone = Milestones.query.get(milestone_id)
    team = Teams.query.get(team_id)

    # Check if milestone and team exist
    if not milestone or not team:
        return abort(404, "Milestone or team not found")

    # Check if the milestone deadline has passed
    if milestone.deadline.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return abort(400, "Cannot submit after the milestone deadline")

    # Verify tasks under the milestone
    milestone_tasks = {str(task.id): task for task in milestone.task_milestones}

    # Prepare the directory for storing uploaded files
    file_dir = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        f"team_{team_id}",
        f"milestone_{milestone_id}",
    )
    os.makedirs(file_dir, exist_ok=True)

    try:
        # Check and process each file in the form data
        for key in request.files:
            task_id = key
            file = request.files.get(key)
            # Ensure task exists under the current milestone and the file is a PDF
            if task_id in milestone_tasks and file.filename.lower().endswith(".pdf"):
                # Generate document title
                document_title = (
                    f"Milestone{milestone_id}_Task{task_id}_Team{team.name}"
                )
                file_url = os.path.join(file_dir, document_title + ".pdf")

                # Check if a previous submission exists for this team and task
                existing_submission = Submissions.query.filter_by(
                    team_id=team_id, task_id=task_id
                ).first()

                if existing_submission:

                    # Update the existing submission
                    existing_submission.submission_time = datetime.now(timezone.utc)
                    existing_submission.feedback = None
                    existing_submission.feedback_by = None
                    existing_submission.feedback_time = None

                    # If there's an existing submission, delete the old file
                    old_document = Documents.query.filter_by(
                        submission_id=existing_submission.id
                    ).first()
                    if old_document and os.path.exists(old_document.file_url):
                        os.remove(old_document.file_url)

                    # Update the document
                    if old_document:
                        old_document.file_url = file_url
                    else:
                        # Create a new document if it doesn't exist
                        new_document = Documents(
                            title=document_title,
                            file_url=file_url,
                            submission=existing_submission,
                        )
                        db.session.add(new_document)

                else:
                    # Create a new submission
                    new_submission = Submissions(
                        task_id=task_id,
                        team_id=team_id,
                        submission_time=datetime.now(timezone.utc),
                    )
                    db.session.add(new_submission)

                    # Create a new document
                    new_document = Documents(
                        title=document_title,
                        file_url=file_url,
                        submission=new_submission,
                    )
                    db.session.add(new_document)

                # Save the new file
                file.save(file_url)
                saved_files.append(file_url)
                tasks.append(task_id)

            else:
                # Invalid task or file type, abort with 400
                for saved_file in saved_files:
                    if os.path.exists(saved_file):
                        os.remove(saved_file)
                return abort(
                    400,
                    f"Task {task_id} is not valid for this milestone or the file is not a PDF",
                )

        db.session.commit()

        current_app.logger.info(
            f"Documents for Milestone {milestone_id} added/updated by user {current_user.id} for team {team_id}"
        )

        return {"message": "Milestone documents submitted successfully"}, 201

    except Exception as e:
        # If any exception occurs during file saving or database operations
        # Delete all saved files
        for saved_file in saved_files:
            if os.path.exists(saved_file):
                os.remove(saved_file)

        current_app.logger.error(f"Error in submit_milestone: {str(e)}")
        return abort(500, "An unexpected error occurred. Try again later.")


"""
    API: Get AI Analysis
    ---------------------
    Uses AI to provide high-level recommendations or indicates alignment with the milestone and task requirements.

    Roles Accepted:
    - Student

    Path Parameters:
    - task_id (int): ID of the task.

    Response:
    - 200: JSON object containing the AI-generated analysis, including:
        - Content review
        - Task requirement checks.
    - 404: If the team, submission, or document is not found.
    - 500: If the document cannot be read or the AI analysis fails or Internal server error.
    - 403: If the user does not have the required role.
    - 400: If the milestone deadline has passed.
"""


@student.route(
    "/milestone_management/individual/ai_analysis/<int:task_id>",
    methods=["GET"],
)
@roles_required("Student")
def get_ai_analysis(task_id):

    team_id = get_team_id(current_user)
    submission = Submissions.query.filter_by(team_id=team_id, task_id=task_id).first()

    if not submission or not submission.documents:
        return abort(404, "Submission or document not found")

    if submission.task.milestone.deadline.replace(tzinfo=timezone.utc) < datetime.now(
        timezone.utc
    ):
        return abort(400, "Milestone Deadline Passed")

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
                    You are an AI expert specializing in analyzing the submitted documents and recommending the changes based on milestone and task description.

                    ### Instructions:
                    - Review the document and compare it against the provided milestone and task descriptions.
                    - Provide a response with a consistent header structure, regardless of the document's alignment.
                    - The response must always include two sections:
                    1. **Alignment Assessment**
                    2. **Recommendations**

                    ### Response Format:
                    #### Alignment Assessment
                    - State whether the document fully aligns with the milestone and task descriptions in short and concise way.

                    #### Recommendations
                    - If fully aligned: "No changes required."
                    - If discrepancies exist: Provide exactly three high-level recommendations.

                    ### Tasks:
                    1. Analyze the document thoroughly
                    2. Maintain the specified response structure
                    3. Provide clear, concise insights
                    """,
                },
                {
                    "role": "user",
                    "content": f"""
                    ### Inputs:  
                    1. **Submission Details**:   
                    - Content: {text}  
                    2. **Milestone Description**:  
                    {submission.task.milestone.description} 
                    3. **Task Description**:  
                    {submission.task.description} 
                    """,
                },
            ],
            model="llama-3.1-8b-instant",
        )

        response = chat_completion.choices[0].message.content
        return {"analysis": response}, 200

    except Exception as e:
        return abort(500, f"AI analysis error: {str(e)}")


"""
    API: Download Submission File
    ------------------------------
    Allows students to download the submitted document for a specific task under their team.

    Role Required:
    - Student

    Path Parameters:
    - task_id: The ID of the task for which the document is being downloaded.

    Response:
    - 200: File attachment response containing the PDF document.
    - 404: If the submission or document does not exist, or the file is not found on the server.
    - 403: If the user does not have the required role.
    - 500: Internal server error.
"""


@student.route("/download_submission/<int:task_id>", methods=["GET"])
@roles_required("Student")
def download_submission(task_id):

    team_id = get_team_id(current_user)
    submission = Submissions.query.filter(
        Submissions.task_id == task_id, Submissions.team_id == team_id
    ).first()

    if not submission or not submission.documents:
        return abort(404, "Submission or document not found")

    document = submission.documents

    # Check file existence
    if not os.path.exists(document.file_url):
        return abort(404, "File not found")

    file_response = make_response(send_file(document.file_url))
    file_response.headers["Content-Disposition"] = (
        f'attachment; filename="{document.title}.pdf"'
    )
    return file_response, 200


"""
    API: AI Chat Assistant for Milestones
    -------------------------------------
    Allows students to interact with an AI assistant to ask questions about their project milestones, tasks, and deadlines.

    Role Required:
    - Student

    Request Body:
    - message (string): The query or message from the student to the AI assistant.

    Functionality:
    - Retrieves milestone data, including tasks and deadlines, to provide operational guidance.
    - Generates responses based on predefined milestones using an AI chat model.

    Response:
    - 200: JSON response containing the AI assistant's analysis or answer.
    - 400: If the `message` field is missing or empty.
    - 403: If the user does not have the required role.
    - 500: Internal server error.
"""


@student.route("/chat", methods=["POST"])
@roles_required("Student")
def chat():
    data = request.json
    user_message = data.get("message")
    if not user_message:
        return abort(400, "User message can not be empty")
    milestones = db.session.query(Milestones).all()
    ai_prompt = []

    for milestone in milestones:
        milestone_ai_prompt = ""
        milestone_ai_prompt += f"\nMilestone: {milestone.title}\n"
        milestone_ai_prompt += f"\nMilestone Description: {milestone.description}\n"
        milestone_ai_prompt += (
            f"Deadline: {milestone.deadline.strftime('%Y-%m-%d %H:%M:%S')} GMT\n"
        )
        for task in milestone.task_milestones:
            milestone_ai_prompt += f"Task: {task.description}\n"

        ai_prompt.append(milestone_ai_prompt)

    try:
        chat_completion = ai_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    You are an AI assistant focused solely on helping students with operational aspects of their project milestones. Your knowledge is limited to the following milestone information: 
                    {ai_prompt}

                    Strictly adhere to these guidelines:
                    1. Only answer questions directly related to the milestones, their tasks, deadlines, or general project management.
                    2. If asked about anything outside the provided milestone details, state that you don't have that information.
                    3. Do not provide any information or assistance on technical implementation, coding, or subject matter expertise.
                    4. Be concise and direct in your responses, focusing on operational aspects only.

                    Remember, your purpose is to help students understand and manage their project milestones, not to assist with the actual project work or any other topics.
                    """,
                },
                {
                    "role": "user",
                    "content": str(user_message),
                },
            ],
            model="llama-3.1-8b-instant",
        )

        response = chat_completion.choices[0].message.content
        return {"analysis": response}, 200

    except Exception as e:
        return abort(500, str(e))
