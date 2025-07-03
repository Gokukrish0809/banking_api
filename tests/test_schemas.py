import pytest
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError

from db.schemas import (
    CustomerInput,
    AccountOutput,
    TransferInput,
    TransferOutput,
    BalanceOutput,
    LoginInput,
    Token,
    TokenData,
)

# Dummy classes for from_attributes testing
class DummyAccount:
    def __init__(self, account_number, balance, customer_id, name, email):
        self.account_number = account_number
        self.balance = balance
        self.customer_id = customer_id
        self.name = name
        self.email = email

class DummyTransfer:
    def __init__(self, from_account_number, to_account_number, amount, timestamp):
        self.from_account_number = from_account_number
        self.to_account_number = to_account_number
        self.amount = amount
        self.timestamp = timestamp


def test_customer_input_valid_and_invalid():
    # Valid input
    ci = CustomerInput(name="Alice", email="alice@example.com", initial_deposit=Decimal("10.50"))
    assert ci.name == "Alice"
    assert ci.email == "alice@example.com"
    assert ci.initial_deposit == Decimal("10.50")

    # Invalid: non-positive initial_deposit
    with pytest.raises(ValidationError):
        CustomerInput(name="Bob", email="bob@example.com", initial_deposit=Decimal("0"))

    # Invalid: bad email
    with pytest.raises(ValidationError):
        CustomerInput(name="Carol", email="not-an-email", initial_deposit=Decimal("5"))


def test_account_output_from_attributes_and_validation():
    dummy = DummyAccount(
        account_number=123,
        balance=Decimal("150.75"),
        customer_id=5,
        name="Dave",
        email="dave@example.com"
    )
    # Pydantic v2: use model_validate with from_attributes
    ao = AccountOutput.model_validate(dummy, from_attributes=True)
    assert ao.account_number == 123
    assert ao.balance == Decimal("150.75")
    assert ao.customer_id == 5
    assert ao.name == "Dave"
    assert ao.email == "dave@example.com"

    # Invalid: zero or negative balance
    with pytest.raises(ValidationError):
        AccountOutput(
            account_number=1,
            balance=Decimal("0"),
            customer_id=1,
            name="Eve",
            email="eve@example.com"
        )


def test_transfer_input_valid_and_invalid():
    # Valid
    ti = TransferInput(from_account_number=1, to_account_number=2, amount=Decimal("20"))
    assert ti.amount == Decimal("20")

    # Invalid: non-positive amount
    with pytest.raises(ValidationError):
        TransferInput(from_account_number=1, to_account_number=2, amount=Decimal("0"))


def test_transfer_output_from_attributes_and_validation():
    now = datetime.utcnow()
    dummy = DummyTransfer(
        from_account_number=10,
        to_account_number=20,
        amount=Decimal("33.33"),
        timestamp=now
    )
    # Pydantic v2: use model_validate
    to = TransferOutput.model_validate(dummy, from_attributes=True)
    assert to.from_account_number == 10
    assert to.to_account_number == 20
    assert to.amount == Decimal("33.33")
    assert to.timestamp == now

    # Invalid: zero amount
    with pytest.raises(ValidationError):
        TransferOutput(
            from_account_number=1,
            to_account_number=2,
            amount=Decimal("0"),
            timestamp=now
        )


def test_balance_output_valid_and_invalid():
    # Valid
    bo = BalanceOutput(account_number=7, balance=Decimal("5"))
    assert bo.account_number == 7
    assert bo.balance == Decimal("5")

    # Invalid: zero or negative balance
    with pytest.raises(ValidationError):
        BalanceOutput(account_number=8, balance=Decimal("0"))


def test_login_input_simple():
    li = LoginInput(username="user", password="pass")
    assert li.username == "user"
    assert li.password == "pass"


def test_token_model():
    t = Token(access_token="abc123", token_type="bearer")
    assert t.access_token == "abc123"
    assert t.token_type == "bearer"


def test_token_data_defaults_and_assignment():
    td = TokenData()
    assert td.username is None

    td2 = TokenData(username="frank")
    assert td2.username == "frank"
