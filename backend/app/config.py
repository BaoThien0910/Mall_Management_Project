# File: app/config.py
from typing import Any, List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cấu hình tập trung của backend, lấy dữ liệu từ biến môi trường và file .env."""

    APP_NAME: str = "Trung Tam Thuong Mai API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str
    SQLALCHEMY_ECHO: bool = False

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    CORS_ALLOWED_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
        ]
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: List[str] = Field(default_factory=lambda: ["*"])

    PAYMENT_SIMULATION_ENABLED: bool = True

    AUDIT_SECURITY_EVENTS: bool = True
    TRUST_X_FORWARDED_FOR: bool = True

    @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_allowed_origins(cls, value: Any) -> Any:
        """Hỗ trợ CORS origins dạng JSON list hoặc chuỗi phân tách bởi dấu phẩy."""
        if isinstance(value, str):
            stripped_value = value.strip()
            if stripped_value.startswith("["):
                return stripped_value

            return [
                origin.strip()
                for origin in stripped_value.split(",")
                if origin.strip()
            ]

        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
