"""Reset the local database and uploads to the fixed StudyDrive demo state.

Run from the project root with:
    python -m scripts.reset_demo
"""

from __future__ import annotations

import shutil
from pathlib import Path

from flask import current_app

from app import create_app
from app.extensions import db
from scripts.seed import seed_demo_data


def reset_demo_data() -> dict[str, int]:
    from app import models  # noqa: F401

    upload_root = Path(current_app.config["UPLOAD_FOLDER"])
    db.session.remove()
    db.drop_all()

    if upload_root.exists():
        shutil.rmtree(upload_root)
    upload_root.mkdir(parents=True, exist_ok=True)

    db.create_all()
    return seed_demo_data()


def main() -> None:
    app = create_app()
    with app.app_context():
        try:
            counts = reset_demo_data()
        except Exception:
            db.session.rollback()
            raise

        print(
            "Reset demo hoàn tất: "
            f"{counts['users']} users, "
            f"{counts['folders']} folders, "
            f"{counts['files']} files, "
            f"{counts['shares']} shares."
        )


if __name__ == "__main__":
    main()
