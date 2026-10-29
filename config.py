import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///cgpa.db")

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    RESET_TOKEN_EXPIRES = timedelta(minutes=15)

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 465))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")

    ACCESS_COOKIE_NAME = "access_token"
    REFRESH_COOKIE_NAME = "refresh_token"
    COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "0") == "1"
    COOKIE_SAMESITE = "Lax"

    @classmethod
    def validate(cls):
        missing = [n for n in ("SECRET_KEY", "JWT_SECRET_KEY") if not getattr(cls, n)]
        if missing:
            raise RuntimeError(f"Missing required env var(s): {', '.join(missing)}")