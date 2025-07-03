from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Customer
from db.schemas import CustomerInput, AccountOutput, BalanceOutput, LoginInput
from utils.util import (
    get_or_create_customer,
    create_account_for_customer,
    get_account_by_number
)
from authentication.oauth import get_current_user
from config import USERNAME

router = APIRouter()

@router.post("/", response_model=AccountOutput)
def create_account(
    customer: CustomerInput,
    db: Session = Depends(get_db),
    get_current_user : str = Depends(get_current_user),
    summary = "Create an account",
    description = "Retruns the details of the created account. Only accessible to authenticated users",
    responses = {
        200 : {"Description " : "Successful response"},
        500 : {"Description " : "Database error"},
    }
    ):
    """
    a function to create an account for a cutomer
    """
    # Check if customer exists by email
    customer_db = db.query(Customer).filter(Customer.email == customer.email).first()

    try:
        # Delegate to utils: get or create customer
        customer_db = get_or_create_customer(db, customer)
        # Delegate to utils: create account for customer
        new_account = create_account_for_customer(db, customer_db, customer.initial_deposit)

    except HTTPException:
        # Raise Exceptions
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {e}"
        )

    # Return combined response
    return AccountOutput(
        account_number=new_account.account_number,
        balance=new_account.balance,
        customer_id=customer_db.customer_id,
        name=customer_db.name,
        email=customer_db.email
    )   


# Endpoint: get account balance
@router.get("/{account_number}/balance", response_model=BalanceOutput)
def get_balance(
    account_number: int,
    db: Session = Depends(get_db),
    get_current_user : str = Depends(get_current_user),
    summary = "To get the balance of an account number",
    description = "Retruns the balance of an account number. Only accessible to authenticated users",
    responses = {
        200 : {"Description " : "Successful response"},
        500 : {"Description " : "Database error"},
        404 : {"Description " : "Account not found"},
    }
):
    """
    To get the balance of an account
    """
    try:
        # Delegate to utils: fetch account or raise 404
        account = get_account_by_number(db, account_number)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database lookup error: {e}"
        )
    
     # handle util returning None
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return BalanceOutput(
        account_number=account.account_number,
        balance=account.balance
    )

