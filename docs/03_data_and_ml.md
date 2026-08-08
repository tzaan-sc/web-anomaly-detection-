# 03. DỮ LIỆU & HỌC MÁY (DATA & MACHINE LEARNING)

## 1. Structured Log Schema (`request_logs`)
Hệ thống lưu lại các metadata cần thiết của mọi request để phục vụ quá trình ML.
Tuyệt đối KHÔNG LƯU: mật khẩu, cookie, session/csrf token thô, nội dung tệp.

Các trường quan trọng:
- `request_id`: UUID duy nhất cho mỗi request.
- `timestamp`: Thời gian UTC.
- `user_id`, `session_id_hash`: Định danh người dùng và phiên.
- `action`: Hành động nghiệp vụ (VD: `DOWNLOAD_FILE`, `SHARE_FILE`).
- `action_type`: Phân loại nhóm hành động cho ML (`login`, `list`, `create`, `view_detail`, `edit`, `export`, `delete`, `restore`, `admin`, `other`).
- `is_sensitive`: Flag boolean nếu request là thao tác nhạy cảm (Xóa, Export, Đổi quyền).
- `resource_type`, `resource_id`: Loại và ID của tài nguyên bị thao tác.
- `permission`, `authorization_result`: Quyền hiện tại và kết quả phê duyệt (`ALLOWED`, `DENIED`).
- `status_code`: Mã lỗi HTTP.

## 2. Các kịch bản bất thường (Anomalies)
Hệ thống giả lập và phát hiện 3 scenario chính:
1. **Export Abuse:** Gửi nhiều request tạo export metadata/file trong thời gian ngắn, số lượng file lớn hoặc không thuộc quyền.
2. **Delete Abuse:** Thực hiện soft-delete liên tục nhiều file thuộc nhiều thư mục trong một window.
3. **IDOR / BOLA Scan:** Liên tục thay đổi `resource_id` để thăm dò, nhận về nhiều lỗi 403 (Forbidden) hoặc 404 (Not Found), tỷ lệ `permission_none_rate` cao.

## 3. Data Generation & Feature Engineering
- **Window size:** Logs được nhóm theo user + session trong từng khoảng thời gian (cửa sổ - window) là **5 phút**.
- **Features (Đặc trưng):** 
  - Hoạt động chung: `request_count`, `unique_endpoint_count`, `avg_inter_request_sec`, `error_rate`.
  - Phục vụ Export/Delete: `export_count`, `delete_count`, `unique_deleted_resource_count`.
  - Phục vụ BOLA: `unique_resource_id_count`, `forbidden_rate`, `not_found_rate`, `unique_failed_resource_id_count`.
- **Ground Truth (`ground_truth.csv`):** Chứa các nhãn (0: normal, 1: anomaly) và kịch bản để huấn luyện và đánh giá.

## 4. Mô hình Học máy (Isolation Forest)
Hệ thống sử dụng thuật toán **Isolation Forest** để phát hiện sự bất thường.
- Huấn luyện chủ yếu trên dữ liệu normal.
- Trả về `anomaly_score` và `scenario_hint` (gợi ý nguyên nhân).
- Kết quả được ghi nhận vào bảng `alerts` để Admin review.
