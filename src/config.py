from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# 프로젝트 루트의 .env 파일 로드
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    app_name: str = "CRM Message Generator"
    app_version: str = "0.1.0"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    api_prefix: str = "/api/v1"
    docs_url: str = "/docs"

    # Database Settings
    rds_db_path: str = "database/rds.db"
    vector_db_path: str = "database/vector.db"

    # AI Model Settings
    google_api_key: str | None = None
    embedding_model: str = "text-embedding-004"  # 768 dimensions

    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# 전역 설정 인스턴스
settings = Settings()
