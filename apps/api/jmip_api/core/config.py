from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application identity
    app_name: str = "jmip-api"
    env: str = "dev"  # dev | staging | prod
    log_level: str = "INFO"

    # Release metadata
    version: str = "0.1.0"
    commit: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="JMIP_",
        case_sensitive=False,
    )


settings = Settings()
