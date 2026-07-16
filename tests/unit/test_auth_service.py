import pytest
from jose import JWTError

from app.services.auth import create_access_token, decode_access_token, hash_password, verify_password


def test_hash_password_does_not_store_plaintext():
    hashed = hash_password("supersecret123")
    assert hashed != "supersecret123"


def test_verify_password_accepts_correct_password():
    hashed = hash_password("supersecret123")
    assert verify_password("supersecret123", hashed) is True


def test_verify_password_rejects_incorrect_password():
    hashed = hash_password("supersecret123")
    assert verify_password("wrong-password", hashed) is False


def test_create_and_decode_access_token_roundtrip():
    token = create_access_token(subject="42")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"


def test_decode_access_token_rejects_tampered_token():
    token = create_access_token(subject="42")
    header, payload, signature = token.split(".")
    # flip a character in the middle of the payload segment, not the last
    # character of the whole token: base64url's final character can carry
    # unused padding bits, so mutating it doesn't reliably change the
    # decoded bytes and made this test flaky
    mid = len(payload) // 2
    flipped = "a" if payload[mid] != "a" else "b"
    tampered_payload = payload[:mid] + flipped + payload[mid + 1 :]
    tampered = f"{header}.{tampered_payload}.{signature}"
    with pytest.raises(JWTError):
        decode_access_token(tampered)


def test_decode_access_token_rejects_garbage_token():
    with pytest.raises(JWTError):
        decode_access_token("not-a-real-token")
