from fastapi.testclient import TestClient
from fastapi import status

import app.routers.login as login_router
import app.services.login as login_service


def make_form(username: str, password: str):
    return {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }


def test_login_success(client: TestClient, monkeypatch):
    # Mock username/password checks and token creation
    monkeypatch.setattr(login_service, "verify_username", lambda u, c: True)
    monkeypatch.setattr(login_service, "verify_password", lambda p, h: True)
    monkeypatch.setattr(
        login_router,
        "create_access_token",
        lambda data, expires_delta: "fake-jwt-token",
    )

    resp = client.post("/login/", data=make_form("admin", "password"))

    # Assert
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["access_token"] == "fake-jwt-token"
    assert body["token_type"] == "bearer"


def test_login_invalid_username(client: TestClient, monkeypatch):
    # Mock username check fails
    monkeypatch.setattr(login_service, "verify_username", lambda u, c: False)
    # Mock verify password to True
    monkeypatch.setattr(login_service, "verify_password", lambda p, h: True)

    resp = client.post("/login/", data=make_form("baduser", "secret"))

    # Assert
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert resp.json()["detail"] == "Invalid username"


def test_login_invalid_password(client: TestClient, monkeypatch):
    # Mock verify usename to True 
    monkeypatch.setattr(login_service, "verify_username", lambda u, c: True)
    # Mock password check fails
    monkeypatch.setattr(login_service, "verify_password", lambda p, h: False)

    resp = client.post("/login/", data=make_form("admin", "wrongpass"))

    # Assert
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert resp.json()["detail"] == "Invalid password"
