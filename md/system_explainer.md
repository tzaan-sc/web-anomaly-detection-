Kịch bản 1: Thầy hỏi "Em đang làm tới đâu rồi?"
"Dạ thầy, phần web StudyDrive em đã hoàn thiện xong — có đủ auth, upload file, chia sẻ, trash, và trang admin quản lý log. Phần ML em đã code xong pipeline build_features, train và evaluate, nhưng chưa chạy để ra model thật. Tuần này em đang tập trung chạy pipeline để có model.joblib và số liệu đánh giá, sau đó hoàn thiện dashboard alert và báo cáo."
---
✅ Tại sao an toàn: Đúng sự thật. Có kế hoạch cụ thể. Không nói quá, không nói thiếu.
---
Kịch bản 2: Thầy hỏi "Em hiểu hệ thống không?"
Đừng nói "hiểu" chung chung. Giải thích bằng luồng:

"Dạ, hệ thống có 3 tầng. Tầng web là StudyDrive Flask — mỗi request user thực hiện đều được middleware ghi tự động vào bảng request_logs trong MySQL. Tầng ML đọc log đó, chia thành cửa sổ 5 phút theo từng user/session, tính 24 feature thống kê như export_count, forbidden_rate, burst_rate rồi cho Isolation Forest chấm điểm. Cửa sổ nào vượt ngưỡng thì lưu Alert. Tầng cuối là Admin xem Alert trên dashboard."
---
Kịch bản 3: Thầy hỏi kỹ hơn "Isolation Forest hoạt động thế nào?"
"Dạ, Isolation Forest train chủ yếu bằng dữ liệu bình thường. Nguyên lý là dùng cây ngẫu nhiên cắt không gian feature — điểm bình thường nằm gần nhau nên cần nhiều bước cắt mới cô lập được, còn điểm bất thường nằm xa cụm nên bị cô lập nhanh hơn, cho anomaly score cao hơn. Em chọn threshold ở percentile 95 trên tập train để kiểm soát false positive."
---
Kịch bản 4: Thầy hỏi "Kết quả mô hình thế nào?"
Nếu chưa chạy xong — nói thật:

"Dạ em đang chạy pipeline, chưa có số liệu cuối. Dự kiến ngày mai em sẽ có Precision, Recall, F1 và FPR theo từng scenario để báo cáo thầy."

Sau khi chạy xong — nói số thật từ metrics.json.
---
Kịch bản 5: Thầy hỏi gì mà bạn không biết
Đừng bịa. Nói:

"Dạ phần đó em cần xem lại code, em sẽ trả lời thầy sau buổi này ạ."


---

# Giải thích hệ thống Web Anomaly Detection — Đọc để hiểu trước khi bảo vệ


> Viết theo kiểu "đọc một lần là hiểu", không cần biết code trước.

---

## 1. Hệ thống này làm gì? (Một câu)

Xây dựng một website lưu trữ file (như Google Drive thu nhỏ), và gắn thêm một bộ phát hiện hành vi bất thường bằng Machine Learning — khi user làm gì đó đáng ngờ, hệ thống tự phát cảnh báo cho Admin.

---

## 2. Luồng tổng thể (đọc từ trái sang phải)

```
User dùng web
    → Flask nhận request
        → Middleware tự động ghi log mỗi request vào MySQL
            → Admin xem log trên trang quản trị
                → Script chạy pipeline ML:
                    load log → tạo feature → Isolation Forest → lưu Alert
                        → Admin xem Alert trên dashboard
```

---

## 3. Giải thích từng phần

### 3.1. Web StudyDrive (phần "ứng dụng")

Là website để user upload, chia sẻ và quản lý file. Dùng Flask + Jinja2 + Bootstrap.

**Các chức năng có trong web:**

| Chức năng | URL | Vai trò |
|---|---|---|
| Đăng nhập / Đăng xuất | `/auth/login` | USER + ADMIN |
| Trang chính / dashboard | `/` | USER + ADMIN |
| Xem danh sách file/folder | `/documents/` | USER |
| Tạo folder mới | `/documents/folder/create` | USER |
| Upload file | `/documents/upload` | USER |
| Xem chi tiết file | `/documents/file/<id>` | OWNER/VIEWER |
| Download file | `/documents/file/<id>/download` | OWNER/VIEWER |
| Chia sẻ file | `/documents/file/<id>/share` | OWNER |
| Thùng rác / Xóa mềm | `/documents/trash` | USER |
| Trang Admin quản lý user/file | `/admin/` | ADMIN only |
| Trang Admin xem log | `/admin/logs` | ADMIN only |
| Trang Alerts (cảnh báo ML) | `/alerts/` | ADMIN only |

**Hai vai trò:**
- `USER`: dùng web bình thường
- `ADMIN`: xem thêm log, alerts, quản lý tất cả

---

### 3.2. Logging — Cốt lõi của đồ án

**Vấn đề cần giải thích được:** *"Sao hệ thống biết user làm gì?"*

**Trả lời:** Mỗi khi Flask xử lý xong một request, một đoạn code tên `request_logging.py` (middleware) tự động chạy và ghi thông tin vào bảng `request_logs` trong MySQL.

**File liên quan:**
- `app/middleware/request_logging.py` — hook `after_request`: đo thời gian → gọi `save_request_log()`
- `app/services/log_service.py` — hàm `save_request_log()`: phân tích request rồi lưu vào DB

**Mỗi dòng log ghi những gì:**

| Trường | Ý nghĩa | Ví dụ |
|---|---|---|
| `timestamp` | Lúc nào? | `2026-06-24 14:22:41` |
| `user_id` | Ai làm? | `2` (user_id=2) |
| `role` | Vai trò? | `USER` hoặc `ADMIN` |
| `session_id_hash` | Phiên làm việc nào? | hash SHA của session |
| `http_method` | GET hay POST? | `GET`, `POST`, `DELETE` |
| `endpoint` | Route nào? | `documents.download_file` |
| `action` | Hành động cụ thể? | `download_file`, `delete_file` |
| `action_type` | Nhóm hành động? | `export`, `delete`, `view_detail` |
| `is_sensitive` | Nhạy cảm không? | `True` nếu là export/delete/admin |
| `resource_type` | Tác động vào gì? | `file`, `folder` |
| `resource_id` | ID của gì? | `42` (file_id=42) |
| `authorization_result` | Được phép không? | `allowed` hoặc `denied` |
| `status_code` | Kết quả HTTP? | `200`, `403`, `404` |
| `response_time_ms` | Bao lâu? | `199.682` (ms) |

> **Nói với giáo viên:** "Mỗi request HTTP đều được ghi lại tự động nhờ Flask middleware, không cần dev nhớ ghi tay. Bảng `request_logs` là nguồn dữ liệu cho toàn bộ pipeline ML."

---

### 3.3. Bốn script mô phỏng hành vi

Vì đồ án chạy local, không có user thật, nên cần tạo dữ liệu giả nhưng thực tế.

| Script | Mô phỏng gì | Sao là "bất thường"? |
|---|---|---|
| `simulate_normal.py` | User bình thường: login → browse → download → logout | Bình thường |
| `simulate_export_abuse.py` | Export hàng loạt file trong thời gian ngắn | Export 50 file/5 phút là bất thường |
| `simulate_delete_abuse.py` | Xóa nhiều file liên tục | Delete 30 file/5 phút là bất thường |
| `simulate_bola_scan.py` | Truy cập file người khác theo ID tuần tự (IDOR) | Nhiều lỗi 403/404 liên tiếp từ 1 user |

> **BOLA = Broken Object Level Authorization** — Tấn công kiểu đoán ID, ví dụ thử `/file/1`, `/file/2`, `/file/3`...

**Script gộp:** `generate_raw_dataset_v1.py` chạy tất cả 4 script trên cùng lúc và xuất ra:
- `data/raw/request_logs_raw.csv` — toàn bộ log
- `data/raw/ground_truth.csv` — nhãn từng dòng log (normal/anomaly + scenario)

---

### 3.4. Feature Engineering — Biến log thành số để ML hiểu

**Vấn đề:** ML không hiểu được "download_file lúc 14:22". ML chỉ hiểu số.

**Giải pháp:** Chia log thành các **cửa sổ thời gian 5 phút** theo từng user/session, rồi tính các con số thống kê mô tả hành vi trong cửa sổ đó.

**File:** `ml/build_features.py`

**Ví dụ cụ thể:**

```
User A, Session X, từ 14:00 đến 14:05:
  - 3 request download → export_count = 3, export_ratio = 0.6
  - 0 lỗi 403 → forbidden_count = 0
  - 5 request tổng → request_count = 5
  → Cửa sổ này được đặc trưng bởi vector 24 số
```

**24 feature được tạo ra:**

| Nhóm | Feature | Phát hiện gì |
|---|---|---|
| **Tốc độ** | `request_count`, `burst_rate`, `avg_inter_request_sec` | Automation/bot |
| **Đa dạng** | `unique_endpoint_count`, `unique_resource_id_count` | Scan bừa |
| **Export** | `export_count`, `export_ratio` | Export Abuse |
| **Delete** | `delete_count`, `delete_ratio`, `unique_deleted_resource_count` | Delete Abuse |
| **Lỗi** | `forbidden_count`, `forbidden_rate`, `not_found_count`, `unique_failed_resource_id_count` | BOLA Scan |
| **Nhạy cảm** | `sensitive_request_count`, `sensitive_ratio`, `max_sensitive_streak` | Mọi loại |
| **Thời gian** | `session_duration_sec`, `avg_response_time_ms`, `error_rate` | Tổng quát |

---

### 3.5. Isolation Forest — Mô hình ML phát hiện bất thường

**Tại sao chọn Isolation Forest?** Vì không có nhiều mẫu bất thường để train supervised. Isolation Forest train bằng dữ liệu **bình thường** là chủ yếu, sau đó tự nhận ra cái gì "khác với bình thường".

**Nguyên lý đơn giản:**
> Cây ngẫu nhiên cắt không gian dữ liệu. Điểm bất thường bị cô lập (isolated) nhanh hơn → cần ít bước cắt hơn → anomaly score cao hơn.

**Quy trình train:**

```
1. Load data từ data/processed/features_v1/train_features.csv (chỉ normal windows)
2. IsolationForest(n_estimators=100, contamination=0.05).fit(X_train)
3. Tính ngưỡng threshold = percentile 95 của anomaly score trên train set
4. Lưu model vào artifacts/models/iforest_v1.joblib
```

**Quy trình detect:**

```
1. Lấy log từ DB trong khoảng thời gian cần kiểm tra
2. Tính feature 24 chiều cho từng cửa sổ 5 phút
3. model.score_samples(X) → anomaly score
4. Nếu score > threshold → BẤT THƯỜNG → lưu Alert vào DB
```

**File:** `ml/train.py`, `ml/evaluate.py`, `ml/detect.py`

---

### 3.6. Alert Dashboard — Nơi Admin xem kết quả

**File:** `app/blueprints/alerts/routes.py`, `app/templates/alerts/`

Khi model phát hiện bất thường, nó tạo một bản ghi `Alert` trong DB với:
- User bị nghi ngờ
- Cửa sổ thời gian (window_start → window_end)
- Điểm bất thường (anomaly_score)
- Kịch bản gợi ý (export_abuse / delete_abuse / bola_scan)
- Các feature nổi bật (dưới dạng JSON)

Admin vào `/alerts/` để xem danh sách, click vào từng alert để xem chi tiết.

---

## 4. Database gồm những bảng nào?

| Bảng | Lưu gì |
|---|---|
| `users` | Tài khoản user/admin |
| `folders` | Thư mục của user |
| `stored_files` | Metadata file (không lưu nội dung file trong DB) |
| `file_shares` | Ai chia sẻ file cho ai, quyền gì |
| `export_jobs` | Lịch sử export CSV |
| `request_logs` | **Mọi request HTTP** — nguồn dữ liệu ML |
| `alerts` | **Cảnh báo từ ML** — kết quả phát hiện |

---

## 5. Các câu hỏi giáo viên hay hỏi + câu trả lời gợi ý

**Q: Tại sao dùng Isolation Forest mà không dùng mô hình khác?**
> "Isolation Forest phù hợp với bài toán anomaly detection không cần nhãn nhiều. Hệ thống chỉ cần nhiều dữ liệu bình thường để train, còn dữ liệu bất thường chỉ dùng để đánh giá sau. Ngoài ra IF nhẹ, nhanh và giải thích được qua feature importance."

**Q: Làm sao biết một request là bất thường?**
> "Không phân tích từng request riêng lẻ. Hệ thống chia log theo cửa sổ 5 phút của từng user/session, tính 24 feature thống kê, rồi Isolation Forest cho điểm cửa sổ đó. Nếu vượt ngưỡng thì tạo alert."

**Q: BOLA là gì? Phát hiện thế nào?**
> "BOLA (Broken Object Level Authorization) là kiểu tấn công đoán ID để truy cập tài nguyên người khác, ví dụ thử /file/1, /file/2, /file/3... Hệ thống phát hiện qua các feature: `forbidden_count` cao, `not_found_count` cao, `unique_failed_resource_id_count` lớn và `resource_id_change_rate` cao trong một cửa sổ thời gian ngắn."

**Q: Dữ liệu train lấy từ đâu?**
> "Dữ liệu được sinh bằng 4 script mô phỏng chạy trên chính web thật (không giả lập HTTP, mà gọi trực tiếp Flask test client). Tổng tối thiểu 5.000 request log, có nhãn ground_truth. Train set chỉ dùng cửa sổ normal, validation/test có cả normal và anomaly."

**Q: Làm sao tránh data leakage?**
> "Tách dữ liệu theo session/run, không theo random shuffle. Nghĩa là toàn bộ session của một kịch bản anomaly luôn nằm trong test, không bao giờ lẫn vào train."

**Q: False positive rate của mô hình là bao nhiêu?**
> "Theo đánh giá trên test set, FPR khoảng X%. Mô hình không tuyên bố dùng được cho thực tế; kết luận chỉ trong phạm vi StudyDrive local và dữ liệu mô phỏng." *(thay X% sau khi chạy evaluate)*

---

## 6. Sơ đồ file code quan trọng nhất

```
run.py                          ← Khởi động web (python run.py)
app/__init__.py                 ← Tạo Flask app, kết nối tất cả lại
app/config.py                   ← Cấu hình DB, secret key, upload folder
app/extensions.py               ← SQLAlchemy (db), CSRF protection

app/middleware/request_logging.py   ← Hook ghi log sau mỗi request
app/services/log_service.py         ← Logic phân tích và lưu log vào DB
app/services/document_service.py    ← Logic upload/share/delete file
app/services/detection_service.py   ← Gọi ML pipeline và lưu Alert

app/models/request_log.py       ← Cấu trúc bảng request_logs
app/models/alert.py             ← Cấu trúc bảng alerts
app/models/stored_file.py       ← Cấu trúc bảng stored_files

ml/build_features.py            ← Tạo 24 feature từ log CSV
ml/train.py                     ← Train Isolation Forest → lưu .joblib
ml/evaluate.py                  ← Tính Precision/Recall/F1/FPR
ml/detect.py                    ← Load model, predict cửa sổ mới

scripts/simulate_normal.py      ← Tạo hành vi bình thường
scripts/simulate_export_abuse.py    ← Tạo hành vi export lạm dụng
scripts/simulate_delete_abuse.py    ← Tạo hành vi xóa lạm dụng
scripts/simulate_bola_scan.py       ← Tạo hành vi IDOR/BOLA scan
scripts/generate_raw_dataset_v1.py  ← Chạy tất cả 4 script + xuất CSV
scripts/run_detection.py            ← Chạy detection service thủ công
scripts/seed.py                     ← Tạo dữ liệu mẫu ban đầu
scripts/reset_demo.py               ← Reset DB về trạng thái demo
```

---

## 7. Các lệnh cần nhớ để chạy demo

```powershell
# 1. Bật môi trường ảo
.\.venv\Scripts\Activate.ps1

# 2. Reset DB về trạng thái sạch
python -m scripts.reset_demo

# 3. Khởi động web
python run.py
# → Mở http://127.0.0.1:5000

# 4. Tạo dữ liệu log (chạy terminal khác)
python -m scripts.generate_raw_dataset_v1 --fast --normal-requests 5000

# 5. Tạo feature
python -m ml.build_features --logs data/raw/request_logs_raw.csv --ground-truth data/raw/ground_truth.csv --output-dir data/processed/features_v1

# 6. Train model
python -m ml.train --features-dir data/processed/features_v1

# 7. Đánh giá
python -m ml.evaluate --features-dir data/processed/features_v1

# 8. Chạy detection (lưu alert vào DB)
python -m scripts.run_detection
```

---

## 8. Tài khoản demo (sau khi seed)

| Username | Password | Vai trò |
|---|---|---|
| `admin` | `Admin@123` | ADMIN |
| `user1` | `User@123` | USER |
| `user2` | `User@123` | USER |

*(Kiểm tra lại trong `scripts/seed.py` để chắc chắn)*
