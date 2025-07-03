import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import routers.transfers
from routers.transfers import router
from db.database import get_db
from authentication.oauth import get_current_user
from utils.util import get_account_by_number, perform_transfer, get_transfer_history_for_account

# Dummy DB session for testing
class DummySession:
    def __init__(self, has_account=True):
        self._has_account = has_account
    def query(self, model):
        return self
    def filter(self, condition):
        return self
    def first(self):
        # For transfer history existence check
        return object() if self._has_account else None
    def rollback(self):
        pass

# Create FastAPI app and override dependencies
app = FastAPI()
app.include_router(router, prefix="/transfers")

@pytest.fixture(autouse=True)
def client(monkeypatch):
    # Bypass authentication
    app.dependency_overrides[get_current_user] = lambda: "test_user"
    # Default DB session returns "existing" account
    app.dependency_overrides[get_db] = lambda: DummySession(has_account=True)
    return TestClient(app)

# Dummy account and record classes
class DummyAccount:
    def __init__(self, number=1, balance=100):
        self.account_number = number
        self.balance = balance

class DummyRecord:
    def __init__(self, from_acc, to_acc, amount, timestamp="2025-07-03T12:00:00"):
        self.from_account_number = from_acc
        self.to_account_number = to_acc
        self.amount = amount
        self.timestamp = timestamp

# Test successful transfer
def test_transfer_success(monkeypatch, client):
    fa = DummyAccount(number=10, balance=200)
    ta = DummyAccount(number=20, balance=50)
    rec = DummyRecord(10, 20, 50)

    monkeypatch.setattr(routers.transfers, 'get_account_by_number', lambda db, num: fa if num==10 else ta)
    monkeypatch.setattr(routers.transfers, 'perform_transfer', lambda db, f, t, amt: rec)

    response = client.post("/transfers/", json={"from_account_number":10, "to_account_number":20, "amount":50})
    assert response.status_code == 200
    assert response.json() == {"from_account_number": 10, "to_account_number": 20, "amount": "50", "timestamp":"2025-07-03T12:00:00"}

# Test transfer to same account
def test_transfer_same_account(monkeypatch, client):
    a = DummyAccount(number=5, balance=100)
    monkeypatch.setattr(routers.transfers, 'get_account_by_number', lambda db, num: a)

    response = client.post("/transfers/", json={"from_account_number":5, "to_account_number":5, "amount":10})
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot transfer to the same account"

# Test insufficient funds
def test_transfer_insufficient_funds(monkeypatch, client):
    fa = DummyAccount(number=1, balance=20)
    ta = DummyAccount(number=2, balance=0)
    monkeypatch.setattr(routers.transfers, 'get_account_by_number', lambda db, num: fa if num==1 else ta)

    response = client.post("/transfers/", json={"from_account_number":1, "to_account_number":2, "amount":50})
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds in source account"

# Test perform_transfer raising HTTPException
def test_transfer_util_http_exception(monkeypatch, client):
    fa = DummyAccount(number=1, balance=100)
    ta = DummyAccount(number=2, balance=0)
    monkeypatch.setattr(routers.transfers, 'get_account_by_number', lambda db, num: fa if num==1 else ta)
    monkeypatch.setattr(routers.transfers, 'perform_transfer', lambda db, f, t, amt: (_ for _ in ()).throw(HTTPException(status_code=422, detail="Bad transfer")))

    response = client.post("/transfers/", json={"from_account_number":1, "to_account_number":2, "amount":10})
    assert response.status_code == 422
    assert response.json()["detail"] == "Bad transfer"

# Test perform_transfer unexpected exception
def test_transfer_util_exception(monkeypatch, client):
    fa = DummyAccount(number=1, balance=100)
    ta = DummyAccount(number=2, balance=0)
    monkeypatch.setattr(routers.transfers, 'get_account_by_number', lambda db, num: fa if num==1 else ta)
    monkeypatch.setattr(routers.transfers, 'perform_transfer', lambda db, f, t, amt: (_ for _ in ()).throw(Exception("db locked")))

    response = client.post("/transfers/", json={"from_account_number":1, "to_account_number":2, "amount":10})
    assert response.status_code == 500
    assert "Transfer failed" in response.json()["detail"]

# Test successful transfer history retrieval
def test_get_transfer_history_success(monkeypatch, client):
    # Override DB to indicate account exists
    app.dependency_overrides[get_db] = lambda: DummySession(has_account=True)
    recs = [DummyRecord(1,2,30), DummyRecord(3,1,20)]
    monkeypatch.setattr(routers.transfers, 'get_transfer_history_for_account', lambda db, num: recs)

    response = client.get("/transfers/1/transfer_history")
    assert response.status_code == 200
    assert response.json() == [{"from_account_number": 1, "to_account_number": 2, "amount": "30", "timestamp":"2025-07-03T12:00:00"},
                                 {"from_account_number":3, "to_account_number":1, "amount": "20", "timestamp":"2025-07-03T12:00:00"}]

# Test transfer history when account does not exist
def test_get_transfer_history_no_account(client):
    app.dependency_overrides[get_db] = lambda: DummySession(has_account=False)

    response = client.get("/transfers/999/transfer_history")
    assert response.status_code == 400
    assert response.json()["detail"] == "Account number does not exist"

# Test transfer history DB error
def test_get_transfer_history_db_error(monkeypatch, client):
    app.dependency_overrides[get_db] = lambda: DummySession(has_account=True)
    monkeypatch.setattr(routers.transfers, 'get_transfer_history_for_account', lambda db, num: (_ for _ in ()).throw(Exception("timeout")))

    response = client.get("/transfers/1/transfer_history")
    assert response.status_code == 500
    assert "Could not fetch history" in response.json()["detail"]
