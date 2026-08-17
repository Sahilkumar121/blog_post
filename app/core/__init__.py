from .config import Setting
from .security import create_hash_password

setting = Setting()  # type: ignore

__all__ = ["create_hash_password"]
