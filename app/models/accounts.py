from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base


class CustomerInput(BaseModel):
    """
    Pydantic schema for creating a new customer account.

    Attributes:
        name (str): The full name of the customer.
        email (EmailStr): A unique, valid email address for the customer.
        initial_deposit (Decimal): The opening deposit amount for the new account.
            Must be greater than 0.
    """

    name: str
    email: EmailStr
    initial_deposit: Decimal = Field(..., gt=0)

    class Config:
        schema_extra = {
            "example": {
                "name": "Alice Wonderland",
                "email": "alice@example.com",
                "initial_deposit": "250.00"
            }
        }


class AccountOutput(BaseModel):
    """
    Pydantic schema for returning account details in responses.

    Attributes:
        account_number (int): The unique identifier for the account.
        balance (Decimal): The current account balance. Must be greater than 0.
        customer_id (int): The ID of the customer who owns this account.
        name (str): The customer’s full name.
        email (EmailStr): The customer’s email address.
    """

    account_number: int
    balance: Decimal = Field(..., gt=0)
    customer_id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True


class BalanceOutput(BaseModel):
    """
    Pydantic schema for returning only the balance of an account.

    Attributes:
        account_number (int): The unique identifier for the account.
        balance (Decimal): The current account balance. Must be greater than 0.
    """

    account_number: int
    balance: Decimal = Field(..., gt=0)

    class Config:
        orm_mode = True


class Customer(Base):
    """
    SQLAlchemy ORM model for the customers table.

    Columns:
        customer_id (int): Primary key, auto-incremented customer identifier.
        name (str): The full name of the customer. Cannot be null.
        email (str): Unique email address of the customer. Cannot be null.
        accounts (Relationship[List[Account]]): All accounts belonging to this customer.

    Relationships:
        accounts (List[Account]): All bank accounts owned by this customer.
        sent_transfers (List[Transfer]): All transfers _from_ any of this customer's accounts.
        received_transfers (List[Transfer]): All transfers _to_ any of this customer's accounts.
    """

    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    accounts = relationship("Account", back_populates="customer")


class Account(Base):
    """
    SQLAlchemy ORM model for the accounts table.

    Columns:
        account_number (int): Primary key, auto-incremented account identifier.
        balance (Decimal): The current balance of the account.
        customer_id (int): Foreign key pointing to the owning customer’s ID.

    Relationships:
        customer (Customer): The owner of this account.
        sent_transfers (Relationship[List[Transfer]]): Transfers sent from this account.
        received_transfers (Relationship[List[Transfer]]): Transfers received by this account.
    """

    __tablename__ = "accounts"

    account_number = Column(Integer, primary_key=True, index=True)
    balance = Column(Numeric(precision=12, scale=2), default=Decimal("0.00"))
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    customer = relationship("Customer", back_populates="accounts")

    sent_transfers = relationship(
        "Transfer",
        foreign_keys="Transfer.from_account_number",
        back_populates="from_account",
    )
    received_transfers = relationship(
        "Transfer",
        foreign_keys="Transfer.to_account_number",
        back_populates="to_account",
    )
