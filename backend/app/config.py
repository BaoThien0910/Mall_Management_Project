from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "TTTM Mall API"
    # SQLite dev default; MSSQL sample:
    # mssql+pyodbc://USER:PWD@HOST/DB?driver=ODBC+Driver+17+for+SQL+Server
    DATABASE_URL: str = "sqlite:///./mall_dev.db"

    JWT_SECRET_KEY: str = "dev-secret-change-in-production-use-openssl-rand"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # 0–1: xác suất thanh toán mô phỏng THẤT BẠI (0 = luôn thành công)
    PAYMENT_SIM_FAIL_RATE: float = 0.0


@lru_cache
def get_settings() -> Settings:
    return Settings()


RoleCode = Literal["admin", "tenant", "staff", "management"]
