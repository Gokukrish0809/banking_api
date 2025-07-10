from datetime import datetime, timedelta, timezone
import jwt
import pytest
from fastapi import HTTPException, status

from app.authentication.oauth import get_current_user
from app.authentication.token import create_access_token
from app.config import ALGORITHM, SECRET_KEY


def test_create_access_token_default_expiry():
    data = {"sub": "alice"}
    token = create_access_token(data)
    # decode to inspect payload
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "alice"

    exp_ts = payload["exp"]
    now_ts = int(datetime.now(timezone.utc).timestamp())
    # default is 15 minutes (900 seconds)
    assert 895 <= exp_ts - now_ts <= 905  # within ~seconds tolerance


def test_create_access_token_custom_expiry():
    data = {"sub": "bob"}
    delta = timedelta(minutes=5)
    token = create_access_token(data, expires_delta=delta)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "bob"

    exp_ts = payload["exp"]
    now_ts = int(datetime.now(timezone.utc).timestamp())
    # custom is 5 minutes (300 seconds)
    assert 295 <= exp_ts - now_ts <= 305


def test_get_current_user_success():
    # use the same token generator
    token = create_access_token({"sub": "carol"}, expires_delta=timedelta(minutes=1))
    username = get_current_user(token)
    assert username == "carol"


def test_get_current_user_missing_sub():
    # create a token without "sub"
    payload = {"foo": "bar", "exp": datetime.now(timezone.utc) + timedelta(minutes=1)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exc:
        get_current_user(token)
    
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "could not validate credentials" in exc.value.detail.lower()


def test_get_current_user_invalid_token():
    bad = "not.a.valid.token"

    with pytest.raises(HTTPException) as exc:
        get_current_user(bad)
    
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "could not validate credentials" in exc.value.detail.lower()
