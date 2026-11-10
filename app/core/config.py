
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database Credentials
    drivername: str
    database: str
    host: str
    port: int
    uname: str
    password: str

    # JWT Credentials
    secret_key: str
    algorithm: str
    login_expiry_min: int

    # Ollama Configuration
    OLLAMA_MODEL: str
    OLLAMA_BASE_URL: str

    # Groq Configuration
    GROQ_API_KEY: SecretStr | None = None
    GROQ_MODEL: str

    # AI Configuration
    AI_PLATFORM: str
    AI_ENABLE_FOLLOWUP: bool
    AI_FOLLOWUP_LIMIT: int


config = Config()
