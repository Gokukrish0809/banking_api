from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

import app.services.transfers as transfer_service
from app.authentication.oauth import get_current_user


@pytest.fixture(autouse=True)
def override_auth(client: TestClient):
    client.app.dependency_overrides[get_current_user] = lambda: {"sub": "testuser"}
    yield
    client.app.dependency_overrides.pop(get_current_user, None)


def create_account(client: TestClient, name: str, email: str, deposit: Decimal) -> int:
    # send Decimal as string
    resp = client.post(
        "/accounts/",
        json={"name": name, "email": email, "initial_deposit": str(deposit)},
    )
    assert resp.status_code == 200
    return resp.json()["account_number"]


def make_transfer_payload(f: int, t: int, amt: Decimal):
    return {"from_account_number": f, "to_account_number": t, "amount": str(amt)}


BASE = "/transfers"


def test_transfer_funds_happy_path(client: TestClient):
    acc1 = create_account(client, "Alice", "alice@example.com", Decimal("100.00"))
    acc2 = create_account(client, "Bob", "bob@example.com", Decimal(" 50.00"))

    resp = client.post(
        BASE + "/", json=make_transfer_payload(acc1, acc2, Decimal("30.00"))
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["from_account_number"] == acc1
    assert data["to_account_number"] == acc2
    # JSON comes back as string or number; convert to Decimal for comparison
    assert Decimal(str(data["amount"])) == Decimal("30.00")
    assert "timestamp" in data


def test_transfer_funds_same_account(client: TestClient):
    acc = create_account(client, "Charlie", "charlie@example.com", Decimal("100"))
    resp = client.post(
        BASE + "/", json=make_transfer_payload(acc, acc, Decimal("10.00"))
    )
    assert resp.status_code == 404
    assert "same account" in resp.json()["detail"].lower()


def test_transfer_funds_insufficient(client: TestClient):
    a1 = create_account(client, "Dave", "dave@example.com", Decimal("20.00"))
    a2 = create_account(client, "Eve", "eve@example.com", Decimal("10.00"))
    resp = client.post(BASE + "/", json=make_transfer_payload(a2, a1, Decimal("30.00")))
    assert resp.status_code == 400
    assert "insufficient" in resp.json()["detail"].lower()


def test_transfer_funds_not_found(client: TestClient):
    resp = client.post(
        BASE + "/", json=make_transfer_payload(999, 1000, Decimal("5.00"))
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_transfer_funds_500(client: TestClient, monkeypatch):
    monkeypatch.setattr(
        transfer_service,
        "perform_transfer",
        lambda db, f, t, a: (_ for _ in ()).throw(
            SQLAlchemyError("simulated db error")
        ),
    )
    resp = client.post(BASE + "/", json=make_transfer_payload(1, 2, Decimal("1.00")))
    assert resp.status_code == 500
    assert "internal server error" in resp.json()["detail"].lower()


def test_get_history_happy_path(client: TestClient):
    a1 = create_account(client, "Frank", "frank@example.com", Decimal("100.00"))
    a2 = create_account(client, "Grace", "grace@example.com", Decimal("50.00"))
    # two transfers
    client.post(BASE + "/", json=make_transfer_payload(a1, a2, Decimal("10.00")))
    client.post(BASE + "/", json=make_transfer_payload(a2, a1, Decimal("5.00")))

    resp = client.get(f"{BASE}/{a1}/transfer_history")
    assert resp.status_code == 200
    lst = resp.json()
    assert len(lst) == 2
    assert Decimal(str(lst[0]["amount"])) == Decimal("5.00")
    assert Decimal(str(lst[1]["amount"])) == Decimal("10.00")


def test_get_history_empty(client: TestClient):
    a = create_account(client, "Henry", "henry@example.com", Decimal("10.00"))
    resp = client.get(f"{BASE}/{a}/transfer_history")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_history_500(client: TestClient, monkeypatch):
    monkeypatch.setattr(
        transfer_service,
        "get_transfer_history_for_account",
        lambda db, acct: (_ for _ in ()).throw(SQLAlchemyError("simulated db error")),
    )
    resp = client.get(f"{BASE}/1/transfer_history")
    assert resp.status_code == 500
    assert "internal server error" in resp.json()["detail"].lower()
