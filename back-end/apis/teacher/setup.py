from flask import Blueprint
from application.models import Teams, Milestones, db
from github import Github, Auth
from groq import Groq
import os

"""
Module: Teacher Blueprint Setup with GitHub and AI Integration
---------------------------------------------------------------
This module sets up the Flask Blueprint for teacher-related functionalities and includes helper functions 
for managing teams, fetching GitHub commit statistics, and integrating with AI tools.

Dependencies:
-------------
- Flask: For creating a Blueprint.
- SQLAlchemy ORM: For database operations.
- PyGithub: For interacting with the GitHub API.
- Groq: For AI tool integration.
- os: For environment variable access.

Blueprint:
----------
- Name: teacher
- URL Prefix: /teacher

Submodules:
-----------
1. milestone_management: Handles milestone-related functionalities.
2. team_management: Manages team-related operations.

Global Variables:
-----------------
1. `github_client`: Configured GitHub client using an access token.
2. `ai_client`: Configured AI client using an API key.

Functions:
----------
1. `get_teams_under_user(user)`
2. `get_single_team_under_user(user, team_id)`
3. `fetch_commit_details(repo_url, username=None)`
"""

teacher = Blueprint("teacher", __name__, url_prefix="/teacher")

# GitHub configuration
github_auth = Auth.Token(os.environ.get("GITHUB_ACCESS_TOKEN"))
github_client = Github(auth=github_auth)

# AI configuration
ai_client = Groq(api_key=os.environ.get("AI_ACCESS_TOKEN"))

"""
Function: Get Teams Under User
-------------------------------
Retrieves all teams managed by the given user. The user's role determines the scope of the query:
- If the user is an Instructor, fetches teams where the user is the assigned instructor.
- If the user is a Teaching Assistant (TA), fetches teams where the user is the assigned TA.

Parameters:
- user: The current user object.

Returns:
- List of `Teams` objects associated with the user.
"""


def get_teams_under_user(user):
    if user.has_role("Instructor"):
        teams = Teams.query.filter(Teams.instructor_id == user.id).all()
    else:
        teams = Teams.query.filter(Teams.ta_id == user.id).all()
    return teams


"""
Function: Get Single Team Under User
-------------------------------------
Fetches a specific team managed by the given user, based on the team ID. The user's role determines the scope:
- If the user is an Instructor, the team must belong to their assigned teams.
- If the user is a TA, the team must belong to their assigned teams.

Parameters:
- user: The current user object.
- team_id (int): The ID of the team to retrieve.

Returns:
- A `Teams` object representing the team if found.
- None if the team does not exist or is not managed by the user.
"""


def get_single_team_under_user(user, team_id):
    if user.has_role("Instructor"):
        team = Teams.query.filter(
            Teams.instructor_id == user.id, Teams.id == team_id
        ).first()
    else:
        team = Teams.query.filter(Teams.ta_id == user.id, Teams.id == team_id).first()
    return team


"""
Function: Fetch Commit Details from GitHub Repository
------------------------------------------------------
Analyzes commit statistics for a given GitHub repository. Optionally filters commits by a specific username. 
Also gathers milestone-specific statistics based on commit messages.

Parameters:
- repo_url (str): URL of the GitHub repository (HTTPS or SSH format).
- username (str, optional): GitHub username to filter commits by. Defaults to None (fetches all commits).

Returns:
- dict: A dictionary containing:
    - `total_commits` (int): Total number of commits in the repository.
    - `lines_of_code_added` (int): Total lines of code added across all commits.
    - `lines_of_code_deleted` (int): Total lines of code deleted across all commits.
    - `milestones` (list): List of dictionaries for each milestone, each containing:
        - `milestone_id` (int): Milestone ID from the commit message.
        - `name` (str): Milestone name.
        - `commits` (int): Number of commits related to the milestone.
        - `lines_of_code_added` (int): Lines of code added for the milestone.
        - `lines_of_code_deleted` (int): Lines of code deleted for the milestone.

Raises:
- ValueError: If the repository URL format is invalid.
- Exception: If any error occurs while interacting with the GitHub API.

Behavior:
- Parses the repository URL to extract owner and repo name.
- Fetches all commits or those by the specified user.
- Processes commit messages to identify milestone-related statistics.
- Summarizes and sorts milestone data.
"""


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

                    # Ignore the milestone whose IDs are not present in the database
                    if not milestone_name:
                        continue

                    # Initialize milestone stats if it doesn't exist
                    if milestone_id not in milestones_stats:
                        milestones_stats[milestone_id] = {
                            "milestone_id": milestone_id,
                            "name": milestone_name,
                            "commits": 0,
                            "lines_of_code_added": 0,
                            "lines_of_code_deleted": 0,
                        }

                    # Update milestone-specific stats
                    milestones_stats[milestone_id]["commits"] += 1
                    milestones_stats[milestone_id][
                        "lines_of_code_added"
                    ] += detailed_commit.stats.additions
                    milestones_stats[milestone_id][
                        "lines_of_code_deleted"
                    ] += detailed_commit.stats.deletions

                except (IndexError, ValueError):
                    # Skip commits that don't follow the milestone format strictly
                    continue

        # Prepare final milestone list sorted by milestone ID
        milestones = sorted(milestones_stats.values(), key=lambda m: m["milestone_id"])
        return {
            "total_commits": total_commits,
            "lines_of_code_added": lines_added,
            "lines_of_code_deleted": lines_deleted,
            "milestones": milestones,
        }
    except Exception as e:
        return e.data


from . import milestone_management, team_management
