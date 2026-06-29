from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-haiku-4-5"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    ADMIN_TOKEN: str

    class Config:
        env_file = ".env"


settings = Settings()