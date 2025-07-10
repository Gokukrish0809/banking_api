from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

import app.services.login as login_service
from app.authentication.token import create_access_token
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, HASH_PASSWORD, USERNAME
from app.models.login import Token

router = APIRouter()


@router.post(
    "/",
    summary="Authenticate user and retrieve access token",
    description=(
        "Validates the provided username and password. "
        "On success, returns a JWT bearer token to be used for authenticated requests."
    ),
    responses={
        200: {"description": "Authentication successful"},
        403: {"description": "Invalid username or password"},
        422: {"description": "Missing or invalid form data"},
    },
)
def login(request: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    Authenticates the users username and password and provides an access token.
    """
    if not login_service.verify_username(request.username, USERNAME):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username")

    if not login_service.verify_password(request.password, HASH_PASSWORD):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": request.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")
