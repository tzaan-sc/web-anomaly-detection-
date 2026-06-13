import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"

# Đọc biến môi trường từ file .env ở thư mục gốc project.
# Dòng này phải nằm trước class Config.
load_dotenv(BASE_DIR / ".env")

DEFAULT_SQLITE_URI = (
    f"sqlite:///{(INSTANCE_DIR / 'app.db').as_posix()}"
)


class Config:
    """Shared configuration."""

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-only-change-this-secret",
    )

    # Có DATABASE_URL thì dùng MySQL.
    # Không có DATABASE_URL thì mới quay về SQLite.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        DEFAULT_SQLITE_URI,
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    MAX_CONTENT_LENGTH = 20 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        "pdf",
        "doc",
        "docx",
        "xls",
        "xlsx",
        "ppt",
        "pptx",
        "txt",
        "csv",
        "png",
        "jpg",
        "jpeg",
        "zip",
    }

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    UPLOAD_FOLDER = str(INSTANCE_DIR / "uploads")


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "testing-secret"

    # Pytest vẫn dùng SQLite tạm thời, không ảnh hưởng MySQL thật.
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}