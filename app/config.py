from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB
    DATABASE_URL: str
    DATABASE_URL_ASYNC: str
    # JWT
    JWT_KEY: str

    # URL

    # AI
    HUGGINGFACEHUB_API_TOKEN: str
    GROQ_API_KEY: str

    # google
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
