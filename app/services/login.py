from passlib.context import CryptContext


def verify_username(username_inp: str, username_correct) -> bool:
    """
    Check whether the provided username matches the expected username.

    Args:
        username_inp (str): The username supplied by the user.
        username_correct (str): The valid username to compare against.

    Returns:
        bool: True if the usernames are identical, False otherwise.
    """
    if username_inp == username_correct:
        return True

    return False


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        plain_password (str): The plaintext password to hash.

    Returns:
        str: The bcrypt-hashed password string, including salt.
    """
    pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

    return pwd_cxt.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.

    Args:
        plain_password (str): The password provided by the user.
        hashed_password (str): The bcrypt-hashed password from storage.

    Returns:
        bool: True if the plaintext password matches the hash, False otherwise.
    """
    pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

    return pwd_cxt.verify(plain_password, hashed_password)
