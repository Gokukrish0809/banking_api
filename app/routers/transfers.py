from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import app.services.transfers as transfer_service
from app.authentication.oauth import get_current_user
from app.database import get_db
from app.exceptions import (AccountNotFoundError, InsufficientFundsError,
                            SameAccountError)
from app.models.transfers import Transfer, TransferInput, TransferOutput

router = APIRouter()


@router.post(
    "/",
    response_model=TransferOutput,
    summary="Transfer funds between accounts",
    description="Moves the specified amount from one account to another. Authentication required.",
    responses={
        200: {"Description ": "Successful response"},
        400: {
            "Description ": "Can not transfer to the same account or insufficient funds"
        },
        404: {"Description ": "Account not found"},
        500: {"Description ": "Internal server error"},
    },
)
def transfer_funds(
    transfer: TransferInput,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> TransferOutput:
    """
    Transfer funds between accounts.
    """
    try:
        from_acc = transfer.from_account_number
        to_acc = transfer.to_account_number
        record = transfer_service.perform_transfer(
            db, from_acc, to_acc, transfer.amount
        )
    except SameAccountError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientFundsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error : {e}")

    return TransferOutput(
        from_account_number=from_acc,
        to_account_number=to_acc,
        amount=record.amount,
        timestamp=record.timestamp,
    )


@router.get(
    "/{account_number}/transfer_history",
    response_model=List[TransferOutput],
    summary="Get account transfer history",
    description="Returns all transfers to and from the given account, most recent first. Authentication required.",
    responses={
        200: {"Description ": "Successful response"},
        500: {"Description ": "Internal server error"},
    }
)
def get_transfer_history(
    account_number: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> list[Transfer]:
    """
    Get the transfer history of an account.
    """
    try:
        history = transfer_service.get_transfer_history_for_account(db, account_number)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

    return history
