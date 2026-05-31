"""Database connection settings (override via environment variables)."""
import os
from pathlib import Path


def _load_env_file() -> None:
    """Load .env from project root if present (docker-compose credentials)."""
    root = Path(__file__).resolve().parents[3]
    env_path = root / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env_file()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv(
        "DB_NAME",
        os.getenv("DB_NAME_SECRET", os.getenv("POSTGRES_DB", "zoo_db")),
    ),
    "user": os.getenv("DB_USER", os.getenv("DB_USER_SECRET", os.getenv("POSTGRES_USER", "postgres"))),
    "password": os.getenv(
        "DB_PASSWORD",
        os.getenv("DB_PASSWORD_SECRET", os.getenv("POSTGRES_PASSWORD", "mysecretpassword")),
    ),
}
