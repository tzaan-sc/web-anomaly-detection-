# StudyDrive Flask Skeleton

Skeleton Flask cho đồ án:

**Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning**

## 1. Thành phần hiện có

- Application factory `create_app()`.
- Blueprints: `main`, `auth`, `documents`, `admin`, `alerts`.
- Cấu hình `development`, `testing`, `production`.
- Flask-SQLAlchemy và Flask-WTF CSRF theo extension pattern.
- Bootstrap base layout, navbar theo session/role, flash message và footer.
- Route `GET /health`.
- Trang lỗi 404 và 500.
- Kiểm thử bằng pytest.
- SQLite mặc định để chạy skeleton nhanh; có mẫu cấu hình MySQL.

## 2. Yêu cầu môi trường

- Python 3.11 trở lên.
- Windows PowerShell hoặc Command Prompt.
- Git.

Kiểm tra Python:

```powershell
python --version
```

## 3. Cài đặt lần đầu bằng PowerShell

Mở terminal tại thư mục dự án:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
flask --app run.py init-db
python run.py
```

Mở trình duyệt:

- Trang chủ: `http://127.0.0.1:5000`
- Health check: `http://127.0.0.1:5000/health`

Dừng server bằng `Ctrl + C`.

## 4. Cài đặt bằng Command Prompt

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
flask --app run.py init-db
python run.py
```

## 5. Chạy kiểm thử

```powershell
pytest
```

Kết quả mong đợi: toàn bộ test đều `passed`.

## 6. Dùng MySQL thay cho SQLite

Tạo database:

```sql
CREATE DATABASE studydrive
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Trong `.env`, đặt:

```env
DATABASE_URL=mysql+pymysql://root:MAT_KHAU@localhost:3306/studydrive
```

Sau đó chạy:

```powershell
flask --app run.py init-db
python run.py
```

Không commit `.env` vì file này có thể chứa mật khẩu và secret.

## 7. Kiểm tra khả năng cài lại sạch

Đây là bước acceptance test bắt buộc:

```powershell
deactivate
Remove-Item -Recurse -Force .venv

python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest
python run.py
```

Sau đó xác nhận:

1. `pytest` chạy thành công.
2. `/health` trả HTTP 200 và JSON có `"status": "ok"`.
3. Trang chủ hiển thị Bootstrap UI.
4. `/auth/login`, `/documents/`, `/admin/`, `/alerts/` đều mở được.
5. Đường dẫn không tồn tại hiển thị trang 404 tùy chỉnh.

## 8. Cấu trúc chính

```text
studydrive_flask_skeleton/
├── app/
│   ├── blueprints/
│   │   ├── admin/
│   │   ├── alerts/
│   │   ├── auth/
│   │   ├── documents/
│   │   └── main/
│   ├── static/css/
│   ├── templates/
│   │   ├── admin/
│   │   ├── alerts/
│   │   ├── auth/
│   │   ├── documents/
│   │   ├── errors/
│   │   └── main/
│   ├── __init__.py
│   ├── config.py
│   ├── errors.py
│   └── extensions.py
├── tests/
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md
├── requirements.txt
└── run.py
```

## 9. Vì sao cấu trúc này không circular import?

- `db` và `csrf` chỉ được khai báo trong `app/extensions.py`.
- `create_app()` gọi `init_app()` sau khi app đã được tạo.
- Blueprint được import bên trong `register_blueprints()`, không import app toàn cục.
- Route chỉ import đối tượng blueprint của module tương ứng.
- Model sau này chỉ cần import `db` từ `app.extensions`, không import `app`.
