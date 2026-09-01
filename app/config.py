# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
   
   DATABASE_URL: str

   SECRET_KEY: str

   ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

   REFRESH_TOKEN_EXPIRE_DAYS: int = 7

   REFRESH_COOKIE_NAME: str = "refresh_token"

   COOKIE_SECURE: bool = True

   model_config = SettingsConfigDict(env_file=".env")

settings = Settings()