from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from decimal import Decimal
from config import TIMEZONE

class Customer(Base):
    """
    Reprensents a customer in the bank
    Attributes :
    __tablename__ : The table name in the database
    customer_id : Unique identifier for the customner
    name : Name of the customer
    email : A uniue email id of the customer
    accounts : A relationship to the accounts owned by a customer
    """
    __tablename__ = 'customers'

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    accounts = relationship("Account", back_populates="customer")

class Account(Base):
    """
    Represents an account owned by a customer
    Attributes :
    __tablename__ : The table name in the database
    account_number : A unique identifier for an account for the customer
    balance : The balance amount in an account
    customer_id : The customer_id linked to this particular account
    sent_transfers : A relationship to the accounts in transfers table which dentoes the transfer sent
    received_transfers : A relationship to the accounts in transfers table which dentoes the transfer received
    """
    __tablename__ = 'accounts'
    account_number = Column(Integer, primary_key=True, index=True)
    balance = Column(Numeric(precision=12, scale=2), default=Decimal('0.00'))
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))

    customer = relationship("Customer", back_populates="accounts")
    
    sent_transfers = relationship(
        "Transfer",
        foreign_keys="Transfer.from_account_number",
        back_populates="from_account"
    )
    received_transfers = relationship(
        "Transfer",
        foreign_keys="Transfer.to_account_number",
        back_populates="to_account"
    )

class Transfer(Base):
    """
    A table to store the transfers
    Attributes :
    __tablename__ : Table name
    id : Unique id for the transfer
    from_account_number : Account number from which the money was sent
    to_account_number : Account number to which the money was sent
    amount : The amount of money transferred
    timestamp : The time at which the transfer was done
    from_account : A relationship to the account in the account table
    to_account : A relationship to the account in the account table
    """
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True, index=True)
    from_account_number = Column(Integer, ForeignKey("accounts.account_number"), nullable=False)
    to_account_number = Column(Integer, ForeignKey("accounts.account_number"), nullable=False)
    amount = Column(Numeric(precision=12, scale=2), default=Decimal('0.00'))
    timestamp = Column(DateTime, default=datetime.now(TIMEZONE), nullable=False)

    from_account = relationship(
        "Account",
        foreign_keys=[from_account_number],
        back_populates="sent_transfers"
    )
    to_account = relationship(
        "Account",
        foreign_keys=[to_account_number],
        back_populates="received_transfers"
    )