# ✅ BẢNG CHECKLIST ÔN THI 9 GIỜ — BẢO VỆ ĐỒ ÁN

> **Mục tiêu:** Hiểu toàn hệ thống + tự tin phản biện hội đồng
> **Cách dùng:** Tick `[x]` khi đã thuộc, có thể nói miệng KHÔNG CẦN nhìn tài liệu

---

## 🕐 GIỜ 1–2 | BỨC TRANH TỔNG THỂ & VẤN ĐỀ CỐT LÕI
*Mục tiêu: Kể được "câu chuyện 60 giây" + giải thích tại sao đề tài tồn tại*

| # | Nội dung cần thuộc | Mức độ | Check |
|---|---|---|---|
| 1.1 | **Câu chuyện 60 giây**: Middleware → Window 5 phút → 25 feature → IForest → Threshold 95% → Alert → Active Defense | ⭐⭐⭐ CỐT LÕI | `[ ]` |
| 1.2 | WAF thất bại vì sao? — Phân tích từng request riêng lẻ, không thấy **chuỗi hành vi** | ⭐⭐⭐ | `[ ]` |
| 1.3 | StudyDrive là gì? Ai dùng? Chức năng gì? (upload/download/share/export/delete/admin) | ⭐⭐ | `[ ]` |
| 1.4 | **3 kịch bản tấn công**: Export Abuse / Delete Abuse / BOLA Scan — bản chất, hậu quả | ⭐⭐⭐ | `[ ]` |
| 1.5 | BOLA/IDOR là gì? — Kẻ tấn công đổi `file_id` trên URL để truy cập file người khác | ⭐⭐⭐ | `[ ]` |
| 1.6 | Business Logic Abuse là gì? — Request hợp lệ về cú pháp nhưng chuỗi hành vi phá hoại | ⭐⭐⭐ | `[ ]` |
| 1.7 | Authentication vs Authorization — *"Bạn là ai?"* vs *"Bạn được làm gì?"* | ⭐⭐⭐ | `[ ]` |
| 1.8 | HTTP 200 / 403 / 404 / 500 — ý nghĩa và vai trò trong phát hiện anomaly | ⭐⭐ | `[ ]` |

**Tự kiểm tra miệng:** Giải thích toàn bộ mục 1 trong 3 phút không nhìn tài liệu ✊

---

## 🕑 GIỜ 2–3 | THU THẬP LOG — MIDDLEWARE & STRUCTURED LOGGING
*Mục tiêu: Giải thích được cơ chế ghi log hoạt động như thế nào từ đầu đến cuối*

| # | Nội dung cần thuộc | Mức độ | Check |
|---|---|---|---|
| 2.1 | Luồng `before_request` → Business Logic → `after_request` — vai trò từng hook | ⭐⭐⭐ | `[ ]` |
| 2.2 | `before_request` làm gì? — Sinh UUID `request_id`, bấm giờ `perf_counter()` | ⭐⭐ | `[ ]` |
| 2.3 | `after_request` làm gì? — Tính `response_time_ms`, gọi `save_request_log()` | ⭐⭐⭐ | `[ ]` |
| 2.4 | **Isolated SQLAlchemy session** — Tại sao không dùng chung session nghiệp vụ? | ⭐⭐⭐ | `[ ]` |
| 2.5 | Logging **KHÔNG** lưu gì? — Password, CSRF token, cookie, body request, nội dung file | ⭐⭐⭐ | `[ ]` |
| 2.6 | `session_id_hash` — Tại sao băm SHA-256 thay vì lưu session gốc? (chống session hijacking) | ⭐⭐⭐ | `[ ]` |
| 2.7 | `action_type` — 10 bucket: login/list/create/view_detail/edit/export/delete/restore/admin/other | ⭐⭐⭐ | `[ ]` |
| 2.8 | `is_sensitive = True` khi nào? — export/delete/admin + view_detail bị từ chối (IDOR hint) | ⭐⭐⭐ | `[ ]` |
| 2.9 | `ownership_result` — OWNER/VIEWER/NONE/NOT_FOUND/ADMIN/ANONYMOUS/UNKNOWN | ⭐⭐ | `[ ]` |
| 2.10 | `authorization_result` — allowed/denied/error (dựa vào status code) | ⭐⭐ | `[ ]` |
| 2.11 | Tại sao lưu vào **DB** chứ không ghi file .log? — Truy vấn linh hoạt, index, forensics | ⭐⭐ | `[ ]` |

**Tự kiểm tra:** Vẽ lại luồng middleware bằng tay, giải thích isolated session ✊

---

## 🕒 GIỜ 3–4 | WINDOW 5 PHÚT & FEATURE ENGINEERING
*Mục tiêu: Giải thích vì sao cần window + thuộc 25 feature theo 4 nhóm*

| # | Nội dung cần thuộc | Mức độ | Check |
|---|---|---|---|
| 3.1 | **Tại sao cần window?** — 1 request đơn lẻ vô nghĩa, cần xem chuỗi hành vi | ⭐⭐⭐ | `[ ]` |
| 3.2 | **Tumbling Window** (không chồng lấp) — `floor('5min')`, mỗi request thuộc đúng 1 window | ⭐⭐⭐ | `[ ]` |
| 3.3 | **Khóa gom nhóm kép**: `user_id + session_id_hash + mốc 5 phút` | ⭐⭐⭐ | `[ ]` |
| 3.4 | `window_id` = SHA1(user_id \| session_hash \| window_start)[:16] | ⭐⭐ | `[ ]` |
| 3.5 | **NHÓM 1 — Traffic & Timing** (6 feature): `request_count`, `session_duration_sec`, `avg_inter_request_sec`, `min_inter_request_sec`, `burst_rate`, `avg_response_time_ms` | ⭐⭐⭐ | `[ ]` |
| 3.6 | **NHÓM 2 — Sensitive & Abuse** (8 feature): `sensitive_request_count`, `sensitive_ratio`, `export_count`, `export_ratio`, `delete_count`, `delete_ratio`, `unique_deleted_resource_count`, `max_sensitive_streak` | ⭐⭐⭐ | `[ ]` |
| 3.7 | **NHÓM 3 — Diversity & Interaction** (5 feature): `unique_endpoint_count`, `unique_method_count`, `unique_resource_id_count`, `resource_id_request_ratio`, `resource_id_change_rate` | ⭐⭐⭐ | `[ ]` |
| 3.8 | **NHÓM 4 — Error & Access Control** (6 feature): `error_rate`, `forbidden_count`, `forbidden_rate`, `not_found_count`, `not_found_rate`, `unique_failed_resource_id_count` | ⭐⭐⭐ | `[ ]` |
| 3.9 | `burst_rate` — tỷ lệ khoảng cách request ≤ 1 giây → nhận diện **tool tự động** | ⭐⭐ | `[ ]` |
| 3.10 | `resource_id_change_rate` — 100% với BOLA (mỗi request là 1 ID mới) | ⭐⭐⭐ | `[ ]` |
| 3.11 | `max_sensitive_streak` — chuỗi is_sensitive=True liên tiếp dài nhất (không bị ngắt) | ⭐⭐ | `[ ]` |
| 3.12 | Feature nào quan trọng nhất cho từng kịch bản: Export/Delete/BOLA? | ⭐⭐⭐ | `[ ]` |

**Bảng ghi nhớ nhanh:**

```
Kịch bản      Feature nổi bật
Export Abuse  export_count↑, export_ratio↑, sensitive_ratio↑, avg_response_time_ms↑
Delete Abuse  delete_count↑, delete_ratio↑, unique_deleted_resource_count↑, max_sensitive_streak↑
BOLA Scan     unique_failed_resource_id_count↑, forbidden_rate↑, not_found_rate↑, resource_id_change_rate→100%
Normal        Tất cả thấp, burst_rate thấp, error_rate thấp
```

**Tự kiểm tra:** Kể tên 25 feature theo nhóm mà KHÔNG nhìn tài liệu ✊

---

## 🕓 GIỜ 4–5 | ISOLATION FOREST — THUẬT TOÁN & CÔNG THỨC
*Mục tiêu: Giải thích nguyên lý + công thức anomaly score + cách chọn ngưỡng*

| # | Nội dung cần thuộc | Mức độ | Check |
|---|---|---|---|
| 4.1 | **Isolation Forest là gì?** — Học không giám sát, cô lập điểm dị thường bằng random split | ⭐⭐⭐ | `[ ]` |
| 4.2 | **Trực giác hình học**: Anomaly ở thưa → ít bước cắt → path ngắn → score cao | ⭐⭐⭐ | `[ ]` |
| 4.3 | **iTree**: Chọn ngẫu nhiên 1 feature → chọn ngẫu nhiên 1 split point trong [min, max] | ⭐⭐⭐ | `[ ]` |
| 4.4 | **Path Length h(x)**: Số bước từ gốc đến khi mẫu x bị cô lập thành lá | ⭐⭐⭐ | `[ ]` |
| 4.5 | **Công thức c(n)**: `c(n) = 2*(ln(n-1) + 0.5772156649) - 2*(n-1)/n` | ⭐⭐⭐ | `[ ]` |
| 4.6 | **Công thức Anomaly Score**: `s(x,n) = 2^(- E[h(x)] / c(n))` | ⭐⭐⭐ | `[ ]` |
| 4.7 | Điểm score → 1.0 khi nào? → 0.5? → 0.0? | ⭐⭐⭐ | `[ ]` |
| 4.8 | Tại sao dùng `-model.score_samples(x)` trong code? (scikit-learn trả âm, đảo dấu) | ⭐⭐ | `[ ]` |
| 4.9 | **Normal-only Training** — Tại sao chỉ train trên data bình thường? | ⭐⭐⭐ | `[ ]` |
| 4.10 | Zero-day attack — Tại sao Supervised (Random Forest) thua? IF thắng? | ⭐⭐⭐ | `[ ]` |
| 4.11 | Tham số: `n_estimators=200`, `max_samples="auto"`, `contamination="auto"`, `n_jobs=-1` | ⭐⭐ | `[ ]` |
| 4.12 | **Percentile Thresholding 95%**: Tính từ train_scores, chấp nhận 5% dung sai FPR | ⭐⭐⭐ | `[ ]` |
| 4.13 | Threshold thực nghiệm: **0.4866** (trên tập kiểm thử) | ⭐⭐⭐ | `[ ]` |

**Tự kiểm tra:** Giải thích được tại sao "path ngắn → score cao → anomaly" bằng lời của mình ✊

---

## 🕔 GIỜ 5–6 | DATA SPLIT CHỐNG RÒ RỈ & KẾT QUẢ THỰC NGHIỆM
*Mục tiêu: Giải thích data leakage + nêu được con số kết quả chính xác*

| # | Nội dung cần thuộc | Mức độ | Check |
|---|---|---|---|
| 5.1 | **Data Leakage là gì?** — Thông tin Test lộ vào Train → kết quả đẹp giả | ⭐⭐⭐ | `[ ]` |
| 5.2 | Random Split nguy hiểm thế nào? — Window cùng session bị xáo vào cả Train + Test | ⭐⭐⭐ | `[ ]` |
| 5.3 | **Group-aware Split**: Đơn vị chia = cả nhóm session, không phải từng dòng | ⭐⭐⭐ | `[ ]` |
| 5.4 | Split group = `run_id` (nếu ≥3 run) hoặc `user_id\|session_id_hash` (fallback) | ⭐⭐ | `[ ]` |
| 5.5 | Phân bổ: Normal → Train 60% / Val 20% / Test 20%; Anomaly → Val 50% / Test 50% | ⭐⭐⭐ | `[ ]` |
| 5.6 | Train set: **8 cửa sổ (100% Normal)** — không có anomaly nào | ⭐⭐⭐ | `[ ]` |
| 5.7 | Val set: **6 cửa sổ** (3 Normal + 1 Export + 1 Delete + 1 BOLA) | ⭐⭐⭐ | `[ ]` |
| 5.8 | Test set: **6 cửa sổ** (3 Normal + 2 Export + 1 BOLA) — holdout độc lập | ⭐⭐⭐ | `[ ]` |
| 5.9 | **Grid Search**: 24 tổ hợp (n_estimators×max_samples×percentile) | ⭐⭐ | `[ ]` |
| 5.10 | Kết quả tối ưu trên **Validation**: n=200, percentile=95% → **F1=80%, Accuracy=83.33%** | ⭐⭐⭐ | `[ ]` |
| 5.11 | Kết quả trên **Test Set**: TN=2, FP=1, FN=1, TP=2 → **Accuracy=66.67%, F1=66.67%** | ⭐⭐⭐ | `[ ]` |
| 5.12 | **Tại sao 66.67% chứ không phải 100%?** — 2 nguyên nhân khoa học (xem mục 6.3) | ⭐⭐⭐ | `[ ]` |
| 5.13 | Export Abuse bị phát hiện **100%** — Anomaly Score trung bình **0.501** > threshold | ⭐⭐⭐ | `[ ]` |
| 5.14 | BOLA Scan bị bỏ sót (FN) — Score **0.4765** < threshold **0.4866** (Low-and-Slow 23 req) | ⭐⭐⭐ | `[ ]` |
| 5.15 | FP là ai? — user6 có lưu lượng đột biến **1.087 req / 5 phút** (người dùng bình thường) | ⭐⭐⭐ | `[ ]` |

**Bảng số cần nhớ:**

```
Metric          Val (tune)    Test (final)
Accuracy        83.33%        66.67%
Precision       100%          66.67%
Recall          66.67%        66.67%
F1-Score        80.00%        66.67%
FPR             0%            33.33%
Threshold               0.4866
```

**Tự kiểm tra:** Nêu số liệu chính xác và giải thích nguồn gốc FN + FP ✊

---

## 🕕 GIỜ 6–7 | DETECTION SERVICE, ALERT & ACTIVE DEFENSE
*Mục tiêu: Mô tả luồng inference online + cơ chế khóa tài khoản*

| # | Nội dung cần thuộc | Mức độ | Check |
|---|---|---|---|
| 6.1 | Detection chạy **on-demand** (admin bấm nút), không real-time — lý do hợp lý | ⭐⭐⭐ | `[ ]` |
| 6.2 | `run_detection()` làm gì? — DB → DataFrame → clean → window → feature → predict → Alert | ⭐⭐⭐ | `[ ]` |
| 6.3 | Offline vs Online: Feature engineering **giống nhau hoàn toàn** (cùng gọi `aggregate_features()`) | ⭐⭐⭐ | `[ ]` |
| 6.4 | **Dedup Alert**: `UNIQUE(window_id, model_version)` — không tạo trùng cảnh báo | ⭐⭐ | `[ ]` |
| 6.5 | **Scenario Hint** — Rule-based heuristic, KHÔNG phải ML, giải thích "vì sao bị flag" | ⭐⭐⭐ | `[ ]` |
| 6.6 | 4 scenario hint: `export_abuse` / `delete_abuse` / `bola_scan` / `resource_probe` / `general_anomaly` | ⭐⭐ | `[ ]` |
| 6.7 | **Top feature deltas** — Top 5 feature value lớn nhất để admin hiểu, KHÔNG phải SHAP | ⭐⭐ | `[ ]` |
| 6.8 | **Active Defense kích hoạt khi**: score > 0.70 **HOẶC** scenario ∈ {bola_scan, export_abuse, delete_abuse} | ⭐⭐⭐ | `[ ]` |
| 6.9 | **Hành động**: `user.locked_until = now() + 60 phút` trong DB | ⭐⭐⭐ | `[ ]` |
| 6.10 | **Tại sao khóa user, không chặn IP?** — NAT/Proxy: nhiều người dùng chung 1 IP | ⭐⭐⭐ | `[ ]` |
| 6.11 | `check_active_defense()` chạy **trước mọi request** — trả 403 nếu `is_locked=True` | ⭐⭐⭐ | `[ ]` |
| 6.12 | Logout **luôn được phép** dù bị khóa — `if endpoint == 'auth.logout': return` | ⭐⭐ | `[ ]` |
| 6.13 | **Digital Forensics**: Từ Alert → click → xem request log gốc trong 5 phút đó | ⭐⭐⭐ | `[ ]` |
| 6.14 | Bảng `alerts`: window_id, anomaly_score, scenario_hint, features_json, status (NEW/REVIEWING/RESOLVED) | ⭐⭐ | `[ ]` |

**Tự kiểm tra:** Vẽ luồng từ "Admin click Chạy Detection" đến "user bị khóa 60 phút" ✊

---

## 🕖 GIỜ 7–8 | KIẾN TRÚC TỔNG THỂ & DATABASE
*Mục tiêu: Mô tả được hệ thống 2 tầng + 8 bảng DB*

| # | Nội dung cần thuộc | Mức độ | Check |
|---|---|---|---|
| 7.1 | **2 tầng hệ thống**: Web Layer (Flask) + ML Layer (offline) + Detection Service (bridge) | ⭐⭐⭐ | `[ ]` |
| 7.2 | **5 Blueprint**: auth / documents / admin / alerts / main — route chính mỗi cái | ⭐⭐ | `[ ]` |
| 7.3 | **8 bảng DB**: users, folders, stored_files, file_shares, export_jobs, export_job_items, request_logs, alerts | ⭐⭐⭐ | `[ ]` |
| 7.4 | `users` — role (USER/ADMIN), is_active, locked_until | ⭐⭐ | `[ ]` |
| 7.5 | `stored_files` — lưu metadata, file vật lý lưu bằng UUID trên disk, hỗ trợ soft delete | ⭐⭐ | `[ ]` |
| 7.6 | `file_shares` — OWNER chia sẻ quyền VIEWER cho user khác | ⭐⭐ | `[ ]` |
| 7.7 | ML Pipeline commands: `build_features` → `train --tune` → `evaluate` → `detect` | ⭐⭐⭐ | `[ ]` |
| 7.8 | **Artifact model**: `model.joblib` chứa `{model, feature_list, threshold, metadata}` | ⭐⭐ | `[ ]` |
| 7.9 | **44/44 test cases Passed** — Pytest, 7 module test, chạy < 15 giây | ⭐⭐⭐ | `[ ]` |
| 7.10 | test_web_freeze.py — Test khóa tài khoản, chặn HTTP 403, tự mở khóa sau 60 phút | ⭐⭐ | `[ ]` |

**Tự kiểm tra:** Giải thích luồng từ "user gửi request" đến "admin xem alert" theo sơ đồ ✊

---

## 🕗 GIỜ 8–9 | LUYỆN PHẢN BIỆN — 15 CÂU HỎI TRỌNG TÂM
*Mục tiêu: Trả lời tự tin, đúng trọng tâm, không bị bối rối*

| # | Câu hỏi hội đồng | Từ khóa đáp án | Check |
|---|---|---|---|
| Q1 | Tại sao chọn Isolation Forest thay vì Random Forest / SVM? | Unsupervised, không cần nhãn, Zero-day, Normal-only | `[ ]` |
| Q2 | Tại sao gom nhóm theo window 5 phút chứ không đưa từng request vào ML? | Chuỗi hành vi, tần suất, 1 request vô nghĩa | `[ ]` |
| Q3 | Data Leakage là gì? Group-aware Split giải quyết thế nào? | Cùng session vào Train+Test, chia theo group | `[ ]` |
| Q4 | Phân biệt Precision và Recall trong ngữ cảnh security? | Precision = ít báo nhầm, Recall = không bỏ sót tấn công | `[ ]` |
| Q5 | Anomaly Score được tính thế nào? Ngưỡng 95% có nghĩa gì? | s(x,n) = 2^(-E[h(x)]/c(n)), 5% dung sai FPR | `[ ]` |
| Q6 | BOLA/IDOR là gì? Feature nào phát hiện? | Đổi resource_id, not_found_rate, forbidden_rate, unique_failed | `[ ]` |
| Q7 | Active Defense — tại sao khóa user không chặn IP? | NAT/Proxy, nhiều user chung 1 IP | `[ ]` |
| Q8 | Tại sao logging dùng Isolated DB session? | Tránh log bị rollback cùng nghiệp vụ, safe failure | `[ ]` |
| Q9 | Kết quả 66.67% trên Test — nguyên nhân khoa học? | 1) Tập nhỏ 6 cửa sổ, 2) BOLA Low-and-Slow (0.4765 < 0.4866) | `[ ]` |
| Q10 | Scenario Hint có phải output của ML không? | KHÔNG — rule-based heuristic giải thích sau khi ML phát hiện | `[ ]` |
| Q11 | `is_sensitive` được gán như thế nào? | export/delete/admin luôn True; view_detail bị từ chối → IDOR | `[ ]` |
| Q12 | Tại sao Train set không được có anomaly? | IF học "normal trông như thế nào", anomaly trong train → sai baseline | `[ ]` |
| Q13 | Attacker dùng nhiều account thì hệ thống có phát hiện không? (Distributed attack) | Điểm yếu — mỗi account score thấp, đây là limitation | `[ ]` |
| Q14 | Slow attack (1 req/3 giây) có bị phát hiện không? | Khó — ít request trong 5 phút, score thấp. Limitation của window 5 phút | `[ ]` |
| Q15 | Nếu có thêm thời gian, cải tiến gì trước? | Real-time streaming (Kafka), cross-session anomaly, LSTM | `[ ]` |

---

## 📊 BẢNG SỐ LIỆU CẦN NHỚ CHÍNH XÁC

| Chỉ số | Giá trị |
|--------|---------|
| Tổng request logs | **10.875 bản ghi** |
| Số feature | **25 feature** (4 nhóm) |
| Window size | **5 phút** (Tumbling) |
| n_estimators | **200** |
| Threshold (percentile) | **95.0%** |
| Threshold (giá trị thực) | **0.4866** |
| Train set | **8 cửa sổ** (100% Normal) |
| Val set | **6 cửa sổ** (3N + 3A) |
| Test set | **6 cửa sổ** (3N + 3A) |
| Val Accuracy | **83.33%** / F1 = **80%** |
| Test Accuracy | **66.67%** / F1 = **66.67%** |
| Export Abuse detection | **100%** (Anomaly Score ≈ 0.501) |
| BOLA Scan (FN) | Score **0.4765** < threshold **0.4866** |
| FP case | user6, **1.087 req/5 phút** |
| Active Defense lock | **60 phút** |
| Test cases | **44/44 Passed** |
| Grid Search combos | **24 tổ hợp** |

---

## ⚡ CHECKLIST CUỐI — 15 PHÚT TRƯỚC KHI VÀO PHÒNG

```
[ ] Tôi kể được câu chuyện 60 giây KHÔNG nhìn tài liệu
[ ] Tôi vẽ được sơ đồ luồng từ request → alert → lock
[ ] Tôi nhớ số liệu: 10.875 log, 25 feature, 5 phút, 200 cây, threshold=0.4866
[ ] Tôi giải thích được tại sao kết quả Test 66.67% (KHÔNG xin lỗi, giải thích khoa học)
[ ] Tôi phân biệt được Precision vs Recall theo ngữ cảnh security
[ ] Tôi biết Scenario Hint KHÔNG phải ML output
[ ] Tôi biết tại sao khóa user chứ không chặn IP
[ ] Tôi biết BOLA Scan bị bỏ sót vì lý do gì (Low-and-Slow, 23 req, score 0.4765)
[ ] Tôi tự tin nêu 2 limitation chính: slow attack, distributed attack
[ ] Tôi sẵn sàng nêu hướng phát triển: Kafka streaming, LSTM
```

---

*Phương châm: Hội đồng không cần kết quả 100%, họ cần thấy bạn HIỂU tại sao kết quả là như vậy.*
