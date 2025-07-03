from fastapi import Depends, HTTPException, APIRouter
from typing import List
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Account
from db.schemas import TransferInput, TransferOutput, LoginInput
from utils.util import (
    get_account_by_number,
    perform_transfer,
    get_transfer_history_for_account
)
from config import USERNAME
from authentication.oauth import get_current_user

router = APIRouter()

# Endpoint: transfer between accounts
@router.post("/", response_model=TransferOutput)
def transfer_funds(
    transfer: TransferInput,
    db: Session = Depends(get_db),
    get_current_user : str = Depends(get_current_user),
    summary = "To transfer funds between accounts",
    description = "Retruns the details of the transfer. Only accessible to authenticated users",
    responses = {
        200 : {"Description " : "Successful response"},
        400 : {"Description " : "Can not transfer to the same account or insufficient funds"},
        404 : {"Description " : "Account not found"},
        500 : {"Description " : "Transfer failed"},
    }
):
    """
    To transfer funds
    """
    # Fetch and validate accounts
    from_acc = get_account_by_number(db, transfer.from_account_number)
    to_acc   = get_account_by_number(db, transfer.to_account_number)

    if from_acc == to_acc :
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")
    if from_acc.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds in source account")

    # Delegate transfer logic to utils
    try:
        record = perform_transfer(db, from_acc, to_acc, transfer.amount)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer failed: {e}")

    return TransferOutput(
        from_account_number=from_acc.account_number,
        to_account_number=to_acc.account_number,
        amount=record.amount,
        timestamp=record.timestamp
    )


# Endpoint: get transfer history for an account
@router.get("/{account_number}/transfer_history", response_model=List[TransferOutput])
def get_transfer_history(
    account_number: int,
    db: Session = Depends(get_db),
    get_current_user : str = Depends(get_current_user),
    summary = "To retrieve the tranfer history of an account",
    description = "Retruns the details of the transfer history. Only accessible to authenticated users",
    responses = {
        200 : {"Description " : "Successful response"},
        400 : {"Description " : "Account number does not exist"},
        500 : {"Description " : "Could not fetch history"},
    }
):
    """
    To get the transfer history of an account
    """
    acc_num = db.query(Account).filter(Account.account_number == account_number).first()
    if not acc_num :
        raise HTTPException(status_code=400, detail="Account number does not exist")
    
    try:
        history = get_transfer_history_for_account(db, account_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch history: {e}")
    return history
