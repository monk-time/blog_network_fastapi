from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='yatube_',
        env_file='.env',
        env_file_encoding='utf-8',
    )
    db_user: str
    db_pass: str
    db_host: str
    db_port: int
    db_name: str
    secret: str


settings = Settings()  # type: ignore

BASE_DIR = Path(__file__).parent
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
