import os

import click
from dotenv import load_dotenv
from flask import Flask

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
    register_blueprints(app)
    register_error_handlers(app)
    register_cli_commands(app)

    return app


def register_extensions(app: Flask) -> None:
    """Attach Flask extensions to the current app instance."""
    db.init_app(app)
    csrf.init_app(app)


def register_blueprints(app: Flask) -> None:
    """Import blueprints locally to avoid circular imports."""
    from app.blueprints.admin import bp as admin_bp
    from app.blueprints.alerts import bp as alerts_bp
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.documents import bp as documents_bp
    from app.blueprints.main import bp as main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(documents_bp, url_prefix="/documents")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(alerts_bp, url_prefix="/alerts")


def register_error_handlers(app: Flask) -> None:
    from app.errors import page_not_found, server_error

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, server_error)


def register_cli_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db() -> None:
        """Create all SQLAlchemy tables currently declared by the project."""
        from app import models  # noqa: F401

        db.create_all()
        click.echo("Đã khởi tạo database.")
