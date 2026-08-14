# Cẩm Nang Hiểu Hệ Thống Web Anomaly Detection
## Đề tài: Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning

> **Dành cho chuẩn bị bảo vệ đồ án:** Trình bày ngắn gọn, trực quan, bám sát 100% mã nguồn thực tế của dự án StudyDrive.

---

## 1. Hệ thống này làm gì? (Tóm tắt 1 câu)

Hệ thống xây dựng một ứng dụng web lưu trữ và chia sẻ tệp tin (**StudyDrive**), tích hợp cơ chế ghi nhật ký truy cập có cấu trúc (**Structured Request Logging**) và mô hình học máy không giám sát (**Isolation Forest**) để tự động phát hiện, cảnh báo và phản ứng kịp thời trước các hành vi tấn công lạm dụng logic nghiệp vụ (**Business Logic Abuse**) và dò quét kiểm soát truy cập đối tượng (**BOLA/IDOR**).

---

## 2. Luồng hoạt động tổng thể của hệ thống

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│ [1] NGƯỜI DÙNG TƯƠNG TÁC WEB (StudyDrive)                                         │
│     - Đăng ký, đăng nhập, tải tệp, tạo thư mục, chia sẻ, xóa, xuất ZIP/CSV        │
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │ HTTP Request
                                         ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ [2] TẦNG FLASK MIDDLEWARE & APPLICATION                                           │
│     - ActiveDefense Middleware: Kiểm tra tài khoản có bị khóa tạm thời không     │
│     - Route Handler & RBAC: Xử lý nghiệp vụ, kiểm tra quyền OWNER / VIEWER        │
│     - RequestLogging Middleware: Tự động trích xuất metadata và đo response time  │
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │ Ghi log tự động
                                         ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ [3] CƠ SỞ DỮ LIỆU CÓ CẤU TRÚC (MySQL / SQLAlchemy)                               │
│     - Bảng `request_logs`: 21 trường dữ liệu có cấu trúc (băm SHA-256 session)    │
│     - Bảng `users`, `folders`, `stored_files`, `file_shares`, `export_jobs`       │
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │ Quét dữ liệu định kỳ (Batch Detection)
                                         ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ [4] PIPELINE MACHINE LEARNING (ml/build_features.py & ml/detect.py)               │
│     - Gom nhóm theo cửa sổ trượt 5 phút (theo từng user và phiên làm việc)        │
│     - Trích xuất Vector 25 đặc trưng số (Feature Extraction)                      │
│     - Chuẩn hóa và đưa qua mô hình Isolation Forest (đã train Normal-only)        │
│     - So sánh Anomaly Score với ngưỡng Percentile 95%                             │
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │ Nếu Anomaly Score >= Threshold
                                         ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ [5] CẢNH BÁO & PHÒNG THỦ CHỦ ĐỘNG (Alerts & Active Defense)                       │
│     - Lưu bản ghi vào bảng `alerts` (kèm Top Features và Scenario Hint)           │
│     - Kích hoạt Active Defense: Khóa tạm thời tài khoản nghi vấn (60 phút)        │
│     - Quản trị viên theo dõi Dashboard trực quan, xem biểu đồ và truy ngược log   │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Các thành phần chính của hệ thống

### 3.1. Ứng dụng Web StudyDrive (`app/`)
Website quản lý tài liệu xây dựng bằng **Flask + Jinja2 + Bootstrap 5 + SQLAlchemy**.

| Blueprint | Route chính | Vai trò truy cập | Chức năng nghiệp vụ |
|---|---|---|---|
| `auth` | `/auth/register` | Khách (Anonymous) | Đăng ký tài khoản người dùng mới |
| `auth` | `/auth/login`, `/auth/logout` | Tất cả | Xác thực tài khoản, khởi tạo session an toàn |
| `main` | `/` | User / Admin | Trang chủ bảng điều khiển hoạt động |
| `documents` | `/documents/` | User / Admin | Duyệt cây thư mục và danh sách tệp tin |
| `documents` | `/documents/folder/create` | User | Tạo thư mục mới theo cấp cha - con |
| `documents` | `/documents/upload` | User | Tải lên tệp tin vật lý (lưu tại `instance/uploads/`) |
| `documents` | `/documents/file/<id>` | OWNER / VIEWER | Xem chi tiết thông tin tệp tin |
| `documents` | `/documents/file/<id>/download` | OWNER / VIEWER | Tải xuống tệp tin đính kèm |
| `documents` | `/documents/file/<id>/share` | OWNER | Chia sẻ quyền truy cập `VIEWER` cho người khác |
| `documents` | `/documents/file/<id>/delete` | OWNER | Xóa mềm tệp tin (chuyển vào Thùng rác) |
| `documents` | `/documents/trash` | User | Xem và khôi phục tệp tin đã xóa mềm |
| `documents` | `/documents/export` | User | Khởi tạo job xuất danh sách tệp tin dạng CSV |
| `admin` | `/admin/`, `/admin/users` | ADMIN | Quản trị tài khoản người dùng, khóa/mở khóa |
| `admin` | `/admin/logs`, `/admin/logs/<id>` | ADMIN | Tra cứu, lọc nhật ký request log chi tiết |
| `alerts` | `/alerts/`, `/alerts/<id>` | ADMIN | Theo dõi danh sách cảnh báo ML, xem chi tiết |
| `alerts` | `/alerts/trigger-detection` | ADMIN | Kích hoạt quét phát hiện bất thường thủ công |

---

### 3.2. Hệ thống Ghi nhật ký có cấu trúc (Structured Request Logging)
Mỗi khi Flask xử lý xong một HTTP Request, middleware `app/middleware/request_logging.py` cùng service `app/services/log_service.py` tự động thu thập và lưu vào bảng `request_logs`.

**21 trường dữ liệu có cấu trúc trong bảng `request_logs`:**
1. `id`: Khóa chính tự tăng.
2. `request_id`: Mã UUID định danh duy nhất cho từng request.
3. `timestamp`: Thời điểm request được thực thi (chuẩn UTC).
4. `user_id`: ID người dùng thực hiện (hoặc `NULL`/`-1` nếu chưa đăng nhập).
5. `is_authenticated`: Cờ Boolean xác nhận trạng thái đăng nhập.
6. `role`: Vai trò (`ANONYMOUS`, `USER`, `ADMIN`).
7. `session_id_hash`: Mã băm SHA-256 của Flask Session ID (chống rò rỉ phiên).
8. `http_method`: Phương thức HTTP (`GET`, `POST`, `PUT`, `DELETE`).
9. `endpoint`: Tên route nội bộ của Flask (`documents.download_file`,...).
10. `path`: Đường dẫn URI thực tế (`/documents/file/42/download`).
11. `action`: Hành động cụ thể (`download_file`, `delete_file`, `view_detail`,...).
12. `action_type`: Nhóm hành vi (`export`, `delete`, `browse`, `admin`,...).
13. `is_sensitive`: Cờ đánh dấu thao tác nhạy cảm (tải nhiều, xóa, đổi quyền).
14. `resource_type`: Loại tài nguyên tác động (`file`, `folder`, `user`, `system`).
15. `resource_id`: ID của tài nguyên bị tác động.
16. `ownership_result`: Kết quả sở hữu (`OWNER`, `VIEWER`, `NONE`).
17. `authorization_result`: Kết quả phân quyền (`allowed`, `denied`).
18. `status_code`: Mã phản hồi HTTP (`200`, `302`, `403`, `404`, `500`).
19. `response_time_ms`: Thời gian xử lý request (tính bằng mili-giây).
20. `ip_address`: Địa chỉ IP của máy khách.
21. `user_agent`: Chuỗi định danh trình duyệt / client.

---

### 3.3. Bốn kịch bản mô phỏng hành vi (Simulators)

Để huấn luyện và kiểm thử mô hình mà không ảnh hưởng tới dữ liệu thật, hệ thống phát triển bộ script mô phỏng tương tác:

| Script giả lập | Hành vi mô phỏng | Đặc trưng nhận diện bất thường |
|---|---|---|
| `scripts/simulate_normal.py` | Người dùng hợp lệ: Đăng nhập, duyệt cây thư mục, xem chi tiết, tải xuống vài tệp, đăng xuất. | Tần suất đều đặn, tỷ lệ lỗi 0%, phân tán đều, không có đột biến xóa hay xuất dữ liệu. |
| `scripts/simulate_export_abuse.py` | Lạm dụng tính năng xuất dữ liệu: Gửi liên tiếp 30–50 yêu cầu export/tải tệp trong 5 phút. | `export_count` tăng cao, `export_ratio` > 0.6, `burst_rate` cao, nguy cơ thất thoát dữ liệu. |
| `scripts/simulate_delete_abuse.py` | Phá hoại dữ liệu: Xóa mềm dồn dập 20–40 tệp tin khác nhau trong thời gian rất ngắn. | `delete_count` lớn, `delete_ratio` cao, `unique_deleted_resource_count` tăng vọt. |
| `scripts/simulate_bola_scan.py` | Rà quét IDOR/BOLA: Thử truy cập tuần tự hàng trăm `file_id` không thuộc quyền sở hữu (`/documents/file/101`,...). | `forbidden_count` (lỗi 403) và `not_found_count` (lỗi 404) tăng vọt, `resource_id_change_rate` cao. |

---

### 3.4. Không gian 25 đặc trưng số (Feature Engineering)
Dữ liệu log thô được chia thành các **cửa sổ trượt 5 phút (5-minute sliding windows)** theo từng `user_id` và `session_id_hash`. Từ mỗi cửa sổ, module `ml/build_features.py` tính toán vector 25 đặc trưng số:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   DANH MỤC 25 ĐẶC TRƯNG HÀNH VI (ml/build_features.py)           │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. Nhóm Lưu lượng & Tần suất (Traffic & Velocity):                               │
│    [1] request_count: Tổng số request trong cửa sổ 5 phút.                       │
│    [2] unique_endpoint_count: Số lượng endpoint duy nhất được gọi.               │
│    [3] unique_method_count: Số lượng HTTP method khác nhau sử dụng.              │
│    [4] session_duration_sec: Khoảng thời gian từ request đầu đến request cuối.   │
│    [5] avg_inter_request_sec: Thời gian trung bình giữa 2 request liên tiếp.     │
│    [6] min_inter_request_sec: Khoảng cách ngắn nhất giữa 2 request (phát hiện bot)│
│    [7] burst_rate: Tỷ lệ bùng nổ (số request chia cho thời lượng phiên).         │
│                                                                                  │
│ 2. Nhóm Lỗi & Bất thường Phân quyền (Errors & Authorization):                    │
│    [8] error_rate: Tỷ lệ request trả về mã lỗi HTTP >= 400.                      │
│    [9] forbidden_count: Số lần gặp lỗi 403 Forbidden (truy cập trái phép).       │
│    [10] forbidden_rate: Tỷ lệ lỗi 403 trên tổng số request.                      │
│    [11] not_found_count: Số lần gặp lỗi 404 Not Found (đoán sai ID).             │
│    [12] not_found_rate: Tỷ lệ lỗi 404 trên tổng số request.                      │
│    [13] unique_failed_resource_id_count: Số lượng ID tài nguyên bị lỗi phân quyền.│
│                                                                                  │
│ 3. Nhóm Lạm dụng Nghiệp vụ Xuất & Xóa (Business Logic Abuse):                    │
│    [14] export_count: Số lần thực hiện hành động xuất/tải dữ liệu.               │
│    [15] export_ratio: Tỷ lệ hành động xuất dữ liệu trên tổng request.            │
│    [16] delete_count: Số lần thực hiện hành động xóa tài nguyên.                 │
│    [17] delete_ratio: Tỷ lệ hành động xóa tài nguyên trên tổng request.          │
│    [18] unique_deleted_resource_count: Số lượng tài nguyên khác nhau bị xóa.     │
│                                                                                  │
│ 4. Nhóm Hành vi Dò quét Tài nguyên (Resource Exploration):                       │
│    [19] unique_resource_id_count: Số lượng ID tài nguyên khác nhau được truy cập.│
│    [20] resource_id_request_ratio: Tỷ lệ request có tương tác với resource_id.   │
│    [21] resource_id_change_rate: Tần suất chuyển đổi giữa các resource_id.      │
│                                                                                  │
│ 5. Nhóm Thao tác Nhạy cảm & Độ trễ (Sensitivity & Latency):                      │
│    [22] sensitive_request_count: Số lượng request thuộc nhóm nhạy cảm.           │
│    [23] sensitive_ratio: Tỷ lệ request nhạy cảm trên tổng request.               │
│    [24] max_sensitive_streak: Chuỗi dài nhất các request nhạy cảm liên tiếp.     │
│    [25] avg_response_time_ms: Thời gian phản hồi trung bình của máy chủ.         │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.5. Thuật toán Isolation Forest & Phát hiện Bất thường
- **Chiến lược huấn luyện:** **Normal-only Training** — Mô hình chỉ được huấn luyện trên các cửa sổ hành vi bình thường (`label = 0`) để học phân bố chuẩn của hệ thống mà không cần nhãn tấn công.
- **Nguyên lý cô lập:** Các điểm bất thường (tấn công) nằm ở vùng mật độ thưa, dễ bị cô lập qua ít lần phân chia nhị phân ngẫu nhiên (độ sâu đường đi $h(x)$ ngắn), dẫn đến Anomaly Score cao.
- **Xác định ngưỡng:** Ngưỡng cảnh báo $\tau$ được tính bằng phân vị thứ 95 (**Percentile 95.0%**) trên tập huấn luyện, giúp kiểm soát chặt chẽ tỷ lệ báo động giả (False Positive Rate).
- **Phòng chống rò rỉ dữ liệu (Group-aware Split):** Phân chia tập Train / Validation / Test theo nhóm `user_id|session_id_hash` và `run_id`, đảm bảo toàn bộ hành vi của một phiên làm việc không bị phân tán giữa các tập.

---

### 3.6. Cơ chế Phòng thủ Chủ động (Active Defense)
Khi tiến trình `detection_service.py` phát hiện một cửa sổ có Anomaly Score vượt ngưỡng:
1. Tạo một bản ghi cảnh báo trong bảng `alerts` kèm theo điểm bất thường, gợi ý kịch bản (`export_abuse`, `delete_abuse`, `bola_scan`) và Top 3 đặc trưng nổi bật nhất.
2. Tự động kích hoạt cơ chế khóa tạm thời: Thiết lập `user.is_locked = True` và `user.locked_until = datetime.utcnow() + timedelta(minutes=60)`.
3. Middleware `app/middleware/active_defense.py` sẽ chặn ngay lập tức mọi request tiếp theo từ người dùng này, vô hiệu hóa phiên làm việc và hiển thị thông báo yêu cầu liên hệ quản trị viên.

---

## 4. Cấu trúc Cơ sở Dữ liệu

| Bảng CSDL | Mục đích lưu trữ | Các trường dữ liệu cốt lõi |
|---|---|---|
| `users` | Tài khoản và trạng thái bảo mật | `id`, `username`, `email`, `password_hash`, `role`, `is_active`, `is_locked`, `locked_until` |
| `folders` | Cấu trúc thư mục của người dùng | `id`, `name`, `user_id`, `parent_id`, `is_deleted`, `created_at` |
| `stored_files` | Metadata của tệp tin tải lên | `id`, `original_filename`, `stored_filename`, `file_size`, `mime_type`, `user_id`, `folder_id`, `is_deleted` |
| `file_shares` | Phân quyền chia sẻ tài nguyên | `id`, `file_id`, `shared_with_user_id`, `permission` (`VIEWER`), `created_at` |
| `export_jobs` | Lịch sử tác vụ xuất dữ liệu | `id`, `user_id`, `status`, `file_path`, `item_count`, `total_size`, `created_at` |
| `request_logs` | Toàn bộ lịch sử HTTP Request | `id`, `request_id`, `timestamp`, `user_id`, `session_id_hash`, `endpoint`, `action`, `status_code`,... (21 trường) |
| `alerts` | Cảnh báo bất thường từ mô hình ML | `id`, `user_id`, `window_id`, `anomaly_score`, `threshold`, `scenario_hint`, `top_features`, `is_reviewed` |

---

## 5. Các câu hỏi bảo vệ đồ án hay gặp & Câu trả lời chuẩn

### Q1: Tại sao đề tài chọn Isolation Forest mà không dùng các thuật toán học có giám sát như Random Forest hay SVM?
> **Trả lời:** Trong thực tế an toàn thông tin, các cuộc tấn công lạm dụng nghiệp vụ (như BOLA hay Export Abuse) diễn ra rất đa dạng và dữ liệu tấn công có nhãn luôn khan hiếm hoặc không đầy đủ. Nếu dùng học có giám sát (Supervised Learning), mô hình sẽ bị thiên lệch (overfitting) và không thể phát hiện những kiểu tấn công mới (Zero-day). Isolation Forest là thuật toán học không giám sát (Unsupervised), chỉ cần học phân bố hành vi bình thường để phát hiện các điểm dị biệt (outliers). Hơn nữa, iForest có độ phức tạp tính toán tuyến tính $O(n \cdot t)$, chạy rất nhẹ và cho tốc độ suy luận nhanh phù hợp với ứng dụng web.

### Q2: Hệ thống ghi nhận request log ở tầng nào? Có làm giảm tốc độ của ứng dụng web không?
> **Trả lời:** Hệ thống ghi log tại tầng **Middleware của Flask** thông qua hook `@app.after_request`. Việc này đảm bảo logic ứng dụng được xử lý xong trước khi ghi log. Thời gian thực thi việc trích xuất metadata và ghi vào MySQL chỉ mất trung bình dưới 2ms mỗi request. Ngoài ra, mật khẩu và Session ID đều được loại bỏ hoặc băm SHA-256 trước khi lưu để đảm bảo tuyệt đối tính riêng tư và an toàn thông tin.

### Q3: BOLA / IDOR là gì? Làm thế nào hệ thống phát hiện được hành vi này qua 25 đặc trưng?
> **Trả lời:** BOLA (Broken Object Level Authorization) hay IDOR là lỗ hổng kiểm soát truy cập ở cấp đối tượng, khi kẻ tấn công thay đổi tham số ID trên URL (ví dụ `/documents/file/1`, `/documents/file/2`) để truy cập tệp tin của người khác. Hệ thống phát hiện BOLA thông qua các đặc trưng: `forbidden_count` (lỗi 403 tăng vọt), `not_found_count` (lỗi 404 do đoán sai ID), `unique_failed_resource_id_count` cao và `resource_id_change_rate` lớn trong cùng một cửa sổ 5 phút.

### Q4: Hiện tượng rò rỉ dữ liệu (Data Leakage) được xử lý như thế nào khi chia tập Train / Val / Test?
> **Trả lời:** Do dữ liệu log được thu thập theo từng phiên làm việc của người dùng, nếu chia ngẫu nhiên (Random Split) theo dòng, các cửa sổ thời gian của cùng một người dùng/phiên tấn công sẽ bị phân tán vào cả tập Train và Test, dẫn đến kết quả đánh giá bị lạc quan ảo. Đề tài áp dụng kỹ thuật **Group-aware Split**: gom nhóm toàn bộ các cửa sổ theo `user_id|session_id_hash` và `run_id`, tập Train chỉ chứa 100% các phiên bình thường, còn tập Test chứa các phiên hoàn toàn độc lập.

### Q5: Dự án đã được kiểm thử như thế nào?
> **Trả lời:** Dự án đã được xây dựng bộ kiểm thử tự động toàn diện bằng `pytest` với **44 bài test tự động** bao gồm kiểm thử xác thực, đăng ký người dùng, kiểm soát phân quyền tài nguyên, bảo mật chống xóa tệp người khác, cơ chế ghi log tầng middleware và kiểm thử luồng phát hiện bất thường. Toàn bộ 44/44 test cases đều vượt qua (100% PASSED).
