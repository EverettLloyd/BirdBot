try:
    from pydantic_settings import BaseSettings
except ImportError:  # fallback for Pydantic v1
    from pydantic import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    ADMIN_CHAT_ID: int
    PUBLICATION_CHANNEL_ID: int

    class Config:
        env_file = '.env'

settings = Settings()
