from decimal import Decimal
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.query import Query

from app.exceptions import AccountNotFoundError
from app.models.accounts import Customer
from app.services import accounts as service


def test_create_customer_new(db_session, mock_customer_input):
    resp = service.create_customer(db_session, mock_customer_input)
    assert isinstance(resp, Customer)
    assert resp.name == "Bob"
    assert resp.email == "bob@example.com"


def test_create_customer_exists(db_session, mock_customer_record, mock_customer_input):
    # Add a customer record to mock db
    db_session.add(mock_customer_record)
    db_session.commit()

    # Test create customer with existing customer details
    resp = service.create_customer(db_session, mock_customer_input)
    assert resp.customer_id == mock_customer_record.customer_id


def test_get_or_create_customer_integrity_error_branch(
    db_session, mock_customer_input, monkeypatch
):
    # First call: inserts the row
    orig = service.create_customer(db_session, mock_customer_input)
    assert isinstance(orig, Customer)

    # Mock Query.one_or_none mocking there is NO existing customer
    monkeypatch.setattr(
        Query,
        "one_or_none",
        lambda self: None,
    )

    # Mock commit() to throw IntegrityError
    def fake_commit():
        raise IntegrityError("UNIQUE constraint failed", params=None, orig=None)

    monkeypatch.setattr(db_session, "commit", fake_commit)

    # Mock rollback()
    monkeypatch.setattr(db_session, "rollback", lambda: None)

    # Now call again
    dup = service.create_customer(db_session, mock_customer_input)

    assert dup.customer_id == orig.customer_id

    # And ensure we didn’t accidentally add a second row
    count = (
        db_session.query(Customer).filter_by(email=mock_customer_input.email).count()
    )
    assert count == 1


def test_create_account_success_customer_exists(db_session, mock_customer_record):
    # prepare a customer record
    db_session.add(mock_customer_record)
    db_session.commit()
    db_session.refresh(mock_customer_record)

    resp = service.create_account_for_customer(
        db_session, mock_customer_record, Decimal("100.00")
    )
    assert resp.account_number is not None
    assert resp.balance == Decimal("100.00")


def test_get_account_by_number_success(db_session, mock_customer_input):

    cust = service.create_customer(db_session, mock_customer_input)
    acct = service.create_account_for_customer(db_session, cust, Decimal("50.0"))

    resp = service.get_account_by_number(db_session, acct.account_number)

    assert resp.account_number == acct.account_number
    assert resp.customer_id == cust.customer_id
    assert resp.balance == acct.balance


def test_get_account_not_found(db_session):
    with pytest.raises(AccountNotFoundError):
        service.get_account_by_number(db_session, 999999)
