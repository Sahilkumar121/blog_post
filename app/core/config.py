from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    DB_URL: str
    SECRETE_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTE: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


setting = Setting()  # type: ignore
