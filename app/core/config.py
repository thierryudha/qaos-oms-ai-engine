from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # variabel GEMINI_API_KEY wajib ada di .env
    GEMINI_API_KEY: str

    GEMINI_PRIMARY_MODEL: str = "gemini-3.8-flash"
    GEMINI_FALLBACK_MODEL: str = "gemini-3.5-flash-lite"
    GEMINI_FALLBACK_MODEL_2: str = "gemini-3.1-flash-lite"
    ALLOWED_ORIGINS: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # abaikan env var lain di .env yang belum didaftarkan di sini
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
settings = Settings()