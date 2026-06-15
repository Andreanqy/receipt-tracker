from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Receipt Tracker"
    DEBUG: bool = False

    # Postgres
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # MinIO
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_ENDPOINT: str
    MINIO_BUCKET_NAME: str

    @property
    def MINIO_ACCESS_KEY(self) -> str:
        return self.MINIO_ROOT_USER

    @property
    def MINIO_SECRET_KEY(self) -> str:
        return self.MINIO_ROOT_PASSWORD

    # Env
    SECRET_KEY: str

    # External API (proverkacheka.com)
    PROVERKACHEKA_TOKEN: str

    # Anthropic
    ANTHROPIC_API_KEY: str

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
