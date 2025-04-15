import os
from pydantic import BaseSettings, AnyUrl, RedisDsn

class Settings(BaseSettings):
    # Настройки приложения
    APP_PORT: int = 8001
    APP_HOST: str = "0.0.0.0"
    APP_DEBUG: bool = True
    
    # Настройки базы данных
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER", "taskmanager")
    DB_PASS: str = os.getenv("DB_PASS", "taskmanager")
    DB_NAME: str = os.getenv("DB_NAME", "taskmanager")
    DB_URL: str = f"mysql+asyncmy://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Настройки Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_URL: RedisDsn = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    
    # Настройки аутентификации
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "")
    
    class Config:
        env_file = ".env"

settings = Settings()