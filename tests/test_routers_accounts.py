import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

# Import the router and actual dependency functions
import routers.accounts
from routers.accounts import router
from db.database import get_db
from authentication.oauth import get_current_user

# Create a dummy DB session with stubbed methods
def make_dummy_db():
    class DummySession:
        def query(self, model):
            return self
        def filter(self, condition):
            return self
        def first(self):
            return None
        def rollback(self):
            # No-op rollback for testing
            pass
    return DummySession()

# Create FastAPI app and override dependencies
app = FastAPI()
app.include_router(router, prefix="/accounts")

@pytest.fixture(autouse=True)
def client(monkeypatch):
    # Bypass authentication dependency
    app.dependency_overrides[get_current_user] = lambda: "test_user"
    # Override get_db to return a dummy session
    app.dependency_overrides[get_db] = lambda: make_dummy_db()
    return TestClient(app)

# Sample customer input for account creation
customer_input = {
    "name": "John Doe",
    "email": "john@example.com",
    "initial_deposit": 100
}

# Dummy models
class DummyCustomer:
    def __init__(self):
        self.customer_id = 1
        self.name = "John Doe"
        self.email = "john@example.com"

class DummyAccount:
    def __init__(self):
        self.account_number = 12345
        self.balance = 100

# Test creating a new account successfully
def test_create_account_success(monkeypatch, client):
    dummy_customer = DummyCustomer()
    dummy_account = DummyAccount()

    # Patch router-level utility imports
    monkeypatch.setattr(routers.accounts, 'get_or_create_customer', lambda db, c: dummy_customer)
    monkeypatch.setattr(routers.accounts, 'create_account_for_customer', lambda db, c, d: dummy_account)

    response = client.post("/accounts/", json=customer_input)
    assert response.status_code == 200
    assert response.json() == {
        "account_number": 12345,
        "balance": "100",
        "customer_id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    }

# Test account creation raises controlled HTTPException
def test_create_account_http_exception(monkeypatch, client):
    monkeypatch.setattr(routers.accounts, 'get_or_create_customer', lambda db, c: (_ for _ in ()).throw(HTTPException(status_code=400, detail="Bad request")))

    response = client.post("/accounts/", json=customer_input)
    assert response.status_code == 400
    assert response.json()["detail"] == "Bad request"

# Test account creation handles unexpected exceptions
def test_create_account_unexpected_error(monkeypatch, client):
    monkeypatch.setattr(routers.accounts, 'get_or_create_customer', lambda db, c: (_ for _ in ()).throw(Exception("DB failure")))

    response = client.post("/accounts/", json=customer_input)
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

# Test retrieving balance successfully
def test_get_balance_success(monkeypatch, client):
    dummy_account = DummyAccount()
    monkeypatch.setattr(routers.accounts, 'get_account_by_number', lambda db, num: dummy_account)

    response = client.get("/accounts/12345/balance")
    assert response.status_code == 200
    assert response.json() == {"account_number": 12345, "balance": "100"}


# Test get_balance returns 404 when util returns None
def test_get_balance_none(monkeypatch, client):
    # Patch util to return None instead of raising
    monkeypatch.setattr(routers.accounts, 'get_account_by_number', lambda db, num: None)

    response = client.get("/accounts/77777/balance")
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"


# Test database lookup error for balance endpoint
def test_get_balance_db_lookup_error(monkeypatch, client):
    # Simulate unexpected DB failure
    monkeypatch.setattr(routers.accounts, 'get_account_by_number', lambda db, num: (_ for _ in ()).throw(Exception("connection failed")))

    response = client.get("/accounts/77777/balance")
    assert response.status_code == 500
    assert "Database lookup error" in response.json()["detail"]