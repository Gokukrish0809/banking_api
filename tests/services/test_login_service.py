from app.services.login import hash_password, verify_password, verify_username

def test_verify_username_match():
    assert verify_username("alice", "alice") is True


def test_verify_username_mismatch():
    assert verify_username("alice", "bob") is False


def test_hash_and_verify_password():
    plain = "SuperSecret!123"
    hashed1 = hash_password(plain)

    assert hashed1 != plain
    assert verify_password(plain, hashed1) is True

    hashed2 = hash_password(plain)
    assert hashed2 != hashed1
    assert verify_password(plain, hashed2) is True


def test_verify_password_wrong():
    plain = "MyPassw0rd"
    hashed = hash_password(plain)
    assert verify_password("NotMyPassword", hashed) is False
