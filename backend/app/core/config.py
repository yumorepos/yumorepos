import os
from pathlib import Path


def _load_local_env_file() -> None:
    """Load backend/.env values for local development without external deps."""
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue

        cleaned = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, cleaned)


_load_local_env_file()


class Settings:
    database_url: str | None = os.getenv("FPI_DATABASE_URL") or os.getenv("DATABASE_URL")
    use_csv_fallback: bool = os.getenv("FPI_USE_CSV_FALLBACK", "false").lower() == "true"


settings = Settings()
