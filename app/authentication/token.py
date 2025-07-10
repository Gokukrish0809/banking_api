from datetime import datetime, timedelta, timezone
import jwt

from app.config import ALGORITHM, SECRET_KEY


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JSON Web Token (JWT) that encodes the given data payload,
    with an expiration time.

    Args:
        data (dict): A dictionary of claims to include in the token payload.
        expires_delta (timedelta | None): Optional time duration after which
            the token should expire. If None, defaults to 15 minutes.

    Returns:
        str: The encoded JWT as a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
