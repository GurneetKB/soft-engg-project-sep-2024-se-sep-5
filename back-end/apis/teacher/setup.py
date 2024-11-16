from flask import Blueprint
from application.models import Teams, Milestones, db
from github import Github, Auth
from groq import Groq
import os


teacher = Blueprint("teacher", __name__, url_prefix="/teacher")

# GitHub configuration
github_auth = Auth.Token(os.environ.get("GITHUB_ACCESS_TOKEN"))
github_client = Github(auth=github_auth)

# AI configuration
ai_client = Groq(api_key=os.environ.get("AI_ACCESS_TOKEN"))


def get_teams_under_user(user):
    if user.has_role("Instructor"):
        teams = Teams.query.filter(Teams.instructor_id == user.id).all()
    else:
        teams = Teams.query.filter(Teams.ta_id == user.id).all()
    return teams


def get_single_team_under_user(user, team_id):
    if user.has_role("Instructor"):
        team = Teams.query.filter(
            Teams.instructor_id == user.id, Teams.id == team_id
        ).first()
    else:
        team = Teams.query.filter(Teams.ta_id == user.id, Teams.id == team_id).first()
    return team


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
                            "linesOfCodeAdded": 0,
                            "linesOfCodeDeleted": 0,
                        }

                    # Update milestone-specific stats
                    milestones_stats[milestone_id]["commits"] += 1
                    milestones_stats[milestone_id][
                        "linesOfCodeAdded"
                    ] += detailed_commit.stats.additions
                    milestones_stats[milestone_id][
                        "linesOfCodeDeleted"
                    ] += detailed_commit.stats.deletions

                except (IndexError, ValueError):
                    # Skip commits that don't follow the milestone format strictly
                    continue

        # Prepare final milestone list sorted by milestone ID
        milestones = sorted(milestones_stats.values(), key=lambda m: m["milestone_id"])
        return {
            "totalCommits": total_commits,
            "linesOfCodeAdded": lines_added,
            "linesOfCodeDeleted": lines_deleted,
            "milestones": milestones,
        }
    except Exception as e:
        return e.data


from . import milestone_management, team_management
