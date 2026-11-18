import os

# must be set before the app is imported
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    if os.path.exists("test.db"):
        os.remove("test.db")
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={"username": "habiba", "password": "secret123"})
    res = client.post("/auth/login", data={"username": "habiba", "password": "secret123"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}
