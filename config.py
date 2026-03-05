import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Settings:
    APP_NAME: str = "AcademiaLMS"
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "super-secret-dev-key-change-in-production-xyz")
    DEBUG: bool = os.environ.get("DEBUG", "true").lower() == "true"

    # Database — SQLite by default, swap DATABASE_URL env var for Postgres etc.
    DATABASE_URL: str = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR}/lms.db")

    # Session cookie
    SESSION_COOKIE_NAME: str = "lms_session"
    SESSION_MAX_AGE: int = 60 * 60 * 8  # 8 hours

    # File uploads
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    ALLOWED_EXTENSIONS: set = {"pdf", "jpg", "jpeg", "png", "doc", "docx", "xls", "xlsx"}
    MAX_UPLOAD_BYTES: int = 50 * 1024 * 1024  # 50 MB

    # Rate limiting
    LOGIN_RATE_LIMIT: str = "10/minute"


settings = Settings()
