# StudyDrive — Web Anomaly Detection

Đề tài: **Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning**.

StudyDrive là ứng dụng Flask lưu trữ và chia sẻ tệp, đồng thời thu thập structured request log để phát hiện:

- Export Abuse
- Delete Abuse
- IDOR/BOLA Scan

## 1. Công nghệ

- Python 3.11+
- Flask, Jinja2, Bootstrap
- Flask-SQLAlchemy
- Flask-WTF
- MySQL
- PyMySQL
- Pandas, scikit-learn, joblib
- Pytest, requests

File vật lý được lưu trong `instance/uploads/`. MySQL lưu metadata, quyền chia sẻ, export job, request log và alert.

---

## 2. Cấu trúc thư mục chính

```text
web-anomaly-detection/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── errors.py
│   ├── blueprints/
│   │   ├── main/
│   │   ├── auth/
│   │   ├── documents/
│   │   ├── admin/
│   │   └── alerts/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── folder.py
│   │   ├── stored_file.py
│   │   ├── file_share.py
│   │   ├── export_job.py
│   │   ├── request_log.py
│   │   └── alert.py
│   ├── services/
│   ├── middleware/
│   ├── decorators/
│   ├── templates/
│   └── static/
├── scripts/
│   ├── __init__.py
│   ├── seed.py
│   ├── reset_demo.py
│   ├── export_logs.py
│   └── simulate_*.py
├── ml/
├── data/
├── artifacts/
├── docs/
├── tests/
├── instance/
│   └── uploads/
├── .env.example
├── .gitignore
├── requirements.txt
├── pytest.ini
├── run.py
└── README.md
```

---

## 3. Yêu cầu trước khi chạy

- Python 3.11 trở lên.
- MySQL hoặc MariaDB đang chạy.
- Có quyền tạo database.
- Port MySQL thường là `3306`; nếu bị xung đột có thể dùng `3307`.

Kiểm tra port:

```powershell
Test-NetConnection 127.0.0.1 -Port 3306
```

Hoặc:

```powershell
Test-NetConnection 127.0.0.1 -Port 3307
```

---

## 4. Tạo virtual environment

Mở PowerShell tại thư mục project:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Kiểm tra dependency:

```powershell
pip check
```

Kết quả mong đợi:

```text
No broken requirements found.
```

---

## 5. Tạo database MySQL

Mở phpMyAdmin hoặc MySQL client và chạy:

```sql
CREATE DATABASE studydrive
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Không cần tự tạo từng bảng. SQLAlchemy sẽ tạo bảng từ models.

---

## 6. Cấu hình `.env`

Sao chép `.env.example` thành `.env`:

```powershell
Copy-Item .env.example .env
```

Ví dụ MySQL port `3306`, user `root`, không có mật khẩu:

```env
APP_ENV=development
SECRET_KEY=change-this-local-secret

DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/studydrive?charset=utf8mb4
```

Nếu dùng port `3307`:

```env
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3307/studydrive?charset=utf8mb4
```

Nếu MySQL có mật khẩu:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@127.0.0.1:3306/studydrive?charset=utf8mb4
```

Không commit hoặc gửi file `.env`. Chỉ commit `.env.example` không chứa secret thật.

---

## 7. Xác nhận Flask đang dùng MySQL

### 7.1. Kiểm tra URL và dialect

```powershell
python -c "from app import create_app; from app.extensions import db; app=create_app('development'); ctx=app.app_context(); ctx.push(); print(db.engine.url.render_as_string(hide_password=True)); print('Dialect:', db.engine.dialect.name); ctx.pop()"
```

Kết quả phải có:

```text
Dialect: mysql
```

Nếu hiện `sqlite`, ứng dụng đang fallback về SQLite. Kiểm tra:

```powershell
Test-Path .env
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('DATABASE_URL'))"
```

### 7.2. Kiểm tra kết nối thật

```powershell
python -c "from app import create_app; from app.extensions import db; from sqlalchemy import text; app=create_app('development'); ctx=app.app_context(); ctx.push(); print('SELECT 1 =', db.session.execute(text('SELECT 1')).scalar()); ctx.pop()"
```

Kết quả:

```text
SELECT 1 = 1
```

---

## 8. Tạo dữ liệu demo

> `reset_demo` xóa toàn bộ bảng và dữ liệu upload demo trước khi tạo lại. Chỉ dùng trên database phát triển/demo.

Reset và tạo dữ liệu mẫu:

```powershell
python -m scripts.reset_demo
```

Kết quả mong đợi:

```text
Reset demo hoàn tất: 6 users, 15 folders, 75 files, 5 shares.
```

Chạy seed mà không xóa dữ liệu:

```powershell
python -m scripts.seed
```

Seed được thiết kế để chạy nhiều lần mà không tạo trùng.

---

## 9. Tài khoản demo

### Admin

```text
Username: admin
Password: StudyDriveAdmin@2026
```

### User

```text
Username: user1
Password: StudyDriveUser@2026
```

Các tài khoản `user2` đến `user5` dùng chung mật khẩu demo:

```text
StudyDriveUser@2026
```

Các tài khoản trên chỉ dùng cho môi trường local/demo.

---

## 10. Kiểm tra dữ liệu MySQL

```powershell
python -c "from app import create_app; from app.models import User, Folder, StoredFile, FileShare; app=create_app('development'); ctx=app.app_context(); ctx.push(); print('users =', User.query.count()); print('folders =', Folder.query.count()); print('files =', StoredFile.query.count()); print('file_shares =', FileShare.query.count()); ctx.pop()"
```

Kết quả đúng:

```text
users = 6
folders = 15
files = 75
file_shares = 5
```

Kiểm tra seed không tạo trùng:

```powershell
python -m scripts.seed
python -m scripts.seed
```

Sau đó kiểm tra bằng assertion:

```powershell
python -c "from app import create_app; from app.models import User, Folder, StoredFile, FileShare; app=create_app('development'); ctx=app.app_context(); ctx.push(); counts=(User.query.count(), Folder.query.count(), StoredFile.query.count(), FileShare.query.count()); print('Counts:', counts); assert counts == (6, 15, 75, 5), f'Seed tạo trùng: {counts}'; print('PASS: seed idempotent'); ctx.pop()"
```

---

## 11. Chạy ứng dụng

```powershell
python run.py
```

Mở:

```text
http://127.0.0.1:5000/
```

Health check:

```text
http://127.0.0.1:5000/health
```

---

## 12. Chạy test

```powershell
python -m pytest -q
```

`TestingConfig` có thể sử dụng:

```text
sqlite:///:memory:
```

Điều này phù hợp cho unit test và route test nhanh. Kết quả pytest không chứng minh MySQL đang hoạt động; MySQL phải được kiểm tra bằng dialect, `SELECT 1` và truy vấn counts ở các mục trên.

---

## 13. Test bằng virtual environment sạch

Không cần xóa `.venv` đang dùng. Tạo môi trường kiểm tra riêng:

```powershell
Remove-Item -Recurse -Force .venv_clean -ErrorAction SilentlyContinue
python -m venv .venv_clean
.\.venv_clean\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
pip check
python -m pytest -q
python run.py
```

Kiểm tra Python đang dùng:

```powershell
where.exe python
```

Đường dẫn đầu tiên phải nằm trong:

```text
.venv_clean\Scripts\python.exe
```

Sau khi test:

```powershell
deactivate
Remove-Item -Recurse -Force .venv_clean
```

---

## 14. Test API bằng Python

### 14.1. Flask test client với pytest

Không cần chạy server thật:

```python
def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
```

Chạy:

```powershell
python -m pytest -q
```

### 14.2. Test server đang chạy bằng `requests`

Khởi động server ở terminal thứ nhất:

```powershell
python run.py
```

Terminal thứ hai:

```python
import requests

response = requests.get(
    "http://127.0.0.1:5000/health",
    timeout=5,
)

print(response.status_code)
print(response.json())

assert response.status_code == 200
```

---

## 15. Lưu trữ file

MySQL chỉ lưu metadata và quan hệ. File thật nằm trong:

```text
instance/uploads/
```

Database lưu:

```text
original_name
stored_name
storage_path
mime_type
file_extension
file_size
owner_id
folder_id
```

Không lưu file người dùng trong `static/`.

---

## 16. Quy tắc bảo mật

- Password phải được hash bằng Werkzeug.
- Không lưu password plaintext.
- Form thay đổi dữ liệu phải có CSRF token.
- Không log password, cookie, CSRF token hoặc session token nguyên bản.
- Không trả `storage_path` cho client.
- Mọi request có `file_id`, `folder_id` hoặc `export_job_id` phải kiểm tra authorization.
- `VIEWER` chỉ được xem và download.
- Simulator chỉ được chạy trên hệ thống local của dự án.

---

## 17. Troubleshooting

### Flask vẫn dùng SQLite

```powershell
Test-Path .env
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('DATABASE_URL'))"
```

Đảm bảo `load_dotenv()` chạy trước khi `Config` gọi `os.getenv()`.

### Không kết nối được MySQL

```powershell
Test-NetConnection 127.0.0.1 -Port 3306
```

Kiểm tra MySQL đang chạy, port và `DATABASE_URL`.

### `Unknown database 'studydrive'`

Tạo database theo mục 5.

### `Access denied for user`

Kiểm tra username và password MySQL.

### `No module named pymysql`

```powershell
pip install PyMySQL
```

và đảm bảo `PyMySQL` có trong `requirements.txt`.

### `no such table` hoặc chưa có bảng

Xác nhận dialect là MySQL rồi chạy:

```powershell
python -m scripts.reset_demo
```

---

## 18. Quy tắc codebase

- Chỉ tạo Flask app qua `create_app()`.
- Model import `db` từ `app.extensions`.
- Không import Flask app toàn cục trong model/service/route.
- Blueprint được đăng ký trong app factory.
- Không commit `.env`, `.venv`, `__pycache__`, database dump chứa secret hoặc file upload cá nhân.

---

## 14. Folder, upload an toàn và My Files

Các endpoint đã triển khai:

```text
GET  /files
GET  /folders/<folder_id>
GET  /folders/create
POST /folders/create
GET  /files/upload
POST /files/upload
```

Đặc điểm an toàn chính:

- Giới hạn upload 20 MB bằng `MAX_CONTENT_LENGTH` và trang lỗi 413.
- Kiểm tra extension, MIME type và chữ ký cơ bản của tệp.
- Làm sạch tên client bằng `secure_filename`, nhưng tên lưu thật luôn là UUID.
- File vật lý nằm trong `instance/uploads/<user_id>/`, không nằm trong `static`.
- Folder đích luôn được truy vấn kèm `owner_id` của user đăng nhập.
- Nếu DB commit thất bại, transaction rollback và file vật lý vừa ghi bị xóa.
- `/files` hỗ trợ search, filter folder/extension, sort và pagination giữ query parameters.

Hướng dẫn chi tiết và test matrix: `docs/implementation_day15_16.md`.

Chạy test:

```powershell
pytest -q
```

Kết quả hiện tại:

```text
15 passed
```

---

## 19. Tuần 3 — Admin logs, export log và simulator dữ liệu

### 19.1. Admin quản lý log

Sau khi đăng nhập admin, mở:

```text
http://127.0.0.1:5000/admin/logs
```

Trang này hỗ trợ:

- Lọc theo thời gian, user, `action_type`, `status_code`, `sensitive`, keyword trong path.
- Sort theo mới/cũ, response time, status hoặc action.
- Pagination và giữ query parameters khi chuyển trang.
- Chi tiết log: `request_id`, `session_id_hash`, user-agent, security context và link user/file/folder nếu xác định được.
- Export CSV theo bộ lọc hiện tại.

Test user thường bị chặn:

```text
Đăng nhập user1 → truy cập /admin/logs → phải nhận 403.
```

### 19.2. Export request logs bằng script

```powershell
python -m scripts.export_logs --output data/raw/request_logs_raw.csv
```

Lọc ví dụ:

```powershell
python -m scripts.export_logs --action-type export --sensitive yes --output data/raw/export_logs.csv
python -m scripts.export_logs --status-code 404 --path-keyword /files --output data/raw/bola_like_logs.csv
```

Audit bằng Pandas:

```powershell
python -m scripts.audit_logs --input data/raw/request_logs_raw.csv --output docs/data_audit.md
```

### 19.3. Chạy simulator normal/anomaly

Terminal 1:

```powershell
python run.py
```

Terminal 2:

```powershell
python -m scripts.reset_demo
python -m scripts.simulate_normal --fast --requests 300
python -m scripts.simulate_export_abuse --fast --severity mild
python -m scripts.simulate_delete_abuse --fast --severity mild
python -m scripts.simulate_bola_scan --fast --mode burst
python -m scripts.export_logs --output data/raw/request_logs_raw.csv
python -m scripts.audit_logs --input data/raw/request_logs_raw.csv --output docs/data_audit.md
```

Sinh raw dataset v1:

```powershell
python -m scripts.generate_raw_dataset_v1 --fast --normal-requests 5000
```

Đầu ra chính:

```text
data/raw/request_logs_raw.csv
data/raw/ground_truth.csv
data/raw/generation_metadata.json
docs/data_audit.md
```

> Lưu ý: các simulator chỉ được chạy trên StudyDrive local của dự án. `simulate_bola_scan.py` chỉ tạo request đổi `file_id`; server vẫn phải trả 404/denied và không lộ dữ liệu user khác.

---

## 20. Pipeline từ ngày 29/06 đến 19/07: ML + Alert + Demo

Chi tiết từng ngày nằm trong:

```text
docs/day/week4_5_6_daily_guide.md
```

### 20.1. Build feature dataset `features_v1`

Sau khi đã có:

```text
data/raw/request_logs_raw.csv
data/raw/ground_truth.csv
```

Chạy:

```powershell
python -m ml.build_features --logs data/raw/request_logs_raw.csv --ground-truth data/raw/ground_truth.csv --output-dir data/processed/features_v1
```

Đầu ra:

```text
data/processed/features_v1/clean_logs.csv
data/processed/features_v1/windowed_logs.csv
data/processed/features_v1/window_mapping.csv
data/processed/features_v1/features_all.csv
data/processed/features_v1/train_features.csv
data/processed/features_v1/validation_features.csv
data/processed/features_v1/test_features.csv
data/processed/features_v1/feature_list.json
data/processed/features_v1/feature_dictionary.md
data/processed/features_v1/split_manifest.json
data/processed/features_v1/processing_report.json
```

Test nhanh:

```powershell
python - <<'PY'
import pandas as pd, json
base='data/processed/features_v1'
f=pd.read_csv(base+'/features_all.csv')
print(f.shape)
print(f[['window_id','label','scenario','request_count','export_count','delete_count','forbidden_rate']].head())
print(json.load(open(base+'/split_manifest.json', encoding='utf-8')))
PY
```

### 20.2. EDA feature

```powershell
python -m ml.eda --features data/processed/features_v1/features_all.csv --output-dir artifacts/figures/eda_features_v1
```

Đầu ra:

```text
artifacts/figures/eda_features_v1/*.png
artifacts/figures/eda_features_v1/eda_notes.md
```

### 20.3. Train Isolation Forest

Baseline:

```powershell
python -m ml.train --features-dir data/processed/features_v1 --output-dir artifacts/models/iforest_v1
```

Tuning bằng validation:

```powershell
python -m ml.train --features-dir data/processed/features_v1 --output-dir artifacts/models/iforest_v1 --tune
```

Đầu ra:

```text
artifacts/models/iforest_v1/model.joblib
artifacts/models/iforest_v1/model_metadata.json
artifacts/models/iforest_v1/feature_list.json
artifacts/metrics/tuning_results.csv
```

### 20.4. Evaluate holdout test

```powershell
python -m ml.evaluate --model artifacts/models/iforest_v1/model.joblib --test data/processed/features_v1/test_features.csv --output-dir artifacts/metrics
```

Đầu ra:

```text
artifacts/metrics/test_metrics.json
artifacts/metrics/scenario_metrics.csv
artifacts/metrics/test_predictions.csv
artifacts/metrics/confusion_matrix.png
artifacts/metrics/score_distribution.png
```

### 20.5. Detect offline bằng CSV feature

```powershell
python -m ml.detect --model artifacts/models/iforest_v1/model.joblib --features data/processed/features_v1/test_features.csv --output artifacts/metrics/detect_predictions.csv
```

### 20.6. Tích hợp web: Run detection và xem alert

Chạy detection từ database log hiện tại:

```powershell
python -m scripts.run_detection
```

Hoặc vào web bằng tài khoản admin:

```text
/alerts → Run detection
```

Kiểm tra alert:

```powershell
python - <<'PY'
from app import create_app
from app.models import Alert
app=create_app('development')
with app.app_context():
    print('alerts =', Alert.query.count())
    for a in Alert.query.order_by(Alert.anomaly_score.desc()).limit(5):
        print(a.id, a.user_id, a.anomaly_score, a.scenario_hint, a.model_version)
PY
```

### 20.7. Demo end-to-end một lệnh

Terminal 1:

```powershell
python run.py
```

Terminal 2:

```powershell
python -m scripts.run_demo_scenario --scenario all --fast --normal-requests 800
```

Sau đó mở:

```text
/admin/logs
/alerts
```

`/alerts/<id>` hiển thị feature nổi bật và link về log gốc trong window.

### 20.8. Gói nộp cuối

PowerShell gợi ý:

```powershell
Compress-Archive -Path app,ml,scripts,docs,data,artifacts,tests,README.md,requirements.txt,run.py,pytest.ini -DestinationPath final_submission_2026-07-19.zip -Force
Get-FileHash final_submission_2026-07-19.zip -Algorithm SHA256
```

Không đưa vào ZIP: `.env`, `.venv`, `.git`, `__pycache__`, dữ liệu cá nhân hoặc secret thật.
