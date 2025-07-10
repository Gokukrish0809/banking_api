from decimal import Decimal
from pydantic import Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import AccountNotFoundError
from app.models.accounts import Account, Customer


def create_customer(db: Session, customer_data) -> Customer:
    """
    Retrieve an existing customer by email if exists or create a new one.

    Args:
        db (Session): SQLAlchemy database session.
        customer_data: An object with `.name` and `.email` attributes
                       (e.g. a Pydantic CustomerInput).

    Returns:
        Customer: The existing or newly created Customer ORM instance.
    """
    try:
        cust = (
            db.query(Customer)
            .filter(Customer.email == customer_data.email)
            .one_or_none()
        )
        if not cust:
            cust = Customer(name=customer_data.name, email=customer_data.email)
            db.add(cust)
            db.commit()
            db.refresh(cust)
        return cust
    except IntegrityError:
        db.rollback()
        return db.query(Customer).filter_by(email=customer_data.email).one()


def create_account_for_customer(
    db: Session, customer: Customer, initial_deposit: Decimal = Field(..., gt=1)
) -> Account:
    """
    Create a new bank account for a given customer with an initial balance.

    Args:
        db (Session): SQLAlchemy database session.
        customer (Customer): The Customer ORM instance to associate the new account with.
        initial_deposit (Decimal): The starting balance for the account. Must be > 1.

    Returns:
        Account: The newly created Account ORM instance, with generated
                 `account_number` and persisted `balance`.
    """
    account = Account(customer_id=customer.customer_id, balance=initial_deposit)

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


def get_account_by_number(db: Session, account_number: int) -> Account:
    """
    Look up an account by its account number.

    Args:
        db (Session): SQLAlchemy database session.
        account_number (int): The unique account number to search for.

    Returns:
        Account: The Account ORM instance matching the given number.

    Raises:
        AccountNotFoundError: If no account with the given number exists.
    """
    account = (
        db.query(Account).filter(Account.account_number == account_number).one_or_none()
    )

    if not account:
        raise AccountNotFoundError(account_number)

    return account
