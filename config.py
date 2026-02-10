from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PORT: int = 8000
    MONGODB_URI: str
    DB_NAME: str
    SECRET_KEY: str
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3-flash-preview"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
