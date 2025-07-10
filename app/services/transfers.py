from datetime import datetime
from decimal import Decimal
from pydantic import Field
from sqlalchemy.orm import Session

import app.services.accounts as accounts_service
from app.config import TIMEZONE
from app.exceptions import (InsufficientFundsError,
                            SameAccountError, AccountNotFoundError)
from app.models.transfers import Transfer


def perform_transfer(
    db: Session, from_acc: int, to_acc: int, amount: Decimal = Field(..., gt=0)
) -> Transfer:
    """
    Move funds from one account to another, recording the transfer.

    Args:
        db (Session): SQLAlchemy session to use for queries and persistence.
        from_acc (int): Account number to debit.
        to_acc (int): Account number to credit.
        amount (Decimal): Amount to transfer; must be greater than zero.

    Returns:
        Transfer: The newly created Transfer ORM object, including timestamp.

    Raises:
        SameAccountError: If from_acc and to_acc are the same.
        InsufficientFundsError: If the source account’s balance is less than amount.
    """
    from_acc_validated = accounts_service.get_account_by_number(db, from_acc)
    to_acc_validated = accounts_service.get_account_by_number(db, to_acc)

    if from_acc_validated.account_number == to_acc_validated.account_number:
        raise SameAccountError(from_acc_validated.account_number)

    if from_acc_validated.balance < amount:
        raise InsufficientFundsError(from_acc_validated.balance, amount)

    from_acc_validated.balance -= amount
    to_acc_validated.balance += amount

    transfer = Transfer(
        from_account_number=from_acc_validated.account_number,
        to_account_number=to_acc_validated.account_number,
        amount=amount,
        timestamp=datetime.now(TIMEZONE),
    )

    db.add(transfer)
    db.commit()
    db.refresh(transfer)

    return transfer


def get_transfer_history_for_account(
    db: Session, account_number: int
) -> list[Transfer]:
    """
    Retrieve all transfers involving a given account, newest first.

    Args:
        db (Session): SQLAlchemy session to use for the query.
        account_number (int): The account number whose history to fetch.

    Returns:
        List[Transfer]: A list of Transfer ORM objects where the given account
                        is either the source or the destination, ordered by
                        timestamp descending.

    (No exceptions are raised here; any SQLAlchemyError will propagate to the caller.)
    """
    account_validated = accounts_service.get_account_by_number(db, account_number)
    
    return (
        db.query(Transfer)
        .filter(
            (Transfer.from_account_number == account_validated.account_number)
            | (Transfer.to_account_number == account_validated.account_number)
        )
        .order_by(Transfer.timestamp.desc())
        .all()
    )
