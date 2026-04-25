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
    image_api_url: str = Field(default="", alias="IMAGE_API_URL")
    image_api_key: str = Field(default="", alias="IMAGE_API_KEY")
    rag_api_url: str = Field(default="", alias="RAG_API_URL")
    rag_api_key: str = Field(default="", alias="RAG_API_KEY")
    media_root: str = Field(default="storage", alias="MEDIA_ROOT")
    provider_timeout_seconds: int = Field(default=90, alias="PROVIDER_TIMEOUT_SECONDS")
    visual_style_rules: str = Field(
        default=(
            "balance, functional zoning, coherent materials, realistic lighting, "
            "premium but livable interior decisions"
        ),
        alias="VISUAL_STYLE_RULES",
    )
    consultant_system_prompt_default: str = Field(
        default="Ты эксперт по интерьеру. Отвечай конкретно, прикладно и по шагам.",
        alias="CONSULTANT_SYSTEM_PROMPT_DEFAULT",
    )
    personality_formula_path: str = Field(
        default="data/personality_formula.json", alias="PERSONALITY_FORMULA_PATH"
    )


settings = Settings()
