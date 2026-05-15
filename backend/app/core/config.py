import os
import urllib.parse
from pydantic_settings import BaseSettings


def _build_mssql_url(server: str, port: int, database: str, user: str, password: str) -> str:
    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes"
    )
    return f"mssql+aioodbc:///?odbc_connect={params}"


def _build_mssql_sync_url(server: str, port: int, database: str, user: str, password: str) -> str:
    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes"
    )
    return f"mssql+pyodbc:///?odbc_connect={params}"


class Settings(BaseSettings):
    db_server: str = "localhost"
    db_port: int = 1433
    db_name: str = "login_db"
    db_user: str = "sa"
    db_password: str = "123"
    database_url: str | None = None

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return _build_mssql_url(
            self.db_server,
            self.db_port,
            self.db_name,
            self.db_user,
            self.db_password,
        )

    @property
    def sqlalchemy_database_sync_url(self) -> str:
        """Synchronous URL for Alembic migrations"""
        return _build_mssql_sync_url(
            self.db_server,
            self.db_port,
            self.db_name,
            self.db_user,
            self.db_password,
        )


settings = Settings()
