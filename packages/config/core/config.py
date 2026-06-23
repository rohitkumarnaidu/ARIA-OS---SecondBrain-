from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    # Application
    app_name: str = "Second Brain OS"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    log_level: str = "INFO"

    # Supabase (Database + Auth)
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""

    # JWT Authentication
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    # AI / LLM Configuration
    use_local_ai: bool = True
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    ollama_timeout: int = 60
    claude_api_key: Optional[str] = None
    claude_model: str = "claude-sonnet-4-20250514"
    claude_timeout: int = 60

    # AI Resilience
    circuit_breaker_threshold: int = 5
    circuit_breaker_cooldown: int = 60

    # Rate Limiting
    rate_limit_max: int = 100
    rate_limit_window: int = 60

    # Email
    resend_api_key: Optional[str] = None

    # Monitoring
    sentry_dsn: Optional[str] = None
    posthog_api_key: Optional[str] = None

    # External APIs
    brave_api_key: Optional[str] = None


settings = Settings()
