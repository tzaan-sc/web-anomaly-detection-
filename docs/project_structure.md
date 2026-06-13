# CẤU TRÚC DỰ ÁN STUDYDRIVE

## 1. Mục tiêu tổ chức

- `app/` là package Flask chính duy nhất.
- `app/blueprints/` chứa route theo nhóm giao diện.
- `app/models/` chứa SQLAlchemy models, mỗi model một file.
- `app/services/` chứa nghiệp vụ và transaction.
- `app/middleware/` chứa structured request logger.
- `ml/` chứa pipeline Machine Learning.
- `scripts/` chứa seed, reset, export log và simulator.
- `data/` chứa dữ liệu thô, xử lý và mẫu.
- `artifacts/` chứa model, metrics và figures.

---

## 2. Cây thư mục đích

```text
web-anomaly-detection/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── errors.py
│   ├── blueprints/
│   │   ├── __init__.py
│   │   ├── main/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── files/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── admin/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   └── alerts/
│   │       ├── __init__.py
│   │       └── routes.py
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
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── file_service.py
│   │   ├── folder_service.py
│   │   ├── share_service.py
│   │   ├── export_service.py
│   │   ├── log_service.py
│   │   └── detection_service.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── request_logging.py
│   ├── decorators/
│   │   ├── __init__.py
│   │   └── authorization.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── main/
│   │   ├── auth/
│   │   ├── files/
│   │   ├── admin/
│   │   ├── alerts/
│   │   └── errors/
│   └── static/
│       ├── css/
│       │   └── app.css
│       └── js/
│           └── app.js
├── ml/
│   ├── __init__.py
│   ├── build_features.py
│   ├── train.py
│   ├── evaluate.py
│   └── detect.py
├── scripts/
│   ├── __init__.py
│   ├── seed.py
│   ├── reset_demo.py
│   ├── export_logs.py
│   ├── simulate_normal.py
│   ├── simulate_export_abuse.py
│   ├── simulate_delete_abuse.py
│   └── simulate_bola_scan.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
├── artifacts/
│   ├── models/
│   ├── metrics/
│   └── figures/
├── docs/
├── tests/
├── instance/
│   ├── app.db
│   └── uploads/
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md
├── requirements.txt
└── run.py
```

---

## 3. Các thay đổi từ skeleton cũ

```text
app/blueprints/documents/   → app/blueprints/files/
app/models/document.py      → app/models/stored_file.py
app/services/document_service.py → app/services/file_service.py
```

Bổ sung:

```text
Folder
FileShare
ExportJob
ExportJobItem
folder_service
share_service
export_service
instance/uploads/
scripts/__init__.py
```

Không tạo thêm `app/models.py` vì đã có package `app/models/`.

---

## 4. Quy tắc đặt tên và trách nhiệm

- Model chỉ import `db` từ `app.extensions`.
- Class lưu metadata tệp tên `StoredFile`; tên bảng là `files`.
- Route nằm trong `app/blueprints/*/routes.py`.
- Form nằm cạnh blueprint tương ứng.
- Folder/share/export route có thể nằm chung blueprint `files` để tránh chia nhỏ quá mức.
- Service không import Flask app toàn cục.
- Middleware không giữ business logic lớn.
- ML code chỉ đặt trong `ml/`.
- Script vận hành và dữ liệu mẫu chỉ đặt trong `scripts/`.
- File người dùng đặt trong `instance/uploads/`, không đặt trong `static/`.

---

## 5. Database và cấu hình

- Database thống nhất: **SQLite + SQLAlchemy**.
- URI development mặc định: `sqlite:///app.db`.
- Với app factory dùng `instance_relative_config=True`, file nằm tại `instance/app.db`.
- Không commit database chứa dữ liệu thật.
- Có thể commit database demo mẫu nếu giảng viên yêu cầu; ưu tiên tạo lại bằng `reset_demo.py`.
- Không commit `.env`, secret hoặc upload thật.

---

## 6. Thứ tự import model

`app/models/__init__.py` phải import:

```python
from app.models.user import User
from app.models.folder import Folder
from app.models.stored_file import StoredFile
from app.models.file_share import FileShare
from app.models.export_job import ExportJob, ExportJobItem
from app.models.request_log import RequestLog
from app.models.alert import Alert
```

Việc này giúp `db.create_all()` nhận diện đủ bảng.
