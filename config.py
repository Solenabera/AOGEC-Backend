from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PORT: int = 8000

    # Required from .env
    MONGODB_URI: str
    DB_NAME: str = "AOGEC"
    SECRET_KEY: str

    # External APIs & models
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3-flash-preview"
    HF_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()