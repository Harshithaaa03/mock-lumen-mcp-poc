"""Application configuration settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Todo List API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite+aiosqlite:///./todo.db"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
