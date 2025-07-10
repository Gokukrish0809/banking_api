from pydantic import BaseModel


class LoginInput(BaseModel):
    """
    Pydantic schema for employee login credentials.

    Attributes:
        username (str): The employee’s username.
        password (str): The employee’s password.
    """

    username: str
    password: str


class Token(BaseModel):
    """
    Pydantic schema for an OAuth2 access token response.

    Attributes:
        access_token (str): The JWT or token string to be used for bearer authentication.
        token_type (str): The type of the token, typically 'bearer'.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
