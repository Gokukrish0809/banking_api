from fastapi.testclient import TestClient

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
    # Arrange: stub out username/password checks and token creation
    monkeypatch.setattr(login_service, "verify_username", lambda u, c: True)
    monkeypatch.setattr(login_service, "verify_password", lambda p, h: True)
    monkeypatch.setattr(
        login_router,
        "create_access_token",
        lambda data, expires_delta: "fake-jwt-token",
    )

    # Act
    resp = client.post("/login/", data=make_form("admin", "password"))

    # Assert
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] == "fake-jwt-token"
    assert body["token_type"] == "bearer"


def test_login_invalid_username(client: TestClient, monkeypatch):
    # Arrange: username check fails
    monkeypatch.setattr(login_service, "verify_username", lambda u, c: False)
    # password check shouldn't even be called, but stub it to True
    monkeypatch.setattr(login_service, "verify_password", lambda p, h: True)

    # Act
    resp = client.post("/login/", data=make_form("baduser", "secret"))

    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Invalid username"


def test_login_invalid_password(client: TestClient, monkeypatch):
    # Arrange: username OK, password fails
    monkeypatch.setattr(login_service, "verify_username", lambda u, c: True)
    monkeypatch.setattr(login_service, "verify_password", lambda p, h: False)

    # Act
    resp = client.post("/login/", data=make_form("admin", "wrongpass"))

    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Invalid password"
