"""Application configuration.

All deployment-specific values come from the environment (see ``.env.example``).
Secrets (provider keys, signing material) are only ever *referenced* here; raw
secret values are read from the environment, never persisted to MongoDB.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Runtime ---
    environment: str = Field(default="development", alias="VT_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=5206, alias="APP_PORT")

    # --- Database ---
    mongodb_uri: str = Field(
        default="mongodb://127.0.0.1:27017/?replicaSet=rs0",
        alias="MONGODB_URI",
    )
    mongodb_database: str = Field(default="swissspeak", alias="MONGODB_DATABASE")

    # --- Public URLs / CORS ---
    public_web_base_url: str = Field(
        default="http://localhost:5306", alias="PUBLIC_WEB_BASE_URL"
    )
    public_api_base_url: str = Field(
        default="http://localhost:5206", alias="PUBLIC_API_BASE_URL"
    )
    allowed_origins_raw: str = Field(
        default="http://localhost:5306,http://127.0.0.1:5306",
        alias="ALLOWED_ORIGINS",
    )
    # Allow-listed relative frontend paths magic links may return to.
    allowed_return_paths_raw: str = Field(
        default="/auth/callback", alias="ALLOWED_RETURN_PATHS"
    )

    # --- Auth / cookies ---
    cookie_secure: bool = Field(default=False, alias="COOKIE_SECURE")
    cookie_domain: str = Field(default="", alias="COOKIE_DOMAIN")
    session_cookie_name: str = Field(default="ss_session", alias="SESSION_COOKIE_NAME")
    refresh_cookie_name: str = Field(default="ss_refresh", alias="REFRESH_COOKIE_NAME")
    csrf_cookie_name: str = Field(default="ss_csrf", alias="CSRF_COOKIE_NAME")
    access_ttl_seconds: int = Field(default=15 * 60, alias="ACCESS_TTL_SECONDS")
    refresh_ttl_seconds: int = Field(default=30 * 24 * 3600, alias="REFRESH_TTL_SECONDS")
    magic_link_ttl_seconds: int = Field(default=15 * 60, alias="MAGIC_LINK_TTL_SECONDS")
    recent_auth_window_seconds: int = Field(
        default=10 * 60, alias="RECENT_AUTH_WINDOW_SECONDS"
    )

    # --- Email adapter ---
    # "console" writes the magic link to the log (development). "smtp" / provider
    # adapters are wired when EMAIL_PROVIDER + secret references are supplied.
    email_provider: str = Field(default="console", alias="EMAIL_PROVIDER")
    email_from: str = Field(default="SwissSpeak <no-reply@localhost>", alias="EMAIL_FROM")

    # --- AI / audio providers ---
    # "fake" uses a deterministic in-process provider (no external cost); used for
    # local dev and tests. Real routes resolve through versioned app_config.
    speech_provider: str = Field(default="fake", alias="SPEECH_PROVIDER")
    ai_text_provider: str = Field(default="fake", alias="AI_TEXT_PROVIDER")
    openai_apikey: str = Field(default="", alias="OPENAI_APIKEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    google_genai_apikey: str = Field(default="", alias="GOOGLE_GENAI_APIKEY")

    # --- Budget / limits (operational defaults, editable via app_config) ---
    audio_daily_global_cap_microunits: int = Field(
        default=5_000_000, alias="AUDIO_DAILY_GLOBAL_CAP_MICROUNITS"
    )

    @property
    def allowed_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins_raw.split(",") if o.strip()]

    @property
    def allowed_return_paths(self) -> List[str]:
        return [
            p.strip() for p in self.allowed_return_paths_raw.split(",") if p.strip()
        ]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ("production", "prod")


@lru_cache
def get_settings() -> Settings:
    return Settings()
