import pytest
from application.setup import create_app
from application.models import db


@pytest.fixture(scope="module")
def client():
    app = create_app("sqlite:///testing.sqlite3", testing=True)
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


@pytest.fixture
def ta_token(client):
    response = client.post(
        "/login?include_auth_token",
        json={"username": "tajones", "password": "password123"},
    )
    assert (
        response.status_code == 200
    ), f"Login failed with status code {response.status_code}: {response.data}"
    return response.json["response"]["user"]["authentication_token"]


@pytest.fixture
def student_token(client):
    response = client.post(
        "/login?include_auth_token",
        json={"username": "student1", "password": "password123"},
    )
    assert (
        response.status_code == 200
    ), f"Login failed with status code {response.status_code}: {response.data}"
    return response.json["response"]["user"]["authentication_token"]


@pytest.fixture
def instructor_token(client):
    response = client.post(
        "/login?include_auth_token",
        json={"username": "profsmith", "password": "password123"},
    )
    assert (
        response.status_code == 200
    ), f"Login failed with status code {response.status_code}: {response.data}"
    return response.json["response"]["user"]["authentication_token"]
