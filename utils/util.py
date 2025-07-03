from fastapi import HTTPException
from sqlalchemy.orm import Session
from db.models import Customer, Account, Transfer
from datetime import datetime
from pydantic import Field
from decimal import Decimal
from passlib.context import CryptContext
from config import TIMEZONE

def get_or_create_customer(db: Session, customer_data):
    customer = db.query(Customer).filter(Customer.email == customer_data.email).first()
    if not customer:
        customer = Customer(name=customer_data.name, email=customer_data.email)
        db.add(customer)
        db.commit()
        db.refresh(customer)
    return customer

def create_account_for_customer(db: Session, customer: Customer, initial_deposit: Decimal = Field(..., gt=1)):
    account = Account(customer_id=customer.customer_id, balance=initial_deposit)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

def get_account_by_number(db: Session, account_number: int) -> Account:
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

def perform_transfer(
    db: Session,
    from_acc: Account,
    to_acc: Account,
    amount: Decimal = Field(..., gt=0)
) -> Transfer:
    if from_acc.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    from_acc.balance -= amount
    to_acc.balance   += amount
    transfer = Transfer(
        from_account_number=from_acc.account_number,
        to_account_number=to_acc.account_number,
        amount=amount,
        timestamp=datetime.now(TIMEZONE)
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    
    return transfer

def get_transfer_history_for_account(
    db: Session,
    account_number: int
) -> list[Transfer]:
    
    return db.query(Transfer)\
             .filter(
                 (Transfer.from_account_number == account_number) |
                 (Transfer.to_account_number   == account_number)
             )\
             .order_by(Transfer.timestamp.desc())\
             .all()



def hash_password(plain_password : str) -> str :
    pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated = "auto")
    return pwd_cxt.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated = "auto")
    return pwd_cxt.verify(plain_password, hashed_password)