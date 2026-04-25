from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    telegram_token: str = Field(default="", alias="TELEGRAM_TOKEN")
    database_url: str = Field(default="sqlite:///./interior_bot.db", alias="DATABASE_URL")
    admin_api_key: str = Field(default="dev-admin-key", alias="ADMIN_API_KEY")

    # External integrations placeholders.
    getcourse_api_url: str = Field(default="", alias="GETCOURSE_API_URL")
    getcourse_api_token: str = Field(default="", alias="GETCOURSE_API_TOKEN")
    llm_api_url: str = Field(default="", alias="LLM_API_URL")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")


settings = Settings()
