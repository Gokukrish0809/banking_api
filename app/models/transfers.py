from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from app.config import TIMEZONE
from app.database import Base


class TransferInput(BaseModel):
    """
    Pydantic schema for initiating a funds transfer.

    Attributes:
        from_account_number (int): The account number to debit funds from.
        to_account_number (int): The account number to credit funds to.
        amount (Decimal): The amount to transfer. Must be greater than 0.
    """

    from_account_number: int
    to_account_number: int
    amount: Decimal = Field(..., gt=0)

    class Config:
        schema_extra = {
            "example": {
                "from_account_number": 1234,
                "to_account_number":   5678,
                "amount":              "100.00"
            }
        }


class TransferOutput(BaseModel):
    """
    Pydantic schema for returning transfer details in responses.

    Attributes:
        from_account_number (int): The source account number.
        to_account_number (int): The destination account number.
        amount (Decimal): The transferred amount.
        timestamp (datetime): ISO timestamp when the transfer occurred.
    """

    from_account_number: int
    to_account_number: int
    amount: Decimal = Field(..., gt=0)
    timestamp: datetime

    class Config:
        orm_mode = True


class Transfer(Base):
    """
    SQLAlchemy ORM model for the transfers table.

    Columns:
        id (int): Primary key, unique transfer identifier.
        from_account_number (int): FK to accounts.account_number, source account.
        to_account_number (int): FK to accounts.account_number, destination account.
        amount (Decimal): The amount of money transferred.
        timestamp (datetime): When the transfer was executed (default=now).

    Relationships:
        from_account (Account): The Account object from which funds were debited.
        to_account   (Account): The Account object to which funds were credited.
    """

    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True, index=True)
    from_account_number = Column(
        Integer, ForeignKey("accounts.account_number"), nullable=False
    )
    to_account_number = Column(
        Integer, ForeignKey("accounts.account_number"), nullable=False
    )
    amount = Column(Numeric(precision=12, scale=2), default=Decimal("0.00"))
    timestamp = Column(DateTime, default=datetime.now(TIMEZONE), nullable=False)

    from_account = relationship(
        "Account", foreign_keys=[from_account_number], back_populates="sent_transfers"
    )
    to_account = relationship(
        "Account", foreign_keys=[to_account_number], back_populates="received_transfers"
    )
