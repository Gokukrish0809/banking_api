from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from app.config import ALGORITHM, SECRET_KEY
from app.models.login import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """
    Extract and validate the current user's identity from a JWT bearer token.

    This dependency function will decode the JWT token, verify its signature,
    extract the "sub" claim (username), and return it. If the token is invalid,
    expired, or missing the "sub" claim, it raises a 401 Unauthorized HTTPException.

    Args:
        token (str): JWT access token provided by the OAuth2PasswordBearer dependency.

    Returns:
        str: The username extracted from the token's "sub" claim.

    Raises:
        HTTPException: With status code 401 if the token is invalid, expired, or
            missing the required "sub" claim.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    return username
