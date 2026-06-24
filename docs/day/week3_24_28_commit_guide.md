# Commit guide — 24/06 đến 28/06/2026

## 24/06 — Admin log manager

```powershell
git add app/blueprints/admin/routes.py app/templates/admin/logs.html app/templates/admin/log_detail.html app/templates/admin/index.html app/templates/base.html app/services/log_service.py tests/test_admin_logs.py
git commit -m "feat(admin): add request log manager"
```

Test chính:

```powershell
python -m pytest tests/test_admin_logs.py -q
```

## 25/06 — Logger QA, export_logs và data dictionary

```powershell
git add scripts/export_logs.py scripts/audit_logs.py docs/data_dictionary.md tests/test_request_logging.py README.md
git commit -m "test(logging): add log export and data quality checks"
```

Test chính:

```powershell
python -m pytest tests/test_request_logging.py -q
python -m scripts.export_logs --output data/raw/logs_test.csv
python -m scripts.audit_logs --input data/raw/logs_test.csv --output docs/data_audit.md
```

## 26/06 — Normal simulator

```powershell
git add scripts/simulator_common.py scripts/simulate_normal.py docs/data_generation_plan.md docs/ground_truth_schema.md README.md
git commit -m "feat(data): add normal behavior simulator"
```

Test chính:

```powershell
python run.py
python -m scripts.simulate_normal --fast --requests 300
```

## 27/06 — Three anomaly simulators

```powershell
git add scripts/simulate_export_abuse.py scripts/simulate_delete_abuse.py scripts/simulate_bola_scan.py scripts/simulator_common.py README.md
git commit -m "feat(data): add anomaly behavior simulators"
```

Test chính:

```powershell
python -m scripts.simulate_export_abuse --fast --severity mild
python -m scripts.simulate_delete_abuse --fast --severity mild
python -m scripts.simulate_bola_scan --fast --mode burst
```

## 28/06 — Raw dataset v1 generation and audit

```powershell
git add scripts/generate_raw_dataset_v1.py scripts/audit_logs.py docs/data_generation_plan.md docs/ground_truth_schema.md README.md
git commit -m "feat(data): generate and audit raw dataset v1"
git tag raw-dataset-v1-2026-06-28
```

Test chính:

```powershell
python -m scripts.generate_raw_dataset_v1 --fast --normal-requests 5000
```

Checklist khóa raw v1:

```text
☐ request_logs_raw.csv đủ 5.000–10.000 dòng
☐ ground_truth.csv có normal/export/delete/bola
☐ generation_metadata.json có run_id/seed/config/version
☐ docs/data_audit.md không báo duplicate request_id
☐ không có password/token/cookie/body/storage_path trong CSV
```
