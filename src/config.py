from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CRM Message Generator"
    app_version: str = "0.1.0"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    api_prefix: str = "/api/v1"
    docs_url: str = "/docs"

    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env_example",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# 전역 설정 인스턴스
settings = Settings()
