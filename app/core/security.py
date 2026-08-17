from pwdlib import PasswordHash
from pydantic import SecretStr

password_hash = PasswordHash.recommended()


def create_hash_password(plain_password: SecretStr) -> str:
    return password_hash.hash(plain_password.get_secret_value())


def verify_hash_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)
