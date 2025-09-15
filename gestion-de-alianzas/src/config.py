# publicaciones_app/src/config.py
import os
from functools import lru_cache


class Settings:
    """Application settings."""

    @classmethod
    @lru_cache()
    def app_name(cls) -> str:
        return os.getenv("APP_NAME", "Gestion de alianzas app")

    @classmethod
    @lru_cache()
    def log_level(cls) -> str:
        return os.getenv("LOG_LEVEL", "DEBUG")