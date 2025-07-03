from fastapi import APIRouter, HTTPException, Depends
from db.schemas import Token
from utils.util import verify_password
from authentication.token import create_access_token
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from config import USERNAME, HASH_PASSWORD, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post('/')
def login(request : OAuth2PasswordRequestForm = Depends(),
    summary = "Authenticates the employee",
    description = "Retruns an access token. Only accessible to authenticated users",
    responses = {
        200 : {"Description " : "Successful response"},
        404 : {"Description " : "Invalid username or password"},
    }
    ):
    """
    Authenticates the users username and password and provides an access token
    """
    if request.username != USERNAME :
        raise HTTPException(status_code=404, detail="Invalid username")
    if not verify_password(request.password, HASH_PASSWORD) :
        raise HTTPException(status_code=404, detail="Invalid password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": request.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")