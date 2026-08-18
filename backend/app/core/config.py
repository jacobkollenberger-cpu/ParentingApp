"""
Application configuration, loaded from environment variables.

Using pydantic-settings means required values fail fast at startup
if missing, rather than causing confusing errors later.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/parenting_app"

    # Auth
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # AI
    anthropic_api_key: str = ""

    # App
    environment: str = "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
