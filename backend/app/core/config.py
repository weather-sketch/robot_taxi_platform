from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Robotaxi Feedback Platform"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./robotaxi.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # AI / LLM
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # SLA defaults (in minutes)
    SLA_P0_RESPONSE: int = 60
    SLA_P0_RESOLVE: int = 240
    SLA_P1_RESPONSE: int = 60
    SLA_P1_RESOLVE: int = 1440
    SLA_P2_RESPONSE: int = 240
    SLA_P2_RESOLVE: int = 4320
    SLA_P3_RESPONSE: int = 1440
    SLA_P3_RESOLVE: int = 10080

    # SLA warning threshold (percentage of time remaining)
    SLA_WARNING_THRESHOLD: float = 0.25

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
