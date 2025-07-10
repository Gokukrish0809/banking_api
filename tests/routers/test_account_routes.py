import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.authentication.oauth import get_current_user
from app.services import accounts as account_service


@pytest.fixture(autouse=True)
def override_auth(client: TestClient):
    """
    Stub out get_current_user for all tests in this module.
    """
    client.app.dependency_overrides[get_current_user] = lambda: {"sub": "testuser"}
    yield
    client.app.dependency_overrides.pop(get_current_user, None)


def test_create_account_happy_path(client: TestClient):
    payload = {"name": "random", "email": "random@example.com", "initial_deposit": 123.45}
    resp = client.post("/accounts/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # New account should have these fields:
    assert "account_number" in data
    assert data["name"] == "random"
    assert data["email"] == "random@example.com"
    assert float(data["balance"]) == pytest.approx(123.45)


def test_create_account_500_response(client, monkeypatch):
    # Arrange: make get_or_create_customer raise a SQLAlchemyError
    def fake_get_or_create(db, customer):
        raise SQLAlchemyError("simulated DB failure")

    monkeypatch.setattr(account_service, "create_customer", fake_get_or_create)

    payload = {
        "name": "Something",
        "email": "something@example.com",
        "initial_deposit": 10.0,
    }

    # Act
    resp = client.post("/accounts/", json=payload)

    # Assert
    assert resp.status_code == 500
    assert "internal server error" in resp.json()["detail"].lower()


def test_get_balance_happy_path(client: TestClient):
    # First create an account
    payload = {"name": "Bob", "email": "bob@example.com", "initial_deposit": 50.0}
    create = client.post("/accounts/", json=payload)
    assert create.status_code == 200
    acct_no = create.json()["account_number"]

    # Now fetch its balance
    resp = client.get(f"/accounts/{acct_no}/balance")
    assert resp.status_code == 200
    bal = resp.json()
    assert bal["account_number"] == acct_no
    assert float(bal["balance"]) == pytest.approx(50.0)


def test_get_balance_account_not_found(client: TestClient):
    # No accounts in DB, so this should 404
    resp = client.get("/accounts/9999/balance")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_get_balance_returns_500_response(client, monkeypatch):
    # Arrange: force the service to throw a SQLAlchemyError
    def fake_get_account(db, acct_no):
        raise SQLAlchemyError("simulated read failure")

    monkeypatch.setattr(account_service, "get_account_by_number", fake_get_account)

    # Act
    resp = client.get("/accounts/99999/balance")

    # Assert
    assert resp.status_code == 500
    body = resp.json()
    assert "internal server error" in body["detail"].lower()
