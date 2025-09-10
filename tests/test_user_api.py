import pytest
from fastapi.testclient import TestClient

from main_app import app

client = TestClient(app)
# app.dependency_overrides[] = lambda: MockService()


@pytest.mark.parametrize(
    "id_",
    "username",
    "password",
    [
        (1111, "Alice", "asdf"),
        (33333, "Charlie", "sdfsdf"),
    ],
)
def test_create_user_success(id_, username, password):
    response = client.post(
        "/user", json={"id": id_, "username": username, "password": password}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == username
    assert data["id"] == id_


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"username": "aaa", "password": "asdf"},
        {"username": "aaa", "password": "asdf", "id": "askdjf"},
        {"username": "aaa", "password": "asdf", "id": -4},
    ],
)
def test_create_user_validation_errors(data):
    response = client.post("/user", data=data)
    assert response.status_code == 422


def test_create_user_duplicate():
    user = dict(id=1111, username="Andy", password="12345")
    response = client.post("/user", data=user)
    assert response.status_code == 201

    response = client.post("/user", data=user)
    assert response.status_code == 409
