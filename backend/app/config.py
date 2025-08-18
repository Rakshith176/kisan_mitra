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
    # Updated Live API models based on Google documentation
    gemini_live_model: str = "gemini-live-2.5-flash-preview"  # Half-cascade for better tool support
    gemini_live_native_audio_model: str = "gemini-2.5-flash-preview-native-audio-dialog"  # Native audio for better speech
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
        
    # Agricultural data sources
    agmarknet_base_url: str = "https://agmarknet.gov.in/api/v1"
    
    # RAG configuration
    chroma_persist_directory: str = "./chroma_db"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Audio processing
    audio_sample_rate: int = 16000  # Input sample rate
    audio_output_sample_rate: int = 24000  # Output sample rate

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()


