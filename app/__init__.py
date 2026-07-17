import os

import click
from dotenv import load_dotenv
from flask import Flask, g, request, session

from app.config import CONFIG_BY_NAME
from app.extensions import csrf, db


def create_app(config_name: str | None = None) -> Flask:
    """Application factory used by development, testing, and production."""
    load_dotenv()

    env_name = config_name or os.getenv("APP_ENV", "development")
    config_class = CONFIG_BY_NAME.get(env_name)

    if config_class is None:
        valid_names = ", ".join(CONFIG_BY_NAME)
        raise ValueError(
            f"APP_ENV='{env_name}' không hợp lệ. Giá trị hợp lệ: {valid_names}."
        )

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    register_extensions(app)
    register_logging_middleware(app)
    register_request_hooks(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_cli_commands(app)

    return app


def register_extensions(app: Flask) -> None:
    """Attach Flask extensions to the current app instance."""
    db.init_app(app)
    csrf.init_app(app)

def register_logging_middleware(app: Flask) -> None:
    """Attach structured request logging hooks."""
    from app.middleware.request_logging import register_request_logging

    register_request_logging(app)

def register_request_hooks(app: Flask) -> None:
    """Load logged-in user and prevent caching protected HTML pages."""

    @app.before_request
    def load_logged_in_user() -> None:
        from app.models import User

        user_id = session.get("user_id")
        g.current_user = None

        if user_id is None:
            return

        user = db.session.get(User, user_id)

        # Session không hợp lệ hoặc tài khoản đã bị khóa.
        if user is None or not user.is_active:
            session.clear()
            return

        g.current_user = user

    from app.middleware.active_defense import check_active_defense
    app.before_request(check_active_defense)

    @app.after_request
    def prevent_html_cache(response):
        # Tránh browser hiển thị lại dashboard sau khi logout bằng nút Back.
        if response.content_type and response.content_type.startswith("text/html"):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0"
            )
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response

    @app.context_processor
    def inject_current_user():
        return {
            "current_user": g.get("current_user"),
        }

def register_blueprints(app: Flask) -> None:
    """Import blueprints locally to avoid circular imports."""
    from app.blueprints.admin import bp as admin_bp
    from app.blueprints.alerts import bp as alerts_bp
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.documents import bp as documents_bp
    from app.blueprints.main import bp as main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(documents_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(alerts_bp, url_prefix="/alerts")


def register_error_handlers(app: Flask) -> None:
    from app.errors import (
        forbidden,
        page_not_found,
        request_entity_too_large,
        server_error,
    )

    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(413, request_entity_too_large)
    app.register_error_handler(500, server_error)

def register_cli_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db() -> None:
        """Create all SQLAlchemy tables currently declared by the project."""
        from app import models  # noqa: F401

        db.create_all()
        click.echo("Đã khởi tạo database.")
