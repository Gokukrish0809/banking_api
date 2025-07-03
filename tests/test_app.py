# tests/test_util_py.py
import pytest
from decimal import Decimal
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from db.database import Base
from db.models import Customer, Account, Transfer
from utils.util import (
    get_or_create_customer,
    create_account_for_customer,
    get_account_by_number,
    perform_transfer,
    get_transfer_history_for_account,
)

import re
from utils.util import hash_password, verify_password

@pytest.fixture(autouse=True)
def patch_timezone(monkeypatch):
    # Ensure datetime.now(TIMEZONE) is UTC for predictability
    monkeypatch.setattr(config, "TIMEZONE", timezone.utc)

@pytest.fixture(scope="module")
def engine():
    # In-memory SQLite for tests
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    return eng

@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    sess = Session()
    try:
        yield sess
    finally:
        sess.rollback()
        sess.close()

def test_get_or_create_customer_creates_and_returns(db_session):
    class C: name = "Alice"; email = "alice@example.com"
    # First call: should create
    cust1 = get_or_create_customer(db_session, C)
    assert cust1.customer_id is not None
    assert cust1.name == "Alice"
    assert cust1.email == "alice@example.com"

    # Second call: should fetch same
    cust2 = get_or_create_customer(db_session, C)
    assert cust2.customer_id == cust1.customer_id

def test_create_account_for_customer(db_session):
    # Prep a customer
    cust = Customer(name="Bob", email="bob@example.com")
    db_session.add(cust); db_session.commit(); db_session.refresh(cust)

    # Create account with deposit > 1
    acc = create_account_for_customer(db_session, cust, Decimal("150.00"))
    assert acc.account_number is not None
    assert isinstance(acc.account_number, int)
    assert acc.balance == Decimal("150.00")
    assert acc.customer_id == cust.customer_id

def test_get_account_by_number_not_found(db_session):
    with pytest.raises(HTTPException) as exc:
        get_account_by_number(db_session, 9999)
    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()

def test_get_account_by_number_success(db_session):
    # Prep customer & account
    cust = Customer(name="Carol", email="carol@example.com")
    db_session.add(cust); db_session.commit(); db_session.refresh(cust)
    acc_created = create_account_for_customer(db_session, cust, Decimal("20.00"))

    # Fetch it
    acc = get_account_by_number(db_session, acc_created.account_number)
    assert acc.account_number == acc_created.account_number
    assert acc.balance == Decimal("20.00")

def test_perform_transfer_insufficient_and_success(db_session):
    # Setup two customers & accounts
    c1 = get_or_create_customer(db_session, type("X",(object,),{"name":"Dana","email":"dana@example.com"}))
    c2 = get_or_create_customer(db_session, type("Y",(object,),{"name":"Eli","email":"eli@example.com"}))
    a1 = create_account_for_customer(db_session, c1, Decimal("50"))
    a2 = create_account_for_customer(db_session, c2, Decimal("10"))

    # Insufficient funds
    with pytest.raises(HTTPException) as exc:
        perform_transfer(db_session, a2, a1, Decimal("20"))
    assert exc.value.status_code == 400
    assert "insufficient" in exc.value.detail.lower()

    # Successful transfer
    tr = perform_transfer(db_session, a1, a2, Decimal("30"))
    # balances updated
    assert a1.balance == Decimal("20")
    assert a2.balance == Decimal("40")
    # transfer record correct
    assert isinstance(tr, Transfer)
    assert tr.from_account_number == a1.account_number
    assert tr.to_account_number == a2.account_number
    assert tr.amount == Decimal("30")
    # timestamp was set using our patched TIMEZONE
    assert isinstance(tr.timestamp, datetime)

def test_get_transfer_history_for_account(db_session):
    # Single customer, two accounts
    cust = get_or_create_customer(db_session, type("Z",(object,),{"name":"Fay","email":"fay@example.com"}))
    a1 = create_account_for_customer(db_session, cust, Decimal("100"))
    a2 = create_account_for_customer(db_session, cust, Decimal("0"))

    # Perform two transfers: a1→a2 then a2→a1
    t1 = perform_transfer(db_session, a1, a2, Decimal("40"))
    t2 = perform_transfer(db_session, a2, a1, Decimal("15"))

    history = get_transfer_history_for_account(db_session, a1.account_number)
    # Should include both, ordered newest first (t2 then t1)
    assert len(history) == 2
    assert history[0].id == t2.id
    assert history[1].id == t1.id
    # amounts match
    assert history[0].amount == Decimal("15")
    assert history[1].amount == Decimal("40")



@pytest.fixture
def plain_password():
    return "password"

def test_hash_password_returns_bcrypt_hash(plain_password):
    hashed = hash_password(plain_password)
    # Should be a string, not equal to the plain text
    assert isinstance(hashed, str)
    assert hashed != plain_password
    # Bcrypt hashes start with $2b$ or $2a$
    assert re.match(r"^\$2[abxy]?\$[0-9]{2}\$[./A-Za-z0-9]{53}$", hashed)

def test_verify_password_succeeds(plain_password):
    hashed = hash_password(plain_password)
    assert verify_password(plain_password, hashed) is True

def test_verify_password_fails_on_wrong_password(plain_password):
    hashed = hash_password(plain_password)
    assert verify_password("wrong-password", hashed) is False
