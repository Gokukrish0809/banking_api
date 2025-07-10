from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services import accounts as accounts_service
from app.authentication.oauth import get_current_user
from app.database import get_db
from app.exceptions import AccountNotFoundError
from app.models.accounts import AccountOutput, BalanceOutput, CustomerInput

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=AccountOutput,
    summary="Create an account",
    responses={
        201: {
            "description": "Account created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "account_number": 1234,
                        "balance": "250.00",
                        "customer_id": 99,
                        "name": "Alice Wonderland",
                        "email": "alice@example.com",
                    }
                }
            },
        },
        500: {"description": "Internal server error"},
    },
)
def create_account(
    customer: CustomerInput,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> AccountOutput:
    """
    Create an account for a customer.
    """
    try:
        customer_db = accounts_service.create_customer(db, customer)
        new_account = accounts_service.create_account_for_customer(
            db, customer_db, customer.initial_deposit
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")

    return AccountOutput(
        account_number=new_account.account_number,
        balance=new_account.balance,
        customer_id=customer_db.customer_id,
        name=customer_db.name,
        email=customer_db.email,
    )


@router.get(
    "/{account_number}/balance",
    response_model=BalanceOutput,
    summary="Retrieve account balance",
    description="Returns the current balance for the given account number. Only accessible to authenticated users.",
    responses={
        200: {
            "description": "Balance retrieved successfully",
            "content": {
                "application/json": {
                    "example": {"account_number": 1234, "balance": "100.00"}
                }
            },
        },
        404: {"description": "Account not found"},
        500: {"description": "Internal server error"},
    },
)
def get_balance(
    account_number: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> BalanceOutput:
    """
    Get the balance of an account.
    """
    try:
        account = accounts_service.get_account_by_number(db, account_number)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")

    return BalanceOutput(account_number=account.account_number, balance=account.balance)
