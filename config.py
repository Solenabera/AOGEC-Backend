from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PORT: int = 8000

    # MONGODB_URI: str = "mongodb+srv://solenabera55_db_user:r2042uOqq0ca4hWu@cluster0.5pzi4qv.mongodb.net/aogec?retryWrites=true&w=majority"
    MONGODB_URI: str = "mongodb://localhost:27017"
    
    DB_NAME: str = "AOGEC"

    SECRET_KEY: str = "333b343063623434633766616332313536656564313934363736393664"

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3-flash-preview"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()