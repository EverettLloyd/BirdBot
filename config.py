try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_CHAT_ID: int
    ADMIN_TOPIC_ID: int | None = None  # ID топика форума (опционально)
    CARE_ADMIN_CONTACT: str | None = None  # например, "@bird_admin"

    class Config:
        env_file = ".env"

settings = Settings()
