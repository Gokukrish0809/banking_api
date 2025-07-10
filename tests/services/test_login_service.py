from app.services.login import hash_password, verify_password, verify_username

def test_verify_username_match():
    # exact match should return True
    assert verify_username("alice", "alice") is True


def test_verify_username_mismatch():
    # different strings → False
    assert verify_username("alice", "bob") is False


def test_hash_and_verify_password():
    plain = "SuperSecret!123"
    # hashing should not return the plain text
    hashed1 = hash_password(plain)
    assert hashed1 != plain

    # verify_password should accept the correct plain text
    assert verify_password(plain, hashed1) is True

    # hashing again yields a different hash (new salt)
    hashed2 = hash_password(plain)
    assert hashed2 != hashed1
    # but verify_password still succeeds
    assert verify_password(plain, hashed2) is True


def test_verify_password_wrong():
    plain = "MyPassw0rd"
    hashed = hash_password(plain)
    # verify_password should reject an incorrect password
    assert verify_password("NotMyPassword", hashed) is False
