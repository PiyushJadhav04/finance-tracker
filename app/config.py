from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    # separate DB so pytest runs never touch dev data; defaults to the same
    # server/credentials as database_url with "_test" appended to the name
    test_database_url: str = (
        "postgresql+asyncpg://finance_tracker:finance_tracker@localhost:5432/finance_tracker_test"
    )
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
