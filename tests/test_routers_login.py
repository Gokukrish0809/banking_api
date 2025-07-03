import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

# Import the login router and its dependencies
import routers.login
from routers.login import router
from config import HASH_PASSWORD

# Create FastAPI app and include the login router
app = FastAPI()
app.include_router(router, prefix="/login")

@pytest.fixture(autouse=True)
def client():
    return TestClient(app)

# Helper: default form data
def form_data(username, password):
    return {"username": username, "password": password}

# Test successful login returns access token and bearer type
def test_login_success(monkeypatch, client):
    # Patch module constants and dependencies
    monkeypatch.setattr(routers.login, 'USERNAME', 'admin')
    monkeypatch.setattr(routers.login, 'HASH_PASSWORD', HASH_PASSWORD)
    monkeypatch.setattr(routers.login, 'verify_password', lambda pw, hp: True)
    monkeypatch.setattr(routers.login, 'create_access_token', lambda data, expires_delta: 'token123')

    response = client.post(
        "/login/",
        data=form_data('admin', 'password')
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data == {"access_token": "token123", "token_type": "bearer"}

# Test invalid username yields 404
def test_login_invalid_username(client):
    response = client.post(
        "/login/",
        data=form_data('wronguser', 'password')
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid username"

# Test invalid password yields 404
def test_login_invalid_password(monkeypatch, client):
    monkeypatch.setattr(routers.login, 'USERNAME', 'admin')
    monkeypatch.setattr(routers.login, 'HASH_PASSWORD', 'hashedpass')
    monkeypatch.setattr(routers.login, 'verify_password', lambda pw, hp: False)

    response = client.post(
        "/login/",
        data=form_data('admin', 'badpass')
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid password"

# Test missing form data returns 422
def test_login_missing_form(client):
    response = client.post("/login/", data={})
    assert response.status_code == 422
