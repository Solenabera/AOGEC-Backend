from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PORT: int = 8000
    MONGODB_URI: str
    DB_NAME: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
