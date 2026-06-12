# Cấu trúc dự án StudyDrive

## Mục tiêu tổ chức

- `app/` là package Flask chính duy nhất.
- `ml/` chứa pipeline Machine Learning.
- `scripts/` chứa script seed, reset, export và mô phỏng hành vi.
- `data/` chứa dữ liệu thô, xử lý và mẫu.
- `artifacts/` chứa model, metrics và figures sinh ra trong quá trình ML.

## Cây thư mục hiện tại

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
│   │   ├── documents/
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
│   │   ├── document.py
│   │   ├── request_log.py
│   │   └── alert.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── document_service.py
│   │   ├── log_service.py
│   │   └── detection_service.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── request_logging.py
│   ├── decorators/
│   │   ├── __init__.py
│   │   └── authorization.py
│   ├── templates/
│   └── static/
├── ml/
│   ├── __init__.py
│   ├── build_features.py
│   ├── train.py
│   ├── evaluate.py
│   └── detect.py
├── scripts/
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
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md
├── requirements.txt
└── run.py
```

## Quy tắc đặt tên và trách nhiệm

- Model chỉ import `db` từ `app.extensions`.
- Route nằm trong `app/blueprints/*/routes.py`.
- Form nằm cạnh blueprint tương ứng.
- Service không import Flask app toàn cục.
- Middleware chỉ xử lý quan sát/chặn request, không giữ business logic lớn.
- ML code chỉ đặt trong `ml/`.
- Script vận hành/dữ liệu mẫu chỉ đặt trong `scripts/`.

## Ghi chú

- Không đổi `DATABASE_URL`.
- Không chuyển MySQL sang SQLite.
- Không commit secret hoặc `.env`.
