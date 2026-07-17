"""Script to safely upgrade the database schema."""
import os
from sqlalchemy import text
from app import create_app
from app.extensions import db

def main():
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN locked_until DATETIME;"))
                print("Thêm cột locked_until vào users thành công.")
            except Exception as e:
                print("Cột locked_until có thể đã tồn tại hoặc lỗi:", e)

            try:
                conn.execute(text("ALTER TABLE alerts ADD COLUMN admin_notes TEXT;"))
                print("Thêm cột admin_notes vào alerts thành công.")
            except Exception as e:
                print("Cột admin_notes có thể đã tồn tại hoặc lỗi:", e)

if __name__ == "__main__":
    main()
