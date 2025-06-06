from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    DATABASE_URL: str
    BOT_TOKEN: str
    SECRET_KEY: str
    ALGORITHM: str

def load_config(path: Path) -> Settings:
   conf = Settings(_env_file=path)
   return conf