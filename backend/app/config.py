import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    log_level: str = "info"

    database_url: str = "sqlite+aiosqlite:///./data/app.db"

    google_api_key: str | None = os.getenv("google_api_key")
    gemini_model: str = "gemini-2.5-flash"
    gemini_live_model: str = "gemini-2.0-flash-live-001"  # Official Live API model (without models/ prefix)
    live_audio_sample_rate_hz: int = 16000

    # Tavily API for web search capabilities
    tavily_api_key: str | None = None

    # Weather providers
    # Open-Meteo does not require an API key, but allow configuration for enterprise/self-hosted gateways
    open_meteo_api_key: str | None = None

    # Market prices (Agmarknet via data.gov.in)
    data_gov_in_api_key: str | None = os.getenv("data_gov_in_api_key")
    agmarknet_resource_id: str | None = os.getenv("agmarknet_resource_id")
    agmarknet_base_url: str = "https://api.data.gov.in/resource/"
    tavily_api_key: str | None = os.getenv("tavily_api_key")

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()


