from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash
from pydantic import SecretStr

from app.core.config import setting

password_hash = PasswordHash.recommended()


def create_hash_password(plain_password: SecretStr) -> str:
    return password_hash.hash(plain_password.get_secret_value())


def verify_hash_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_token(data: dict, expire_delta: timedelta | None):
    to_encode = data.copy()
    if expire_delta:
        expire_date = datetime.now(UTC) + expire_delta
    else:
        expire_date = datetime.now(UTC) + timedelta(
            minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTE
        )

    to_encode.update({"exp": expire_date})

    encode_jwt = jwt.encode(to_encode, setting.SECRETE_KEY, algorithm=setting.ALGORITHM)

    return encode_jwt
