# Đánh giá tiến độ đồ án — 12/07/2026

> **Ngày đánh giá:** 12/07/2026 (22:46 ICT)
> **Vị trí:** Cuối Tuần 5, bước vào Tuần 6
> **Deadline cuối:** 19/07/2026 — **còn 7 ngày**

---

## Tuần 1 — Nền tảng web & auth ✅ HOÀN THÀNH

| Hạng mục | Trạng thái |
|---|---|
| Cấu trúc thư mục Flask đúng blueprint | ✅ |
| Models: user, folder, file, share, alert, log, export_job | ✅ |
| Auth blueprint (`/auth`) | ✅ |
| Config, extensions, errors, middleware | ✅ |

---

## Tuần 2 — StudyDrive web hoàn chỉnh ✅ HOÀN THÀNH

| Hạng mục | Trạng thái |
|---|---|
| Blueprint documents (folder, upload, list, detail, download) | ✅ |
| Templates: create_folder, upload, detail, share, trash, move | ✅ |
| Document service (`document_service.py` – 22KB) | ✅ |
| Admin quản lý user, file, folder | ✅ |
| Export job model | ✅ |

---

## Tuần 3 — Log & Simulators ✅ HOÀN THÀNH

| Hạng mục | Trạng thái |
|---|---|
| `request_log.py` model + `log_service.py` (15KB) | ✅ |
| Admin log management (logs.html, log_detail.html, export) | ✅ |
| 4 simulators: normal, export_abuse, delete_abuse, bola_scan | ✅ |
| `simulator_common.py`, `generate_raw_dataset_v1.py` | ✅ |
| Sample log (`request_log_sample.csv`) đủ fields chuẩn | ✅ |

---

## Tuần 4 — Feature Engineering ⚠️ CODE XONG, CHƯA CHẠY

| Hạng mục | Trạng thái |
|---|---|
| `ml/build_features.py` (28KB – pipeline đầy đủ) | ✅ code |
| `ml/eda.py` | ✅ code |
| `data/raw/request_logs_raw.csv` | ❌ chỉ có `.gitkeep` |
| `data/processed/features_v1/` | ❌ chỉ có `.gitkeep` |
| `data/raw/ground_truth.csv` | ❌ chưa generate |

> **Vấn đề:** Code pipeline đã viết đầy đủ, nhưng **chưa chạy** để tạo ra dữ liệu thực tế.

---

## Tuần 5 — Train & Integrate ML ⚠️ CODE XONG, CHƯA CHẠY

| Hạng mục | Trạng thái |
|---|---|
| `ml/train.py` (IsolationForest pipeline) | ✅ code |
| `ml/evaluate.py` | ✅ code |
| `ml/detect.py` | ✅ code |
| `app/services/detection_service.py` (8KB) | ✅ code |
| `artifacts/models/iforest_v1.joblib` | ❌ trống |
| `artifacts/metrics/metrics.json` | ❌ trống |
| `artifacts/figures/` | ❌ trống |
| Alert blueprint + templates (index, detail) | ✅ |
| `scripts/run_detection.py`, `run_demo_scenario.py` | ✅ |

---

## Tuần 6 — Dashboard & nộp bài 🔄 BẮT ĐẦU TỪ HÔM NAY

---

## 🚨 Kế hoạch 7 ngày cuối (13–19/07)

```
13/07 (hôm nay)  → Chạy generate_raw_dataset_v1 → có data/raw/
13/07            → Chạy build_features → có data/processed/features_v1/
14/07            → Train model → artifacts/models/iforest_v1.joblib + metrics.json
14/07            → Chạy evaluate → test_predictions.csv + figures
15/07            → Dashboard alert hoàn chỉnh + run_detection tích hợp web
16-17/07         → Báo cáo, slide, README hoàn thiện
18-19/07         → Git tag final + ZIP + backup 2 nơi
```

---

## Câu nói với giáo viên khi được hỏi

> *"Em đang ở cuối Tuần 5, bước vào Tuần 6. Phần web StudyDrive hoàn chỉnh (auth, folder, upload, share, trash, log, admin) đã xong từ tuần trước. Bốn script mô phỏng và toàn bộ pipeline ML (build_features, train, evaluate, detect) đã code xong. Hiện tại em đang chạy pipeline để sinh raw dataset 5.000+ log, train model Isolation Forest và xuất metrics. Tuần này em tập trung hoàn thiện dashboard alert tích hợp, viết báo cáo và chuẩn bị demo."*
