from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from decimal import Decimal

class CustomerInput(BaseModel):
    """
    To get the input from the customer details as input
    """
    name : str
    email : EmailStr
    initial_deposit: Decimal = Field(..., gt=0)
    
class AccountOutput(BaseModel):
    """
    To display the details of the account created
    """
    account_number: int
    balance: Decimal = Field(..., gt=0)
    customer_id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True    

class TransferInput(BaseModel):
    """
    To get the account details to make the transaction
    """
    from_account_number: int
    to_account_number: int
    amount: Decimal = Field(..., gt=0)

class TransferOutput(BaseModel):
    """
    To display the output of the transfer details
    """
    from_account_number: int
    to_account_number: int
    amount: Decimal = Field(..., gt=0)
    timestamp: datetime

    class Config:
        orm_mode = True

class BalanceOutput(BaseModel):
    """
    To display the balance of the customer
    """
    account_number: int
    balance:  Decimal = Field(..., gt=0)

    class Config:
        orm_mode = True

class LoginInput(BaseModel):
    """
    Login credentials of the employee
    """
    username : str
    password : str

class Token(BaseModel):
    """
    Token details
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None