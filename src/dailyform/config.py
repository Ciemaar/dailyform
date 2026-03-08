from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    toodledo_access_token: str | None = None
    owm_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Settings()
