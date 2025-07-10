from datetime import datetime
from decimal import Decimal
import pytest

import app.services.accounts as account_service
import app.services.transfers as transfer_service
from app.exceptions import (AccountNotFoundError, InsufficientFundsError,
                            SameAccountError)
from app.models.transfers import Transfer


@pytest.fixture
def two_accounts(db_session, mock_customer_input):
    """
    Create one customer and two accounts for them:
      - acct1 with 200
      - acct2 with 50
    """
    cust = account_service.create_customer(db_session, mock_customer_input)
    acct1 = account_service.create_account_for_customer(
        db_session, cust, Decimal("200")
    )
    acct2 = account_service.create_account_for_customer(db_session, cust, Decimal("50"))
    return acct1, acct2


def test_perform_transfer_success(db_session, two_accounts):
    acct1, acct2 = two_accounts
    tx = transfer_service.perform_transfer(
        db_session, acct1.account_number, acct2.account_number, Decimal("75")
    )

    a1 = account_service.get_account_by_number(db_session, acct1.account_number)
    a2 = account_service.get_account_by_number(db_session, acct2.account_number)

    assert a1.balance == Decimal("125")
    assert a2.balance == Decimal("125")

    assert isinstance(tx, Transfer)
    assert tx.amount == Decimal("75")
    assert isinstance(tx.timestamp, datetime)


def test_same_account_error(db_session, two_accounts):
    acct1, _ = two_accounts
    with pytest.raises(SameAccountError):
        transfer_service.perform_transfer(
            db_session, acct1.account_number, acct1.account_number, Decimal("10")
        )


def test_insufficient_funds_error(db_session, two_accounts):
    acct1, acct2 = two_accounts
    # acct2 only has 50, try to send 100

    with pytest.raises(InsufficientFundsError):
        transfer_service.perform_transfer(
            db_session, acct2.account_number, acct1.account_number, Decimal("100")
        )


def test_perform_transfer_account_not_found(db_session):
    # no accounts in DB yet
    with pytest.raises(AccountNotFoundError):
        transfer_service.perform_transfer(db_session, 9999, 8888, Decimal("10"))


def test_get_transfer_history(db_session, two_accounts):
    acct1, acct2 = two_accounts
    # make two transfers
    tx1 = transfer_service.perform_transfer(
        db_session, acct1.account_number, acct2.account_number, Decimal("10")
    )
    tx2 = transfer_service.perform_transfer(
        db_session, acct2.account_number, acct1.account_number, Decimal("5")
    )

    history = transfer_service.get_transfer_history_for_account(
        db_session, acct1.account_number
    )

    assert len(history) == 2
    assert history[0].amount == Decimal("5")
    assert history[1].amount == Decimal("10")
    assert all(isinstance(rec, Transfer) for rec in history)
