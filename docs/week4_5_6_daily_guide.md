# Hướng dẫn làm tiếp lộ trình 29/06 → 19/07 và test từng ngày

Tài liệu này đi kèm các file code đã bổ sung cho phần ML và alert dashboard:

- `ml/build_features.py`
- `ml/eda.py`
- `ml/train.py`
- `ml/evaluate.py`
- `ml/detect.py`
- `app/services/detection_service.py`
- `app/blueprints/alerts/routes.py`
- `app/templates/alerts/index.html`
- `app/templates/alerts/detail.html`
- `scripts/run_detection.py`
- `scripts/run_demo_scenario.py`

> Luôn chạy từ thư mục gốc `web-anomaly-detection`. PowerShell nên bật venv trước: `.\.venv\Scripts\Activate.ps1`.

---

## Chuẩn bị trước ngày 29

Terminal 1:

```powershell
python -m scripts.reset_demo
python run.py
```

Terminal 2 dùng để chạy simulator/ML:

```powershell
python -m scripts.generate_raw_dataset_v1 --fast --normal-requests 5000
```

Kết quả cần có:

```text
data/raw/request_logs_raw.csv
data/raw/ground_truth.csv
data/raw/generation_metadata.json
docs/data_audit.md
```

Nếu máy yếu hoặc cần test nhanh:

```powershell
python -m scripts.generate_raw_dataset_v1 --fast --normal-requests 800
```

---

## Thứ Hai 29/06 — Làm sạch, chuẩn hóa log và gắn nhãn sơ bộ

### File cần làm

Đã bổ sung trong `ml/build_features.py`:

- `load_logs`
- `validate_schema`
- `clean_logs`
- `load_ground_truth`
- `attach_ground_truth`

### Lệnh chạy

```powershell
python -m ml.build_features --logs data/raw/request_logs_raw.csv --ground-truth data/raw/ground_truth.csv --output-dir data/processed/features_v1
```

### Cách test

```powershell
python - <<'PY'
import pandas as pd
clean = pd.read_csv('data/processed/features_v1/clean_logs.csv')
report = __import__('json').load(open('data/processed/features_v1/processing_report.json', encoding='utf-8'))
print(clean.shape)
print(clean.dtypes)
print(report['cleaning'])
print('duplicate request_id =', clean['request_id'].duplicated().sum())
print(clean[['timestamp','user_id','session_id_hash','label','scenario']].head())
PY
```

PASS khi:

- `duplicate request_id = 0`
- `timestamp` parse được, không bị rỗng hàng loạt
- có cột `label`, `scenario`, `run_id`
- số dòng không mất ngoài `bad timestamp` và `duplicate` đã ghi trong report

Commit gợi ý:

```powershell
git add ml/build_features.py data/processed/features_v1 docs/day/week4_5_6_daily_guide.md
git commit -m "feat: build clean request log dataset"
```

---

## Thứ Ba 30/06 — Chia cửa sổ hành vi theo user/session

### File cần làm

Trong `ml/build_features.py`:

- `assign_windows`
- `make_window_id`
- xuất `windowed_logs.csv`
- xuất `window_mapping.csv`

### Lệnh chạy

```powershell
python -m ml.build_features --logs data/raw/request_logs_raw.csv --ground-truth data/raw/ground_truth.csv --output-dir data/processed/features_v1
```

### Cách test

```powershell
python - <<'PY'
import pandas as pd
mapping = pd.read_csv('data/processed/features_v1/window_mapping.csv')
windows = pd.read_csv('data/processed/features_v1/windowed_logs.csv')
print(mapping.shape)
print('request duplicated in mapping =', mapping['request_id'].duplicated().sum())
print('null window_id =', mapping['window_id'].isna().sum())
print(windows[['request_id','user_id','session_id_hash','timestamp','window_start','window_end','window_id']].head(20))
PY
```

PASS khi:

- mỗi request có đúng 1 `window_id`
- không có `window_id` rỗng
- `window_start` cách nhau theo mốc 5 phút

Commit gợi ý:

```powershell
git add ml/build_features.py data/processed/features_v1/window_mapping.csv
git commit -m "feat: create user session time windows"
```

---

## Thứ Tư 01/07 — Feature hoạt động chung + Export/Delete

### File cần làm

Trong `ml/build_features.py`:

- `aggregate_features`
- feature chung: `request_count`, `unique_endpoint_count`, `avg_inter_request_sec`, `burst_rate`, `error_rate`, `sensitive_ratio`
- feature Export/Delete: `export_count`, `export_ratio`, `delete_count`, `delete_ratio`, `unique_deleted_resource_count`
- `feature_dictionary.md`

### Lệnh chạy

```powershell
python -m ml.build_features --logs data/raw/request_logs_raw.csv --ground-truth data/raw/ground_truth.csv
```

### Cách test

```powershell
python - <<'PY'
import pandas as pd, json
f = pd.read_csv('data/processed/features_v1/features_all.csv')
feature_list = json.load(open('data/processed/features_v1/feature_list.json', encoding='utf-8'))
print('features:', len(feature_list), feature_list)
print(f[feature_list].isna().sum().sort_values(ascending=False).head())
print(f[['window_id','label','scenario','request_count','export_count','delete_count','sensitive_ratio']].head(20))
print('inf count:', (~pd.DataFrame(__import__('numpy').isfinite(f[feature_list]))).sum().sum())
PY
```

PASS khi:

- có ít nhất 12 feature
- không NaN/inf
- `export_count`, `delete_count` tăng ở window anomaly tương ứng

Commit gợi ý:

```powershell
git add ml/build_features.py data/processed/features_v1/feature_dictionary.md
git commit -m "feat: aggregate activity export delete features"
```

---

## Thứ Năm 02/07 — Feature IDOR/BOLA và chuỗi hành vi

### File cần làm

Trong `ml/build_features.py`:

- `unique_resource_id_count`
- `resource_id_request_ratio`
- `forbidden_count`, `forbidden_rate`
- `not_found_count`, `not_found_rate`
- `unique_failed_resource_id_count`
- `resource_id_change_rate`
- `max_sensitive_streak`

### Lệnh chạy

```powershell
python -m ml.build_features --logs data/raw/request_logs_raw.csv --ground-truth data/raw/ground_truth.csv
```

### Cách test

```powershell
python - <<'PY'
import pandas as pd
f = pd.read_csv('data/processed/features_v1/features_all.csv')
cols = ['scenario','label','request_count','unique_resource_id_count','forbidden_rate','not_found_rate','unique_failed_resource_id_count','resource_id_change_rate']
print(f[cols].sort_values(['label','unique_failed_resource_id_count'], ascending=[False, False]).head(20))
print('\nMean theo scenario:')
print(f.groupby('scenario')[cols[2:]].mean().round(3))
PY
```

PASS khi:

- window `bola` có `forbidden_rate` hoặc `not_found_rate` cao
- `unique_failed_resource_id_count` của BOLA cao hơn normal
- không dùng khoảng cách số ID làm feature chính

Commit gợi ý:

```powershell
git add ml/build_features.py data/processed/features_v1/feature_dictionary.md
git commit -m "feat: add bola resource probing features"
```

---

## Thứ Sáu 03/07 — Chia train/validation/test chống leakage

### File cần làm

Trong `ml/build_features.py`:

- `split_features`
- xuất `train_features.csv`
- xuất `validation_features.csv`
- xuất `test_features.csv`
- xuất `split_manifest.json`

### Lệnh chạy

```powershell
python -m ml.build_features --logs data/raw/request_logs_raw.csv --ground-truth data/raw/ground_truth.csv
```

### Cách test

```powershell
python - <<'PY'
import pandas as pd, json
base='data/processed/features_v1'
train=pd.read_csv(base+'/train_features.csv')
val=pd.read_csv(base+'/validation_features.csv')
test=pd.read_csv(base+'/test_features.csv')
manifest=json.load(open(base+'/split_manifest.json', encoding='utf-8'))
print(manifest)
print('train anomaly rows =', train['label'].sum())
print('overlap train/test window =', len(set(train.window_id)&set(test.window_id)))
print('overlap train/val window =', len(set(train.window_id)&set(val.window_id)))
PY
```

PASS khi:

- `train anomaly rows = 0`
- không trùng `window_id` giữa train/validation/test
- validation/test có anomaly để đánh giá

Commit gợi ý:

```powershell
git add ml/build_features.py data/processed/features_v1/split_manifest.json
git commit -m "feat: split feature windows without leakage"
```

---

## Thứ Bảy 04/07 — EDA và kiểm tra chất lượng feature

### File cần làm

Đã bổ sung `ml/eda.py`.

### Lệnh chạy

```powershell
python -m ml.eda --features data/processed/features_v1/features_all.csv --output-dir artifacts/figures/eda_features_v1
```

### Cách test

```powershell
Get-ChildItem artifacts\figures\eda_features_v1
Get-Content artifacts\figures\eda_features_v1\eda_notes.md
```

PASS khi có:

- `hist_request_count.png`
- `hist_export_count.png`
- `hist_delete_count.png`
- `hist_forbidden_rate.png`
- `hist_unique_resource_id_count.png`
- `eda_notes.md`

Commit gợi ý:

```powershell
git add ml/eda.py artifacts/figures/eda_features_v1
git commit -m "docs: add feature eda charts and notes"
```

---

## Chủ Nhật 05/07 — Khóa features_v1

### Lệnh chạy cuối tuần

```powershell
python -m ml.build_features --logs data/raw/request_logs_raw.csv --ground-truth data/raw/ground_truth.csv --output-dir data/processed/features_v1
python -m ml.eda
```

### Cách test tái lập

Chạy lại 2 lần:

```powershell
python -m ml.build_features --logs data/raw/request_logs_raw.csv --ground-truth data/raw/ground_truth.csv --output-dir data/processed/features_v1
python - <<'PY'
import pandas as pd, json
base='data/processed/features_v1'
print(pd.read_csv(base+'/features_all.csv').shape)
print(json.load(open(base+'/processing_report.json', encoding='utf-8'))['window_count'])
PY
```

PASS khi shape/schema giống nhau.

Commit/tag:

```powershell
git add ml data/processed/features_v1 artifacts/figures/eda_features_v1
git commit -m "milestone: freeze features v1"
git tag milestone-week-4
```

---

## Thứ Hai 06/07 — Train baseline Isolation Forest

### File cần làm

Đã bổ sung `ml/train.py`.

### Lệnh chạy

```powershell
python -m ml.train --features-dir data/processed/features_v1 --output-dir artifacts/models/iforest_v1
```

### Cách test

```powershell
python - <<'PY'
import joblib, json, os
path='artifacts/models/iforest_v1/model.joblib'
print(os.path.exists(path))
artifact=joblib.load(path)
print(artifact.keys())
print(artifact['metadata']['model_version'])
print('features =', len(artifact['feature_list']))
print('threshold =', artifact['threshold'])
PY
```

PASS khi process mới load được `model.joblib`, có `threshold`, `feature_list`, `metadata`.

---

## Thứ Ba 07/07 — Tuning tham số và threshold

### Lệnh chạy

```powershell
python -m ml.train --features-dir data/processed/features_v1 --output-dir artifacts/models/iforest_v1 --tune
```

### Cách test

```powershell
python - <<'PY'
import pandas as pd, json
print(pd.read_csv('artifacts/metrics/tuning_results.csv').head(10))
meta=json.load(open('artifacts/models/iforest_v1/model_metadata.json', encoding='utf-8'))
print(meta['parameters'])
print(meta['validation_metrics'])
PY
```

PASS khi:

- có `artifacts/metrics/tuning_results.csv`
- chọn config dựa trên F1/FPR validation
- không dùng test set để chọn threshold

---

## Thứ Tư 08/07 — Đánh giá holdout test

### File cần làm

Đã bổ sung `ml/evaluate.py`.

### Lệnh chạy

```powershell
python -m ml.evaluate --model artifacts/models/iforest_v1/model.joblib --test data/processed/features_v1/test_features.csv --output-dir artifacts/metrics
```

### Cách test

```powershell
Get-ChildItem artifacts\metrics
python - <<'PY'
import json, pandas as pd
print(json.load(open('artifacts/metrics/test_metrics.json', encoding='utf-8')))
print(pd.read_csv('artifacts/metrics/scenario_metrics.csv'))
print(pd.read_csv('artifacts/metrics/test_predictions.csv').head())
PY
```

PASS khi có:

- `test_metrics.json`
- `scenario_metrics.csv`
- `test_predictions.csv`
- `confusion_matrix.png`
- `score_distribution.png`

---

## Thứ Năm 09/07 — Phân tích false positive/false negative

### Lệnh hỗ trợ

```powershell
python - <<'PY'
import pandas as pd
p=pd.read_csv('artifacts/metrics/test_predictions.csv')
fp=p[(p.label==0)&(p.y_pred==1)].sort_values('anomaly_score', ascending=False).head(10)
fn=p[(p.label==1)&(p.y_pred==0)].sort_values('anomaly_score').head(10)
fp.to_csv('artifacts/metrics/false_positive_top10.csv', index=False, encoding='utf-8-sig')
fn.to_csv('artifacts/metrics/false_negative_top10.csv', index=False, encoding='utf-8-sig')
print('FP:', fp[['window_id','scenario','anomaly_score','scenario_hint','request_count','export_count','delete_count','forbidden_rate']])
print('FN:', fn[['window_id','scenario','anomaly_score','scenario_hint','request_count','export_count','delete_count','forbidden_rate']])
PY
```

Tạo file ghi nhận:

```powershell
New-Item -Force docs\error_analysis.md
```

Nội dung nên ghi:

- False positive thường do normal user thao tác nhanh/export hợp lệ.
- False negative có thể do window cắt ranh giới hoặc severity nhẹ.
- `scenario_hint` chỉ để giải thích, không phải nhãn train.

Commit:

```powershell
git add artifacts/metrics docs/error_analysis.md ml/detect.py
git commit -m "docs: analyze false positives and negatives"
```

---

## Thứ Sáu 10/07 — Đóng gói model và inference pipeline

### File cần làm

Đã bổ sung `ml/detect.py`.

### Lệnh chạy

```powershell
python -m ml.detect --model artifacts/models/iforest_v1/model.joblib --features data/processed/features_v1/test_features.csv --output artifacts/metrics/detect_predictions.csv
```

### Cách test

```powershell
python - <<'PY'
import pandas as pd, joblib
p=pd.read_csv('artifacts/metrics/detect_predictions.csv')
print(p[['window_id','anomaly_score','threshold','y_pred','scenario_hint','top_features_json']].head())
print('anomaly rows =', p.y_pred.sum())
artifact=joblib.load('artifacts/models/iforest_v1/model.joblib')
print(artifact['metadata']['model_version'])
PY
```

PASS khi:

- restart process vẫn predict được
- output có `y_pred`, `anomaly_score`, `scenario_hint`
- thiếu model thì báo lỗi rõ

---

## Thứ Bảy 11/07 — Tích hợp detection, lưu alert và liên kết log

### File cần làm

Đã bổ sung:

- `app/services/detection_service.py`
- `scripts/run_detection.py`
- cập nhật `app/blueprints/alerts/routes.py`
- cập nhật template alerts

### Lệnh chạy

```powershell
python -m scripts.run_detection
```

Hoặc mở web:

```text
/admin hoặc /alerts → Run detection
```

### Cách test

```powershell
python - <<'PY'
from app import create_app
from app.models import Alert
app=create_app('development')
with app.app_context():
    print('alerts =', Alert.query.count())
    for a in Alert.query.order_by(Alert.anomaly_score.desc()).limit(5):
        print(a.id, a.user_id, a.window_id, a.anomaly_score, a.scenario_hint, a.model_version)
PY
```

Chạy lại lần 2:

```powershell
python -m scripts.run_detection
```

PASS khi alert không bị nhân đôi nhờ unique `window_id + model_version`.

---

## Chủ Nhật 12/07 — Demo end-to-end ba scenario

### Lệnh nhanh

Terminal 1:

```powershell
python run.py
```

Terminal 2:

```powershell
python -m scripts.run_demo_scenario --scenario all --fast --normal-requests 800
```

### Cách test trên web

1. Đăng nhập admin.
2. Mở `/admin/logs`, lọc `action_type=export`, `delete`, hoặc status `403/404`.
3. Mở `/alerts`.
4. Vào chi tiết alert, bấm **Xem log gốc**.

PASS khi mỗi scenario có alert hoặc có giải thích trung thực trong `docs/error_analysis.md` nếu bị bỏ sót.

Tag:

```powershell
git add .
git commit -m "milestone: integrate isolation forest alerts"
git tag milestone-week-5
```

---

## Thứ Hai 13/07 — Hoàn thiện dashboard logs + alerts

### File cần kiểm tra

- `app/templates/alerts/index.html`
- `app/templates/alerts/detail.html`
- `app/blueprints/alerts/routes.py`
- `app/services/detection_service.py`

### Cách test

```text
/admin/logs        → filter/sort/export vẫn chạy
/alerts            → thấy tổng log, tổng alert, top users, filter hint/model/status
/alerts/<id>       → thấy feature nổi bật và log gốc
```

User thường test:

```text
Đăng nhập user1 → truy cập /alerts → phải bị 403 hoặc redirect/chặn
```

Commit:

```powershell
git add app/blueprints/alerts app/templates/alerts app/services/detection_service.py
git commit -m "feat: add integrated alert dashboard"
```

---

## Thứ Ba 14/07 — Ổn định reset/demo scripts và cài lại

### File cần kiểm tra

- `scripts/reset_demo.py`
- `scripts/run_demo_scenario.py`
- `README.md`

### Cách test 2 vòng demo

```powershell
python -m scripts.reset_demo
python -m scripts.run_demo_scenario --scenario all --fast --normal-requests 300
python -m scripts.run_demo_scenario --scenario all --fast --normal-requests 300 --skip-reset
```

PASS khi:

- không lỗi path Windows
- không lỗi model thiếu sau khi train
- không duplicate alert không kiểm soát
- README đủ lệnh chạy từ đầu

---

## Thứ Tư 15/07 — Regression test và CODE FREEZE

### Lệnh test code

```powershell
python -m pytest
python -m scripts.reset_demo
python run.py
```

### Test thủ công bắt buộc

USER flow:

1. Login `user1`.
2. My Drive → upload/list/search/detail/download.
3. Share file cho user2.
4. Export CSV.
5. Delete → Trash → Restore.

VIEWER flow:

1. Login `user2`.
2. Mở **Được chia sẻ với tôi**.
3. View/download file được share.
4. Thử rename/delete/share → phải bị chặn.

ADMIN flow:

1. Login `admin`.
2. `/admin/users` khóa/mở user.
3. `/admin/files` lọc owner/extension/deleted.
4. `/admin/logs` lọc/export.
5. `/alerts` run detection, mở detail.

Tạo file:

```powershell
New-Item -Force docs\regression_test_report.md
```

Commit/tag:

```powershell
git add .
git commit -m "test: freeze web logging ml regression"
git tag code-freeze-2026-07-15
```

---

## Thứ Năm 16/07 — Hoàn thiện báo cáo

### Checklist nội dung

- Chương 1: lý do, mục tiêu, phạm vi StudyDrive + ML.
- Chương 2: Auth, Authorization, CSRF, IDOR/BOLA, logging, anomaly detection, Isolation Forest.
- Chương 3: kiến trúc, DB, use case, route, phân quyền, log schema, dữ liệu, feature.
- Chương 4: cài đặt, simulator, feature engineering, tuning, metrics, dashboard alert.
- Chương 5: kết quả đạt được, hạn chế, hướng phát triển.

### File số liệu cần chèn

```text
artifacts/metrics/test_metrics.json
artifacts/metrics/scenario_metrics.csv
artifacts/metrics/confusion_matrix.png
artifacts/metrics/score_distribution.png
artifacts/figures/eda_features_v1/*.png
```

PASS khi báo cáo không còn TODO và số liệu khớp file metrics.

---

## Thứ Sáu 17/07 — Slide và kịch bản demo

### Tạo file

```powershell
New-Item -Force docs\DEMO_SCRIPT.md
```

### Dàn slide 12–15 trang

1. Tên đề tài.
2. Vấn đề và mục tiêu.
3. Scope StudyDrive.
4. Use case user/admin.
5. Kiến trúc tổng thể.
6. Cơ chế auth/authorization.
7. Structured logging.
8. Dữ liệu mô phỏng và ground truth.
9. Feature engineering theo window.
10. Isolation Forest và threshold.
11. Kết quả tổng.
12. Detection rate theo scenario.
13. Dashboard alert.
14. Hạn chế.
15. Kết luận.

PASS khi thuyết trình thử 8–12 phút và demo không quá dài.

---

## Thứ Bảy 18/07 — Diễn tập, quay video và đóng gói candidate

### Lệnh rehearsal

```powershell
python -m scripts.reset_demo
python run.py
python -m scripts.run_demo_scenario --scenario all --fast --normal-requests 500
```

### Gói candidate

Không đưa `.env`, `.venv`, `__pycache__`, `.git`, mật khẩu thật vào ZIP.

PowerShell gợi ý:

```powershell
Compress-Archive -Path app,ml,scripts,docs,data,artifacts,tests,README.md,requirements.txt,run.py,pytest.ini -DestinationPath submission_candidate.zip -Force
```

PASS khi giải nén ZIP thử ở thư mục khác vẫn thấy README, code, data sample, model, metrics, docs.

---

## Chủ Nhật 19/07 — Tổng kiểm tra và hoàn thành

### Checklist cuối

```powershell
python -m pytest
python -m scripts.reset_demo
python -m scripts.run_demo_scenario --scenario all --fast --normal-requests 300
```

Kiểm tra artifact:

```text
Source: app/, scripts/, ml/, tests/
Data: data/raw/request_logs_raw.csv, data/raw/ground_truth.csv, data/processed/features_v1/
Model: artifacts/models/iforest_v1/model.joblib
Metrics: artifacts/metrics/test_metrics.json, scenario_metrics.csv, test_predictions.csv
Docs: README.md, báo cáo, slide, DEMO_SCRIPT.md, regression_test_report.md
Ảnh/video: confusion matrix, score distribution, EDA, ảnh web/log/alert
```

Tạo bản nộp cuối:

```powershell
Compress-Archive -Path app,ml,scripts,docs,data,artifacts,tests,README.md,requirements.txt,run.py,pytest.ini -DestinationPath final_submission_2026-07-19.zip -Force
Get-FileHash final_submission_2026-07-19.zip -Algorithm SHA256
```

Tag:

```powershell
git add .
git commit -m "release: final studydrive anomaly detection project"
git tag final-2026-07-19
```

PASS khi:

- ZIP mở được
- không có secret
- README chạy được từ đầu
- alert truy ngược về log gốc được
- báo cáo/slide/video thống nhất cùng model/dataset version
