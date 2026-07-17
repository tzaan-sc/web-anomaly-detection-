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

## Tuần 4 — Feature Engineering ✅ HOÀN THÀNH

| Hạng mục | Trạng thái |
|---|---|
| `ml/build_features.py` (28KB – pipeline đầy đủ) | ✅ |
| `ml/eda.py` | ✅ |
| `data/raw/request_logs_raw.csv` | ✅ đã sinh (5.500+ logs) |
| `data/processed/features_v1/` | ✅ đã xử lý và phân tách |
| `data/raw/ground_truth.csv` | ✅ đã sinh |

---

## Tuần 5 — Train & Integrate ML ✅ HOÀN THÀNH

| Hạng mục | Trạng thái |
|---|---|
| `ml/train.py` (IsolationForest pipeline) | ✅ |
| `ml/evaluate.py` | ✅ |
| `ml/detect.py` | ✅ |
| `app/services/detection_service.py` (8KB) | ✅ |
| `artifacts/models/iforest_v1/` | ✅ model.joblib đã train |
| `artifacts/metrics/` | ✅ test_metrics.json & tuning_results.csv |
| `artifacts/metrics/` (figures) | ✅ confusion_matrix.png & score_distribution.png |
| Alert blueprint + templates (index, detail) | ✅ |
| `scripts/run_detection.py`, `run_demo_scenario.py` | ✅ |

## Tuần 6 — Dashboard & nộp bài ✅ HOÀN THÀNH

| Hạng mục | Trạng thái |
|---|---|
| Dashboard alert tích hợp hoàn chỉnh | ✅ |
| ML Pipeline (Feature build -> Train -> Evaluate) | ✅ |
| Lưu vết Alert phát hiện bất thường vào DB | ✅ |
| Toàn bộ 38 test cases hoạt động hoàn chỉnh | ✅ |

---

## 🚨 Kế hoạch 7 ngày cuối (13–19/07)

```
13/07 → Chạy generate_raw_dataset_v1 → có data/raw/ ✅
13/07 → Chạy build_features → có data/processed/features_v1/ ✅
14/07 → Train model → artifacts/models/iforest_v1/model.joblib ✅
14/07 → Chạy evaluate → test_predictions.csv + figures ✅
15/07 → Dashboard alert hoàn chỉnh + run_detection tích hợp web ✅
16-17/07 → Toàn bộ 38 bài test tự động thông qua, cập nhật tiến độ ✅
18-19/07 → Git tag final + ZIP + backup 2 nơi 🔄 SẮP THỰC HIỆN
```

---

## Câu nói với giáo viên khi được hỏi

> *"Em đã hoàn thành toàn bộ đồ án. Phần web StudyDrive hoàn chỉnh (auth, folder, upload, share, trash, log, admin) hoạt động trơn tru. Hệ thống ML (build_features, train, evaluate, detect) dùng Isolation Forest đã được huấn luyện xong trên tập dataset 5.567 logs thực tế thu thập từ simulator. Các cảnh báo bất thường (Export Abuse, Delete Abuse, BOLA Scan) đã được tích hợp hiển thị đầy đủ trên Dashboard Alert của Admin. Em đã viết xong 38 bài test tự động cho toàn bộ ứng dụng và tất cả đều pass. Hiện tại em chuẩn bị nộp bài và chuẩn bị demo."*
