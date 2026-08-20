# 📚 Kiến Trúc & Cơ Chế Hoạt Động — Web Anomaly Detection

> **Đồ án:** Hệ thống phát hiện hành vi bất thường trên web (StudyDrive)
> **Stack chính:** Flask · SQLAlchemy · Isolation Forest (scikit-learn) · Pandas
> **Cập nhật:** 2026-08-19

---

## 📋 Mục Lục

1. [Tổng Quan Hệ Thống](#1-tổng-quan-hệ-thống)
2. [Luồng Thu Thập Log](#2-luồng-thu-thập-log)
3. [Cơ Chế Phát Hiện Bất Thường (ML Pipeline)](#3-cơ-chế-phát-hiện-bất-thường-ml-pipeline)
4. [Feature Engineering Chi Tiết](#4-feature-engineering-chi-tiết)
5. [Model: Isolation Forest](#5-model-isolation-forest)
6. [Luồng Inference Trên Web](#6-luồng-inference-trên-web)
7. [Active Defense & Alert](#7-active-defense--alert)
8. [Simulator & Dữ Liệu Huấn Luyện](#8-simulator--dữ-liệu-huấn-luyện)
9. [Sơ Đồ Kiến Trúc Tổng Thể](#9-sơ-đồ-kiến-trúc-tổng-thể)
10. [Sơ Đồ Luồng Dữ Liệu ML](#10-sơ-đồ-luồng-dữ-liệu-ml)
11. [Câu Hỏi Thường Gặp](#11-câu-hỏi-thường-gặp)

---

## 1. Tổng Quan Hệ Thống

Hệ thống gồm **hai tầng** tách biệt nhưng tích hợp chặt chẽ:

| Tầng | Mô tả | Thư mục |
|------|-------|---------|
| **Web App** | Flask app đóng vai trò "StudyDrive" — nền tảng chia sẻ tài liệu giả lập | `app/` |
| **ML Pipeline** | Thu thập log → Feature Engineering → Train → Detect | `ml/` |

**Triết lý thiết kế:**
- Log chỉ lưu **metadata** (không lưu nội dung file, password, cookie, body request)
- ML dùng kiến trúc **unsupervised** (Isolation Forest) → không cần nhãn để train, chỉ cần normal traffic
- Train set = **chỉ gồm normal window** → anomaly tự nhiên bị cô lập bởi model

---

## 2. Luồng Thu Thập Log

### 2.1 Middleware Ghi Log (Automatic — mọi request)

```
Client gửi Request
        │
        ▼
┌─────────────────────────────────┐
│  before_request hook            │
│  • Gán request_id (UUID hex)    │
│  • Ghi g.request_start_time     │
└─────────────────────────────────┘
        │
        ▼
  [Xử lý nghiệp vụ Flask]
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  after_request hook  (request_logging.py)           │
│  • Tính response_time_ms                            │
│  • Gắn X-Request-ID vào header                     │
│  • Gọi save_request_log(response, time_ms)          │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────┐
│  log_service.build_request_log()                       │
│                                                        │
│  resolve_action(endpoint, method)                      │
│    → "download_file" / "delete_file" / ...             │
│                                                        │
│  resolve_action_type(endpoint, method)                 │
│    → "view_detail" / "delete" / "export" / ...        │
│                                                        │
│  resolve_resource(endpoint, view_args)                 │
│    → resource_type="file", resource_id="42"           │
│                                                        │
│  resolve_resource_context(resource_type, resource_id,  │
│                           user_id, role)               │
│    → ownership_result: OWNER / VIEWER / NONE /        │
│                        NOT_FOUND / ADMIN / ANONYMOUS  │
│    → permission: OWNER / VIEWER / NONE / ADMIN        │
│                                                        │
│  is_sensitive_request(...)                             │
│    → True nếu: export/delete/admin/view_detail bị từ  │
│               chối hoặc không có quyền (IDOR hint)    │
└────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  save_request_log()             │
│  • Dùng isolated SQLAlchemy     │
│    session (không ảnh hưởng     │
│    DB session nghiệp vụ chính)  │
│  • Commit vào bảng request_logs │
└─────────────────────────────────┘
```

### 2.2 Bảng `request_logs` — Schema đầy đủ

| Cột | Kiểu | Ý nghĩa |
|-----|------|---------|
| `id` | Integer PK | Auto-increment |
| `request_id` | String(64) UNIQUE | UUID hex, dùng để tương quan log |
| `timestamp` | DateTime(tz=UTC) | Thời điểm request |
| `user_id` | FK → users | NULL nếu anonymous |
| `is_authenticated` | Boolean | Đã đăng nhập? |
| `role` | String(20) | USER / ADMIN |
| `session_id_hash` | String(128) | Hash của session Flask để nhóm cùng phiên |
| `ip_address` | String(45) | IPv4/IPv6, lấy từ access_route[0] |
| `user_agent` | String(512) | Browser/client string |
| `http_method` | String(10) | GET / POST / DELETE / ... |
| `endpoint` | String(255) | Flask endpoint name (e.g. `documents.download_file`) |
| `path` | String(1024) | URL path (không gồm query string) |
| `action` | String(80) | Tên hành động chi tiết cho admin đọc |
| `action_type` | String(80) | **Nhóm ML**: login/list/create/view_detail/edit/export/delete/restore/admin/other |
| `is_sensitive` | Boolean | Flag cho ML: request đáng chú ý |
| `resource_type` | String(50) | file / folder / user / share |
| `resource_id` | String(100) | ID của resource bị tác động |
| `owner_id` | Integer | ID chủ sở hữu resource |
| `permission` | String(20) | Quyền của user với resource này |
| `ownership_result` | String(20) | OWNER/VIEWER/NONE/NOT_FOUND/ADMIN/ANONYMOUS/UNKNOWN |
| `authorization_result` | String(20) | allowed / denied / error |
| `status_code` | Integer | HTTP status code (200/403/404/...) |
| `response_time_ms` | Float | Thời gian xử lý (ms) |
| `file_size` | BigInteger | Kích thước file nếu có |
| `export_item_count` | Integer | Số item trong export |
| `export_total_size` | BigInteger | Tổng kích thước export |

**Index được tạo sẵn:**
- `(user_id, timestamp)` — lọc log theo user theo thời gian
- `(session_id_hash, timestamp)` — nhóm theo phiên
- `(action_type, timestamp)` — lọc theo loại hành động
- `(status_code, timestamp)` — lọc theo kết quả HTTP
- `(session_id_hash, action_type, status_code)` — truy vấn composite cho ML
- `(resource_type, resource_id)` — tìm theo tài nguyên
- `(is_sensitive, timestamp)` — lọc nhanh request nhạy cảm

### 2.3 Phân Loại `action_type` (Buckets cho ML)

```
action_type     Endpoint ví dụ
─────────────   ──────────────────────────────────
login           auth.login, auth.register, auth.logout
list            documents.index, documents.trash, dashboard
create          documents.upload_file, documents.create_folder
view_detail     documents.file_detail, documents.download_file
edit            documents.rename_file, documents.move_file, documents.share_file
export          documents.export_files_csv
delete          documents.delete_file, documents.permanent_delete_file
restore         documents.restore_file
admin           admin.*, alerts.*
other           Mọi endpoint không khớp
```

### 2.4 Quy Tắc `is_sensitive`

Request được đánh dấu `is_sensitive = True` khi:
1. `action_type` ∈ `{export, delete, restore, admin}` — **luôn nhạy cảm**
2. Endpoint bắt đầu bằng `admin.` hoặc `alerts.`
3. `action_type == "view_detail"` VÀ bị từ chối (`authorization_result == "denied"`) HOẶC không có quyền (`ownership_result` ∈ `{NONE, NOT_FOUND, ANONYMOUS}`) — **IDOR / BOLA attempt**

---

## 3. Cơ Chế Phát Hiện Bất Thường (ML Pipeline)

Pipeline gồm **5 giai đoạn** liên tiếp:

```
[RAW CSV LOG]
      │
      ▼ ml.build_features
  (1) clean_logs()           — Làm sạch, chuẩn hóa dtype
      │
      ▼
  (2) attach_ground_truth()  — Gán nhãn label/scenario (chỉ dùng để đánh giá)
      │
      ▼
  (3) assign_windows()       — Phân cửa sổ 5 phút / user / session
      │
      ▼
  (4) aggregate_features()   — Tổng hợp 25 feature mỗi window
      │
      ▼
  (5) split_features()       — Chia train/validation/test
      │
      ▼ ml.train
  (6) train_one() / tune_model()  — Fit Isolation Forest
      │
      ▼ ml.detect
  (7) predict_feature_dataframe() — Tính anomaly_score, ngưỡng
      │
      ▼ ml.evaluate
  (8) compute_metrics() + plot   — Báo cáo P/R/F1, confusion matrix
```

### 3.1 Bước (1): Làm Sạch Log (`clean_logs`)

| Thao tác | Chi tiết |
|----------|----------|
| Parse timestamp | `pd.to_datetime(..., utc=True)`, bỏ row invalid |
| Dedup request_id | Giữ first, bỏ duplicate |
| Chuẩn hóa numeric | `user_id`, `status_code`, `response_time_ms`, `file_size` |
| Chuẩn hóa bool | `is_authenticated`, `is_sensitive`: nhận "1/true/yes/on/t/y" |
| Fill string | `role=""` → `"ANONYMOUS"`, `action_type=""` → `"other"` |
| Normalize resource_id | Bỏ ".0" float suffix, xử lý NaN → "" |
| Sắp xếp | Theo `user_id → session_id_hash → timestamp → request_id` |

### 3.2 Bước (2): Gán Ground Truth (`attach_ground_truth`)

- Đọc file `ground_truth.csv` từ simulator
- Mỗi dòng ground truth có: `user_id`, `started_at`, `ended_at`, `label` (0/1), `scenario`, `severity`
- Gán nhãn cho từng log row dựa trên **user_id** và **khoảng thời gian**
- Ưu tiên: **anomaly ghi đè normal** khi có overlap (sort by label asc trước)
- **Nhãn KHÔNG được dùng làm feature ML** — chỉ dùng để đánh giá sau

### 3.3 Bước (3): Phân Cửa Sổ Thời Gian (`assign_windows`)

```python
WINDOW_MINUTES = 5  # Cố định 5 phút

window_start = timestamp.floor("5min")   # VD: 14:17:32 → 14:15:00
window_end   = window_start + 5min       # → 14:20:00
window_id    = SHA1(f"{user_id}|{session_id_hash}|{window_start.isoformat()}")[:16]
```

**Đơn vị phân tích** = `(user_id, session_id_hash, 5-minute block)`

Ý nghĩa: Mọi request của cùng 1 user trong cùng 1 session trong cùng 1 khung 5 phút → **1 row trong feature matrix**.

### 3.4 Bước (4): Tổng Hợp Feature (`aggregate_features`)

Xem Mục 4 bên dưới.

### 3.5 Bước (5): Chia Train/Val/Test (`split_features`)

**Chiến lược chia theo group (không theo row):**

```
Group = run_id  (nếu có >= 3 run khác nhau)
      = user_id|session_id_hash  (fallback)

Normal groups → sắp xếp theo thời gian → train 60% / val 20% / test 20%
Anomaly groups → xáo trộn ngẫu nhiên → val 50% / test 50%

Train set → chỉ giữ normal (label=0)
           nếu lẫn anomaly → chuyển sang val
```

**Lý do:** Isolation Forest học "bình thường trông như thế nào", nên train set **không được có anomaly**. Group-aware split ngăn data leakage giữa các phiên của cùng user.

---

## 4. Feature Engineering Chi Tiết

### 4.1 Toàn Bộ 25 Feature

Tất cả feature được tính trên đơn vị **1 window = (user, session, 5 phút)**:

#### Nhóm Traffic Cơ Bản

| Feature | Công thức / Ý nghĩa |
|---------|---------------------|
| `request_count` | `len(window)` — tổng số request |
| `unique_endpoint_count` | Số endpoint Flask khác nhau |
| `unique_method_count` | Số HTTP method khác nhau |
| `session_duration_sec` | `max(timestamp) - min(timestamp)` trong window |
| `avg_inter_request_sec` | Trung bình khoảng cách giữa các request liên tiếp |
| `min_inter_request_sec` | Khoảng cách nhỏ nhất giữa 2 request liên tiếp |
| `burst_rate` | `count(inter_request <= 1s) / count(inter_request)` |
| `avg_response_time_ms` | Trung bình thời gian xử lý |
| `error_rate` | `count(status >= 400) / request_count` |

#### Nhóm Hành Vi Nhạy Cảm

| Feature | Công thức / Ý nghĩa |
|---------|---------------------|
| `sensitive_request_count` | `count(is_sensitive == True)` |
| `sensitive_ratio` | `sensitive_request_count / request_count` |
| `max_sensitive_streak` | Chuỗi liên tiếp `is_sensitive=True` dài nhất |

#### Nhóm Export / Download Hàng Loạt

| Feature | Công thức / Ý nghĩa |
|---------|---------------------|
| `export_count` | `count(action_type=="export" OR "export" in action)` |
| `export_ratio` | `export_count / request_count` |

#### Nhóm Xóa Hàng Loạt

| Feature | Công thức / Ý nghĩa |
|---------|---------------------|
| `delete_count` | `count(action_type=="delete" OR "delete" in action)` |
| `delete_ratio` | `delete_count / request_count` |
| `unique_deleted_resource_count` | Số resource_id khác nhau bị delete |

#### Nhóm Quét Tài Nguyên (BOLA / IDOR Scan)

| Feature | Công thức / Ý nghĩa |
|---------|---------------------|
| `unique_resource_id_count` | Số resource_id khác nhau xuất hiện |
| `resource_id_request_ratio` | `unique_resource_id_count / request_count` |
| `resource_id_change_rate` | Tỷ lệ resource_id thay đổi giữa 2 request liên tiếp |
| `forbidden_count` | `count(status == 403)` |
| `forbidden_rate` | `forbidden_count / request_count` |
| `not_found_count` | `count(status == 404)` |
| `not_found_rate` | `not_found_count / request_count` |
| `unique_failed_resource_id_count` | Số resource_id khác nhau trong 403/404 request |

### 4.2 Feature → Scenario Mapping (Intuition)

```
Scenario          Feature nổi bật
──────────────    ──────────────────────────────────────────────────
bola_scan         unique_failed_resource_id_count tăng cao
                  forbidden_rate tăng cao
                  not_found_rate tăng cao
                  resource_id_change_rate tăng cao

export_abuse      export_count tăng cao
                  export_ratio tăng cao
                  sensitive_ratio tăng cao

delete_abuse      delete_count tăng cao
                  delete_ratio tăng cao
                  unique_deleted_resource_count tăng cao

resource_probe    unique_resource_id_count tăng cao
                  sensitive_ratio tăng vừa

normal            Tất cả thấp, burst_rate thấp, error_rate thấp
```

### 4.3 Hàm Tiện Ích Feature

```python
_safe_ratio(numerator, denominator)
  # Trả 0.0 nếu denominator == 0 → không bao giờ có inf/NaN

_max_true_streak(values)
  # Đếm chuỗi True liên tiếp dài nhất trong list bool

_resource_change_rate(resource_ids)
  # count(resource_ids[i] != resource_ids[i-1]) / (n-1)
```

---

## 5. Model: Isolation Forest

### 5.1 Nguyên Lý Hoạt Động

**Isolation Forest** phát hiện dị thường bằng cách **cô lập** điểm dữ liệu:

```
Ý tưởng:
  - Xây dựng nhiều cây nhị phân ngẫu nhiên (random trees)
  - Mỗi cây: chọn ngẫu nhiên 1 feature và 1 ngưỡng để split
  - Điểm dị thường ít tương đồng với đa số → bị cô lập sớm hơn
                   → path length ngắn hơn trong cây
  - Anomaly score = 1/avg(path_length) qua tất cả cây
  - Điểm bình thường → nằm sâu trong cây → path dài → score thấp
  - Điểm bất thường → bị cô lập sớm → path ngắn → score cao
```

**Ưu điểm cho bài toán này:**
- Không cần nhãn anomaly để train (unsupervised)
- Hiệu quả với không gian chiều cao (25 features)
- Không nhạy cảm với outlier trong train set (nếu train set clean)
- Phát hiện được anomaly mới chưa từng thấy

### 5.2 Tham Số Mặc Định

```python
IsolationForest(
    n_estimators=200,       # Số cây (grid search: 100/200/300)
    max_samples="auto",     # Số sample/cây (grid search: "auto"/256)
    contamination="auto",   # Không đặt contamination thực — dùng percentile
    random_state=20260706,
    n_jobs=-1,              # Song song toàn bộ CPU
)
```

### 5.3 Cách Chọn Ngưỡng (Threshold)

```python
# Bước 1: Train model trên normal_train
model.fit(X_train_normal)

# Bước 2: Tính anomaly_score trên chính train set
train_scores = -model.score_samples(X_train)
# score_samples trả âm → đảo dấu → "càng cao càng bất thường"

# Bước 3: Chọn ngưỡng = percentile thứ P của train score
# Mặc định P = 95 → top 5% score trên normal traffic
threshold = np.percentile(train_scores, 95)

# Bước 4: Inference
y_pred = (score >= threshold).astype(int)  # 1 = anomaly, 0 = normal
```

**Grid search percentile:** `[90.0, 92.5, 95.0, 97.5]`

**Metric tối ưu (theo thứ tự ưu tiên):**
1. F1 cao nhất
2. False Positive Rate thấp nhất
3. Recall cao nhất

### 5.4 Lưu Model Artifact

```
artifacts/models/iforest_v1/
├── model.joblib          # joblib.dump({model, feature_list, threshold, metadata})
├── model_metadata.json   # Tham số, ngưỡng, metric train/val
├── feature_list.json     # Danh sách 25 feature theo thứ tự đúng
└── baseline_metrics.json # Bản sao metadata
```

---

## 6. Luồng Inference Trên Web

### 6.1 Khi Nào Detection Chạy?

Detection **không chạy tự động real-time**. Admin kích hoạt thủ công từ trang `/alerts/` (on-demand batch detection).

```
Admin click "Chạy Detection"
        │
        ▼
detection_service.run_detection(start, end, model_path)
        │
        ├─ query_logs(start, end)          Đọc từ DB
        │
        ├─ request_logs_to_dataframe()     ORM → DataFrame
        │
        ├─ build_features_from_logs_dataframe()
        │    ├─ clean_logs()
        │    ├─ assign_windows()
        │    └─ aggregate_features()
        │
        ├─ load_detector(model_path)       Load model.joblib
        │
        ├─ predict_feature_dataframe()
        │    ├─ anomaly_scores()           -model.score_samples(X)
        │    ├─ threshold comparison       score >= threshold → anomaly
        │    ├─ scenario_hint_from_row()   Rule-based hint
        │    └─ top_feature_deltas()       Top 5 feature values cao nhất
        │
        └─ Lưu Alert vào DB
             Kiểm tra duplicate (window_id + model_version)
             Tạo Alert row: score, scenario_hint, features_json
             Active Defense: khóa user nếu score > 0.7
                             hoặc scenario trong {bola_scan, export_abuse, delete_abuse}
```

### 6.2 Scenario Hint (Rule-based, Không Phải ML)

```python
def scenario_hint_from_row(row):
    if export_count >= 3 or export_ratio >= 0.25:
        return "export_abuse"
    if delete_count >= 3 or delete_ratio >= 0.25:
        return "delete_abuse"
    if unique_failed >= 3 or (forbidden_rate + not_found_rate) >= 0.30:
        return "bola_scan"
    if unique_resource >= 8 and sensitive_ratio >= 0.20:
        return "resource_probe"
    return "general_anomaly"
```

Đây là **heuristic giải thích sau detection**, không phải output ML. Model chỉ nói "có bất thường", hint giải thích "có thể là loại tấn công nào".

---

## 7. Active Defense & Alert

### 7.1 Bảng `alerts`

| Cột | Ý nghĩa |
|-----|---------|
| `window_id` | ID cửa sổ (SHA1 hash) — unique key |
| `window_start/end` | Khoảng thời gian cửa sổ |
| `model_version` | `iforest_v1` |
| `anomaly_score` | Score từ Isolation Forest (càng cao càng nguy hiểm) |
| `scenario_hint` | bola_scan / export_abuse / delete_abuse / resource_probe / general_anomaly |
| `features_json` | JSON: top_features + các metric chính |
| `status` | NEW / REVIEWING / RESOLVED / FALSE_POSITIVE |
| `admin_notes` | Ghi chú khi Admin xử lý alert |

**Ràng buộc:** `UNIQUE(window_id, model_version)` → Không tạo trùng alert cho cùng 1 cửa sổ.

### 7.2 Active Defense Logic

```python
# Trong detection_service.run_detection()
if alert.anomaly_score > 0.7:
    user.locked_until = now() + 60 phút
elif alert.scenario_hint in ("bola_scan", "export_abuse", "delete_abuse"):
    user.locked_until = now() + 60 phút

# Điều kiện bổ sung: user.is_admin == False (Admin không bị khóa)
```

### 7.3 Check Active Defense (Mọi Request)

```python
# app/middleware/active_defense.py — chạy trước mọi request
def check_active_defense():
    if request.endpoint == 'auth.logout':
        return  # Cho phép logout dù bị khóa

    if g.current_user and g.current_user.is_locked:
        abort(403, "Tài khoản bị khóa tạm thời do phát hiện hành vi bất thường")
```

`is_locked` = property trên model User: `locked_until > datetime.now(UTC)`.

---

## 8. Simulator & Dữ Liệu Huấn Luyện

### 8.1 Tại Sao Cần Simulator?

Dữ liệu thực không có nhãn anomaly. Simulator tạo ra:
- **Normal traffic**: hành vi người dùng bình thường (browse, download, upload)
- **Attack traffic**: mô phỏng 3 kịch bản tấn công có nhãn rõ ràng
- **Ground truth CSV**: ghi lại chính xác user nào, khoảng thời gian nào bị đánh dấu

### 8.2 Các Kịch Bản Tấn Công

| Script | Kịch bản | Hành vi mô phỏng |
|--------|----------|-----------------|
| `simulate_bola_scan.py` | BOLA Scan | Brute-force file_id theo tuần tự, truy cập file không thuộc quyền → nhiều 403/404 |
| `simulate_export_abuse.py` | Export Abuse | Gọi export hàng loạt liên tiếp trong thời gian ngắn |
| `simulate_delete_abuse.py` | Delete Abuse | Xóa nhiều file liên tiếp |
| `simulate_normal.py` | Normal | Browse folder, xem file, download, upload, chia sẻ bình thường |

### 8.3 Cách Simulator Ghi Ground Truth

```python
# simulator_common.append_ground_truth()
# Ghi vào data/raw/ground_truth.csv
{
    "scenario_id": "bola_20260705_143022_0",
    "scenario": "bola_scan",
    "label": 1,           # 0=normal, 1=anomaly
    "run_id": "bola_20260705_143022",
    "user_id": 3,
    "username": "alice",
    "session_name": "bola_session_1",
    "severity": "high",
    "started_at": "2026-07-05T14:30:22+00:00",
    "ended_at":   "2026-07-05T14:35:18+00:00",
    "request_count": 47,
    "notes": "Quét 47 file_id không thuộc quyền"
}
```

### 8.4 Export Log Thủ Công

```bash
# Xuất log từ DB ra CSV để chạy ML pipeline
python scripts/export_logs.py --output data/raw/request_logs_raw.csv

# Hoặc qua web: Admin → Logs → Export CSV
```

---

## 9. Sơ Đồ Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────────────────────────────┐
│                          WEB LAYER (Flask)                          │
│                                                                     │
│  Browser ──→ blueprints/                                            │
│               auth / documents / admin / alerts                     │
│                    │                                                │
│               middleware/                                           │
│               request_logging.py  ──→  log_service.py              │
│               active_defense.py                                     │
│                    │                                                │
│               models/                                               │
│               RequestLog  Alert  User  StoredFile  Folder           │
│                    │                                                │
│               [SQLite DB]  (instance/app.db)                        │
└────────────────────┬────────────────────────────────────────────────┘
                     │  export CSV (scripts/export_logs.py)
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         ML LAYER (Offline)                          │
│                                                                     │
│  data/raw/request_logs_raw.csv                                      │
│  data/raw/ground_truth.csv                                          │
│       │                                                             │
│       ▼  python -m ml.build_features                                │
│  data/processed/features_v1/                                        │
│       ├─ clean_logs.csv                                             │
│       ├─ features_all.csv       (25 features per window)           │
│       ├─ train_features.csv     (normal only)                      │
│       ├─ validation_features.csv                                    │
│       └─ test_features.csv                                          │
│       │                                                             │
│       ▼  python -m ml.train --tune                                  │
│  artifacts/models/iforest_v1/                                       │
│       ├─ model.joblib                                               │
│       └─ model_metadata.json                                        │
│       │                                                             │
│       ▼  python -m ml.evaluate                                      │
│  artifacts/metrics/                                                 │
│       ├─ test_predictions.csv                                       │
│       ├─ test_metrics.json                                          │
│       ├─ confusion_matrix.png                                       │
│       └─ score_distribution.png                                     │
└─────────────────────────────────────────────────────────────────────┘
                     │  model.joblib được load khi detect
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DETECTION SERVICE (On-demand)                    │
│                                                                     │
│  detection_service.run_detection()                                  │
│       • Đọc log từ DB (không từ CSV)                                │
│       • Build features giống pipeline offline                       │
│       • Load model.joblib                                           │
│       • Ghi Alert vào DB                                            │
│       • Khóa user nếu nguy hiểm cao                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 10. Sơ Đồ Luồng Dữ Liệu ML

```
REQUEST LOG (1 dòng = 1 HTTP request)
   request_id, timestamp, user_id, session_id_hash,
   action_type, is_sensitive, resource_id, status_code, ...
        │
        │ group by (user_id, session_id_hash, 5-min window)
        ▼
WINDOW FEATURE ROW (1 dòng = 1 cửa sổ 5 phút)
   window_id, user_id, session_id_hash,
   window_start, window_end,
   [25 FEATURES], label, scenario
        │
        ├──── train set (normal only, label=0)
        │         │
        │         ▼
        │    IsolationForest.fit(X_train_normal)
        │    threshold = percentile(train_scores, 95)
        │
        ├──── val set (normal + anomaly)
        │         │
        │         ▼
        │    Tune threshold percentile [90/92.5/95/97.5]
        │    Chọn best theo (F1, FPR, Recall)
        │
        └──── test set (holdout, không chạm khi train/tune)
                  │
                  ▼
             Evaluate: Precision/Recall/F1
             Confusion Matrix, Score Distribution Plot
```

---

## 11. Câu Hỏi Thường Gặp

### Q: Tại sao không dùng supervised model?

**A:** Anomaly trong thực tế rất hiếm và đa dạng. Không có đủ nhãn thực tế. Isolation Forest học "normal trông như thế nào" — bất kỳ thứ gì khác biệt đủ nhiều đều bị cô lập. Kịch bản mới chưa từng thấy vẫn có thể bị phát hiện.

### Q: Tại sao window = 5 phút?

**A:** Đủ ngắn để bắt burst attack (BOLA scan thường xảy ra trong vài phút), đủ dài để tích lũy đủ request cho feature có ý nghĩa thống kê. Giá trị có thể điều chỉnh qua `--window-minutes`.

### Q: Ngưỡng 95 percentile có nghĩa gì?

**A:** Train model trên normal traffic, sau đó nói "top 5% score của normal traffic là ngưỡng". Bất kỳ window nào có score cao hơn → bị coi là anomaly. FPR trên train ≈ 5%, thực tế có thể thấp hơn nếu distribution val/test khác train.

### Q: `scenario_hint` có phải output ML không?

**A:** **Không.** Đây là rule-based heuristic sau khi model đã quyết định "anomaly". Nó giải thích "tại sao bị flag", không phải là quyết định của model. Model chỉ nói 0/1.

### Q: Sự khác biệt giữa offline pipeline và online detection?

**A:**
- **Offline pipeline** (`ml/`): dùng CSV file, thường chạy batch để train/evaluate
- **Online detection** (`detection_service`): đọc trực tiếp từ SQLAlchemy ORM, chạy khi admin bấm nút
- **Feature engineering giống nhau hoàn toàn**: cả hai đều gọi `aggregate_features()` từ `ml.build_features`

### Q: Ground truth dùng để làm gì?

**A:** Chỉ dùng để **đánh giá** (evaluate). Simulator ghi lại khoảng thời gian và user nào đang chạy attack. Label được gán vào features để tính P/R/F1. Label **không bao giờ** đưa vào X_train.

### Q: Tại sao dùng isolated session cho logging?

**A:** Nếu dùng cùng `db.session` với request, một rollback do lỗi nghiệp vụ sẽ xóa cả log. Isolated session đảm bảo log luôn được commit độc lập, không ảnh hưởng và không bị ảnh hưởng bởi transaction chính.

### Q: Top feature deltas có phải SHAP không?

**A:** **Không.** Đây chỉ là các feature có giá trị tuyệt đối lớn nhất trong window bị flag — hiển thị để admin hiểu "request count cao vì sao, export nhiều thế nào". Không phải giá trị SHAP (Shapley values). Đơn giản và minh bạch hơn SHAP.

---

## Tham Chiếu File Nhanh

| File | Vai trò |
|------|---------|
| `app/middleware/request_logging.py` | Hook before/after request, ghi log |
| `app/services/log_service.py` | Logic xây dựng RequestLog row |
| `app/models/request_log.py` | ORM model bảng `request_logs` |
| `app/models/alert.py` | ORM model bảng `alerts` |
| `app/services/detection_service.py` | Online detection + ghi Alert + Active Defense |
| `ml/build_features.py` | Feature engineering pipeline (CLI + library) |
| `ml/train.py` | Train + tune Isolation Forest |
| `ml/detect.py` | Load model + predict + scenario hint |
| `ml/evaluate.py` | Metric + confusion matrix + score distribution plot |
| `scripts/simulator_common.py` | Shared simulator helpers, ground truth writer |
| `scripts/simulate_bola_scan.py` | Mô phỏng BOLA / IDOR scan attack |
| `scripts/simulate_export_abuse.py` | Mô phỏng export hàng loạt |
| `scripts/simulate_delete_abuse.py` | Mô phỏng delete hàng loạt |
| `scripts/simulate_normal.py` | Mô phỏng hành vi người dùng bình thường |
| `scripts/export_logs.py` | Export DB request_logs → CSV |

---

*Tài liệu được tạo từ phân tích trực tiếp codebase ngày 2026-08-19. Cập nhật khi có thay đổi kiến trúc lớn.*
