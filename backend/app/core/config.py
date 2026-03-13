import os


class Settings:
    database_url: str | None = os.getenv("FPI_DATABASE_URL")
    use_csv_fallback: bool = os.getenv("FPI_USE_CSV_FALLBACK", "false").lower() == "true"


settings = Settings()
