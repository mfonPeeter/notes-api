import jwt

from app.config import settings
from app.auth.utils import get_password_hash, verify_password, create_access_token


def test_get_password_hash():
    hashed = get_password_hash("secret123")

    assert hashed != "secret123"
    assert hashed.startswith("$argon2")


def test_verify_password_correct():
    hashed = get_password_hash("secret123")
    verify_hashed = verify_password("secret123", hashed)

    assert verify_hashed


def test_verify_password_wrong():
    hashed = get_password_hash("secret123")
    verify_hashed = verify_password("secret12", hashed)

    assert not verify_hashed


def test_create_access_token():
    token = create_access_token(data={"sub": "mfon@test.com"})

    assert token is not None
    assert isinstance(token, str)

    # decode and verify the payload
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["sub"] == "mfon@test.com"
