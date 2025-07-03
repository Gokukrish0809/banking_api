import pytest
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone

import config
import authentication.oauth as oauth_module
import authentication.token as token_module
from authentication.oauth import get_current_user
from authentication.token import create_access_token

@pytest.fixture(autouse=True)
def patch_config(monkeypatch):
    # Patch config module
    monkeypatch.setattr(config, "SECRET_KEY", "testsecret")
    monkeypatch.setattr(config, "ALGORITHM", "HS256")
    # Patch values inside oauth module
    monkeypatch.setattr(oauth_module, "SECRET_KEY", "testsecret")
    monkeypatch.setattr(oauth_module, "ALGORITHM", "HS256")
    # Patch values inside token module
    monkeypatch.setattr(token_module, "SECRET_KEY", "testsecret")
    monkeypatch.setattr(token_module, "ALGORITHM", "HS256")


def test_get_current_user_valid_token():
    # Create a valid token with 'sub' claim
    token = jwt.encode({"sub": "alice"}, config.SECRET_KEY, algorithm=config.ALGORITHM)
    user = get_current_user(token)
    assert user == "alice"


def test_get_current_user_missing_sub_claim():
    # Token without 'sub' should raise 401
    token = jwt.encode({"data": "nogood"}, config.SECRET_KEY, algorithm=config.ALGORITHM)
    with pytest.raises(HTTPException) as exc:
        get_current_user(token)
    assert exc.value.status_code == 401


def test_get_current_user_invalid_token_string():
    with pytest.raises(HTTPException) as exc:
        get_current_user("not.a.valid.token")
    assert exc.value.status_code == 401


def test_create_access_token_includes_sub_and_expiry_custom():
    # Custom expiry
    delta = timedelta(minutes=5)
    token = create_access_token({"sub": "bob"}, expires_delta=delta)
    # Decode without verifying exp
    payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM], options={"verify_exp": False})
    assert payload.get("sub") == "bob"
    exp_ts = payload.get("exp")
    now_ts = datetime.now(timezone.utc).timestamp()
    assert exp_ts > now_ts
    # Should be roughly now + 5 min
    assert exp_ts < now_ts + 5*60 + 5


def test_create_access_token_default_expiry():
    # Default expiry: 15 minutes
    token = create_access_token({"sub": "carol"}, expires_delta=None)
    payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM], options={"verify_exp": False})
    assert payload.get("sub") == "carol"
    exp_ts = payload.get("exp")
    now_ts = datetime.now(timezone.utc).timestamp()
    # Should be at least now + 14 minutes
    assert exp_ts > now_ts + 14*60
