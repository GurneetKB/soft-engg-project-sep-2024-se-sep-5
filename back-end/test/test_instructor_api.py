import pytest
from datetime import datetime, timezone
from application.setup import create_app
from application.models import *
from flask_security import Security
from flask import Flask
import random

@pytest.fixture
def app() -> Flask:
    # Set up the app with test-specific configurations
    app = create_app(database_uri="sqlite:///:memory:")  # Use in-memory SQLite database for tests
    app.config['TESTING'] = True  # Enable testing mode
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking (optional)
    return app

@pytest.fixture
def clear_db(app):
    # Clear the database before each test
    with app.app_context():
        db.drop_all()  # Drop all tables to clear previous data
        db.create_all()  # Recreate tables
    return db

@pytest.fixture
def client(app, clear_db):
    return app.test_client()

@pytest.fixture
def instructor_token(client):
    # Attempt to login and print the response for debugging
    response = client.post(
        "/login?include_auth_token",
        json={"username": "profsmith", "password": "password123"},
    )
    print(response.data) 
    assert response.status_code == 200, f"Login failed with status code {response.status_code}: {response.data}"
    return response.json["response"]["user"]["authentication_token"]



def test_get_overall_teams_progress(client, instructor_token):
    # Prepare any mock data for teams, milestones, tasks, etc.
    # For example, insert some teams and milestones into the database.
    milestone1 = Milestones(
        title="Milestone 1",
        description="This is the first milestone",  # Provide a valid description
        deadline=datetime(2024, 12, 1, tzinfo=timezone.utc)
    )
    milestone2 = Milestones(
        title="Milestone 2",
        description="This is the second milestone",  # Provide a valid description
        deadline=datetime(2024, 12, 15, tzinfo=timezone.utc)
    )
    db.session.add_all([milestone1, milestone2])
    db.session.commit()

    # Create unique teams for testing
    team = create_mock_team()  # Create a unique mock team

    # Send a GET request to the /teacher/team_management/overall API
    response = client.get(
        "/teacher/team_management/overall",
        headers={"Authentication-Token": instructor_token}
    )
    
    # Check if the response status is OK
    assert response.status_code == 200, "Failed to fetch overall team progress"

    # Check if the response contains expected fields (e.g., 'team_name', 'progress', etc.)
    teams_data = response.json
    assert isinstance(teams_data, list), "Response should be a list of teams"

    for team_data in teams_data:
        assert "team_name" in team_data, "Team name is missing in the response"
        assert "progress" in team_data, "Progress is missing in the response"
        assert isinstance(team_data["progress"], int), "Progress should be an integer"


# Mocked function to create a team with a unique name
def create_mock_team():
    # Generate a random team name to ensure uniqueness
    team_name = f"Team Alpha {random.randint(1000, 9999)}"
    team = Teams(
        name=team_name,
        github_repo_url="https://github.com/example/repo",
        # other fields like instructor_id, ta_id, etc.
    )
    db.session.add(team)
    db.session.commit()
    return team
