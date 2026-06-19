from app.core.security import hash_password, verify_password, create_access_token
from datetime import datetime, timezone, timedelta
from app.config import settings
import jwt

def test_hash_is_not_equal_password():
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert hashed != password

def test_two_hash_of_one_password_are_different():
    password = "password"
    hashed1 = hash_password(password)
    hashed2 = hash_password(password)
    assert hashed1 != hashed2

def test_verify_good_password():
    password = "password"
    hashed = hash_password(password)
    assert verify_password(password, hashed)

def test_verify_bad_password():
    password = "password"
    hashed = hash_password(password)
    bad_password = "bad_password"
    assert not verify_password(bad_password, hashed)

def test_decode_token_has_good_sub():
    data = {"sub": "user_id"}
    token = create_access_token(data)
    decode_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert data["sub"] == decode_token["sub"]

def test_token_time_is_60_mins():
    data = {"sub": "user_id"}
    token = create_access_token(data)
    decode_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    exp = datetime.fromtimestamp(decode_token["exp"], tz=timezone.utc)
    diff = exp - datetime.now(timezone.utc)
    assert timedelta(minutes=59) < diff < timedelta(minutes=61)

def test_expires_delta_is_working():
    data = {"sub": "user_id"}
    expires_delta = timedelta(minutes=33)
    token = create_access_token(data, expires_delta)
    decode_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    exp = datetime.fromtimestamp(decode_token["exp"], tz=timezone.utc)
    diff = exp - datetime.now(timezone.utc)
    assert timedelta(minutes=32) < diff < timedelta(minutes=34)

# Запустить тесты:
# poetry run pytest tests/unit/ -v