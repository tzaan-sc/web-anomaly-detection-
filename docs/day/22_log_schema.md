# LOG SCHEMA — STRUCTURED REQUEST LOGGING

## 1. Mục đích

Tài liệu này quy định cấu trúc log chuẩn cho StudyDrive nhằm:

- Theo dõi request theo người dùng, session và tài nguyên.
- Điều tra các request bị từ chối bởi authorization.
- Hỗ trợ trang Admin Logs.
- Xuất dữ liệu cho feature engineering và Isolation Forest.
- Phát hiện ba scenario: Export Abuse, Delete Abuse và IDOR/BOLA Scan.

Log chỉ ghi metadata cần thiết. Không ghi password, cookie nguyên bản, CSRF token, session token nguyên bản hoặc nội dung tệp.

---

## 2. Luồng ghi log chuẩn

```text
before_request
→ tạo request_id
→ lưu start_time
→ xác định user/session/client cơ bản

route / authorization / service
→ bổ sung action
→ resource_type, resource_id
→ owner_id, permission, authorization_result
→ thông tin file/export nếu có

after_request
→ lấy status_code
→ tính response_time_ms
→ lưu một RequestLog
```

Yêu cầu:

1. Mỗi HTTP request chỉ tạo tối đa một bản ghi `request_logs`.
2. Request thất bại với `401`, `403`, `404`, `413` hoặc `500` vẫn phải được ghi nếu ứng dụng đã nhận request.
3. Lỗi ghi log không được làm request nghiệp vụ chính bị crash.
4. Tất cả timestamp được tạo theo UTC.
5. Middleware không được đọc hoặc ghi toàn bộ request body của form đăng nhập và upload.

---

## 3. Bảng `request_logs`

### 3.1. Schema chuẩn

| Trường | Kiểu SQLAlchemy / MySQL dự kiến | Null | Nguồn dữ liệu | Ý nghĩa |
|---|---|---:|---|---|
| `id` | `Integer` / `INT` | Không | Database | Khóa chính nội bộ |
| `request_id` | `String(64)` / `VARCHAR(64)` | Không | Middleware | UUID hoặc mã duy nhất của request |
| `timestamp` | `DateTime(timezone=True)` / `DATETIME` | Không | Middleware | Thời điểm nhận request theo UTC |
| `user_id` | `Integer` / `INT` | Có | Session/current user | User gửi request; null nếu chưa đăng nhập hoặc login thất bại |
| `role` | `String(20)` / `VARCHAR(20)` | Có | User/session | `USER`, `ADMIN`; null nếu public |
| `session_id_hash` | `String(128)` / `VARCHAR(128)` | Có | Session helper | Hash dùng liên kết các request trong cùng phiên; không lưu token thật |
| `ip_address` | `String(45)` / `VARCHAR(45)` | Có | Request | IPv4 hoặc IPv6 |
| `user_agent` | `String(512)` / `VARCHAR(512)` | Có | Request header | Trình duyệt, Postman hoặc simulator |
| `http_method` | `String(10)` / `VARCHAR(10)` | Không | Request | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| `endpoint` | `String(255)` / `VARCHAR(255)` | Có | Flask request | Tên endpoint Flask, ưu tiên `blueprint.function` |
| `path` | `String(1024)` / `VARCHAR(1024)` | Có | Flask request | URL path không gồm query string; không lưu body/cookie/token |
| `action` | `String(80)` / `VARCHAR(80)` | Có | Route/service | Hành động nghiệp vụ chuẩn |
| `resource_type` | `String(50)` / `VARCHAR(50)` | Có | Route/authorization | Loại tài nguyên bị truy cập |
| `resource_id` | `String(100)` / `VARCHAR(100)` | Có | `view_args`/service | ID tài nguyên; dùng String để hỗ trợ nhiều loại ID |
| `owner_id` | `Integer` / `INT` | Có | Authorization/service | Chủ sở hữu tài nguyên nếu xác định được |
| `permission` | `String(20)` / `VARCHAR(20)` | Có | Authorization | `OWNER`, `VIEWER`, `NONE`; null nếu không áp dụng |
| `authorization_result` | `String(20)` / `VARCHAR(20)` | Có | Authorization | `ALLOWED`, `DENIED`; null nếu không áp dụng |
| `status_code` | `Integer` / `INT` | Không | Response | HTTP status trả về |
| `response_time_ms` | `Float` / `FLOAT` | Không | Middleware | Thời gian xử lý request theo mili giây |
| `file_size` | `BigInteger` / `BIGINT` | Có | File service | Kích thước file liên quan nếu có |
| `export_item_count` | `Integer` / `INT` | Có | Export service | Số tệp trong export |
| `export_total_size` | `BigInteger` / `BIGINT` | Có | Export service | Tổng dung lượng export |

### 3.2. Quy tắc timestamp với MySQL

MySQL `DATETIME` không tự lưu múi giờ. Ứng dụng phải:

- Tạo thời gian bằng UTC.
- Lưu nhất quán dưới dạng UTC.
- Khi export CSV hoặc JSON, biểu diễn theo ISO 8601, ví dụ `2026-06-13T13:20:05Z`.
- Không trộn thời gian local và UTC trong cùng bảng.

---

## 4. Giá trị chuẩn

### 4.1. `role`

```text
USER
ADMIN
```

Public request hoặc login thất bại trước khi xác định user có thể để null.

### 4.2. `permission`

```text
OWNER
VIEWER
NONE
```

- `OWNER`: user sở hữu tài nguyên.
- `VIEWER`: user được chia sẻ quyền xem/tải.
- `NONE`: không có quyền trên tài nguyên.
- Null: endpoint không thao tác tài nguyên cần object authorization.

### 4.3. `authorization_result`

```text
ALLOWED
DENIED
```

- `ALLOWED`: request vượt qua kiểm tra quyền.
- `DENIED`: request bị từ chối.
- Null: endpoint public hoặc không có object authorization.

### 4.4. `resource_type`

```text
USER
FOLDER
FILE
FILE_SHARE
EXPORT_JOB
REQUEST_LOG
ALERT
NONE
```

Trong database có thể dùng null thay cho `NONE`, nhưng toàn hệ thống phải chọn một quy ước và dùng nhất quán. Khuyến nghị dùng null khi không có tài nguyên.

### 4.5. `status_code`

Các mã cần theo dõi:

| Code | Ý nghĩa |
|---:|---|
| `200` | Đọc/cập nhật thành công |
| `201` | Tạo tài nguyên thành công |
| `204` | Xóa/hủy thành công, không có body |
| `302` | Redirect sau form |
| `400` | Input không hợp lệ |
| `401` | Chưa đăng nhập |
| `403` | Đã đăng nhập nhưng không có quyền |
| `404` | Không tồn tại hoặc cố tình ẩn sự tồn tại |
| `409` | Xung đột trạng thái hoặc dữ liệu trùng |
| `413` | File vượt giới hạn |
| `500` | Lỗi ngoài dự kiến |

---

## 5. Danh mục `action`

Tên action dùng chữ hoa và `UPPER_SNAKE_CASE`.

### 5.1. Authentication và profile

```text
VIEW_LOGIN
LOGIN_SUCCESS
LOGIN_FAILED
LOGOUT
VIEW_CURRENT_USER
VIEW_PROFILE
UPDATE_PROFILE
CHANGE_PASSWORD
```

### 5.2. Dashboard

```text
VIEW_DASHBOARD
ADMIN_VIEW_DASHBOARD
```

### 5.3. Folder

```text
VIEW_FOLDER
CREATE_FOLDER
UPDATE_FOLDER
DELETE_FOLDER
```

### 5.4. File

```text
LIST_FILES
VIEW_FILE
UPLOAD_FILE
UPLOAD_REJECTED
DOWNLOAD_FILE
RENAME_FILE
MOVE_FILE
DELETE_FILE
RESTORE_FILE
PERMANENT_DELETE_FILE
```

### 5.5. Sharing

```text
VIEW_SHARED_FILES
VIEW_FILE_SHARES
SHARE_FILE
REVOKE_SHARE
```

### 5.6. Export

```text
VIEW_EXPORT_HISTORY
CREATE_EXPORT_JOB
VIEW_EXPORT_JOB
DOWNLOAD_EXPORT
```

### 5.7. Admin

```text
ADMIN_VIEW_USERS
ADMIN_VIEW_USER
ADMIN_LOCK_USER
ADMIN_UNLOCK_USER
ADMIN_VIEW_FILE_METADATA
ADMIN_VIEW_LOGS
ADMIN_VIEW_LOG_DETAIL
ADMIN_EXPORT_LOGS
RUN_DETECTION
ADMIN_VIEW_ALERTS
ADMIN_VIEW_ALERT_DETAIL
UPDATE_ALERT
```

### 5.8. Security/error context

```text
PERMISSION_DENIED
NOT_FOUND
VALIDATION_FAILED
INTERNAL_ERROR
```

Không nên thay action nghiệp vụ bằng action lỗi trong mọi trường hợp. Ví dụ request xóa trái quyền có thể giữ:

```text
action = DELETE_FILE
authorization_result = DENIED
status_code = 403
```

Cách này giúp feature Delete Abuse và BOLA cùng sử dụng được bản ghi.

---

## 6. Mapping endpoint → action và resource

| Endpoint mẫu | Action | Resource type | Resource ID |
|---|---|---|---|
| `POST /login` thành công | `LOGIN_SUCCESS` | null | null |
| `POST /login` thất bại | `LOGIN_FAILED` | null | null |
| `GET /dashboard` | `VIEW_DASHBOARD` | `USER` | current user ID |
| `POST /api/folders` | `CREATE_FOLDER` | `FOLDER` | folder ID sau khi tạo |
| `GET /folders/{folder_id}` | `VIEW_FOLDER` | `FOLDER` | `folder_id` |
| `GET /files` | `LIST_FILES` | null | null |
| `POST /files/upload` | `UPLOAD_FILE` | `FILE` | file ID sau khi tạo |
| `GET /files/{file_id}` | `VIEW_FILE` | `FILE` | `file_id` |
| `GET /files/{file_id}/download` | `DOWNLOAD_FILE` | `FILE` | `file_id` |
| `PUT /api/files/{file_id}` đổi tên | `RENAME_FILE` | `FILE` | `file_id` |
| `PUT /api/files/{file_id}` di chuyển | `MOVE_FILE` | `FILE` | `file_id` |
| `DELETE /api/files/{file_id}` | `DELETE_FILE` | `FILE` | `file_id` |
| `POST /api/files/{file_id}/restore` | `RESTORE_FILE` | `FILE` | `file_id` |
| `POST /api/files/{file_id}/shares` | `SHARE_FILE` | `FILE` | `file_id` |
| `DELETE /api/files/{file_id}/shares/{user_id}` | `REVOKE_SHARE` | `FILE` | `file_id` |
| `POST /api/exports` | `CREATE_EXPORT_JOB` | `EXPORT_JOB` | job ID sau khi tạo |
| `GET /api/exports/{export_job_id}` | `VIEW_EXPORT_JOB` | `EXPORT_JOB` | `export_job_id` |
| `GET /admin/logs` | `ADMIN_VIEW_LOGS` | `REQUEST_LOG` | null |
| `GET /admin/logs/{log_id}` | `ADMIN_VIEW_LOG_DETAIL` | `REQUEST_LOG` | `log_id` |
| `POST /admin/detection/run` | `RUN_DETECTION` | null | null |
| `GET /admin/alerts/{alert_id}` | `ADMIN_VIEW_ALERT_DETAIL` | `ALERT` | `alert_id` |

---

## 7. Hợp đồng bổ sung context từ route/service

Middleware chỉ tự xác định được thông tin HTTP cơ bản. Route, authorization và service phải bổ sung thông tin nghiệp vụ.

Khuyến nghị tạo helper:

```python
def set_log_context(
    *,
    action=None,
    resource_type=None,
    resource_id=None,
    owner_id=None,
    permission=None,
    authorization_result=None,
    file_size=None,
    export_item_count=None,
    export_total_size=None,
):
    ...
```

Context có thể được lưu tạm trong `flask.g`.

Ví dụ:

```python
set_log_context(
    action="VIEW_FILE",
    resource_type="FILE",
    resource_id=file.id,
    owner_id=file.owner_id,
    permission=permission,
    authorization_result="ALLOWED",
    file_size=file.file_size,
)
```

Request trái quyền:

```python
set_log_context(
    action="VIEW_FILE",
    resource_type="FILE",
    resource_id=requested_file_id,
    owner_id=file.owner_id if file else None,
    permission="NONE",
    authorization_result="DENIED",
)
```

Không ghi metadata bí mật của tài nguyên khi user không có quyền.

---

## 8. Quy tắc lấy `session_id_hash`

Không lưu cookie hoặc session token thô.

Có thể tạo hash bằng HMAC:

```text
HMAC-SHA256(SECRET_KEY, session_identifier)
```

Yêu cầu:

- Cùng một session tạo cùng `session_id_hash`.
- Session mới tạo hash khác.
- Không thể dùng hash để khôi phục session token.
- Không log toàn bộ cookie header.
- Nếu chưa có session, để null.

---

## 9. IP address và proxy

Môi trường local:

```text
request.remote_addr
```

Chỉ sử dụng `X-Forwarded-For` khi ứng dụng được cấu hình proxy tin cậy. Không mặc định tin mọi header do client gửi.

---

## 10. Dữ liệu tuyệt đối không được ghi

Không ghi các dữ liệu sau vào `request_logs`, CSV hoặc console:

```text
password
password_hash
old_password
new_password
cookie nguyên bản
session token nguyên bản
CSRF token
Authorization header nguyên bản
nội dung tệp
request body upload
secret key
DATABASE_URL có mật khẩu
```

Đối với login:

- Được ghi username/email đã chuẩn hóa nếu thật sự cần điều tra, nhưng phạm vi hiện tại không bắt buộc.
- Không ghi password hoặc toàn bộ form body.
- Thông báo lỗi login nên chung chung.

---

## 11. Index

Model hiện tại cần các index:

```text
request_id
timestamp
user_id
session_id_hash
http_method
endpoint
action
resource_type
resource_id
owner_id
permission
authorization_result
status_code
```

Composite index quan trọng:

```text
(user_id, timestamp)
(session_id_hash, timestamp)
(action, timestamp)
(status_code, timestamp)
(resource_type, resource_id)
(authorization_result, timestamp)
```

Mục đích:

- Tìm chuỗi hành vi theo user/session.
- Lọc log Admin theo thời gian và action.
- Truy ngược request trên một tài nguyên.
- Tính tỷ lệ denied, 403 và 404.
- Gom cửa sổ phục vụ feature engineering.

---

## 12. Liên hệ với ba scenario ML

### 12.1. Export Abuse

Trường sử dụng:

```text
timestamp
user_id
session_id_hash
action = CREATE_EXPORT_JOB
resource_type = EXPORT_JOB
resource_id
authorization_result
status_code
export_item_count
export_total_size
```

Feature dự kiến:

```text
export_count
export_ratio
unique_export_job_count
export_item_count_sum
export_total_size_sum
time_to_first_export_sec
export_denied_rate
```

### 12.2. Delete Abuse

Trường sử dụng:

```text
timestamp
user_id
session_id_hash
action = DELETE_FILE hoặc PERMANENT_DELETE_FILE
resource_type = FILE
resource_id
owner_id
permission
authorization_result
status_code
```

Feature dự kiến:

```text
delete_count
delete_ratio
unique_deleted_file_count
avg_inter_delete_sec
time_to_first_delete_sec
delete_permission_mismatch_rate
```

### 12.3. IDOR/BOLA Scan

Trường sử dụng:

```text
timestamp
user_id
session_id_hash
endpoint
action
resource_type
resource_id
owner_id
permission
authorization_result
status_code
```

Feature dự kiến:

```text
unique_resource_id_count
unique_failed_resource_id_count
resource_id_change_rate
permission_none_rate
authorization_denied_rate
forbidden_count
forbidden_rate
not_found_count
not_found_rate
```

---

## 13. Ví dụ bản ghi

```json
{
  "request_id": "6dcaa836-4f0f-4f13-9dc4-fdf48e2f0240",
  "timestamp": "2026-06-13T13:20:05Z",
  "user_id": 3,
  "role": "USER",
  "session_id_hash": "3fe8f4b7...",
  "ip_address": "127.0.0.1",
  "user_agent": "python-requests/2.x",
  "http_method": "GET",
  "endpoint": "documents.file_detail",
  "action": "VIEW_FILE",
  "resource_type": "FILE",
  "resource_id": "42",
  "owner_id": 5,
  "permission": "NONE",
  "authorization_result": "DENIED",
  "status_code": 403,
  "response_time_ms": 18.42,
  "file_size": null,
  "export_item_count": null,
  "export_total_size": null
}
```

---

## 14. Alert schema liên quan

Bảng `alerts` lưu kết quả theo cửa sổ hành vi:

| Trường | Ý nghĩa |
|---|---|
| `user_id` | User liên quan |
| `window_id` | Mã cửa sổ hành vi |
| `window_start`, `window_end` | Khoảng thời gian |
| `model_version` | Phiên bản model |
| `anomaly_score` | Điểm bất thường |
| `scenario_hint` | Gợi ý Export Abuse, Delete Abuse hoặc IDOR/BOLA |
| `features_json` | Feature nổi bật |
| `status` | `NEW`, `REVIEWING`, `RESOLVED` |

Unique constraint:

```text
window_id + model_version
```

giúp chạy detection nhiều lần mà không tạo alert trùng.

---

## 15. Kiểm thử bắt buộc

### 15.1. Middleware

- [ ] Một request tạo đúng một `RequestLog`.
- [ ] `request_id` không trùng.
- [ ] `response_time_ms` là số không âm.
- [ ] Request `403`, `404`, `413`, `500` vẫn được ghi.
- [ ] Lỗi ghi log không làm request chính lỗi theo.
- [ ] Login thất bại không ghi password.

### 15.2. Authorization context

- [ ] OWNER tạo log `permission=OWNER`, `authorization_result=ALLOWED`.
- [ ] VIEWER tải file tạo log `permission=VIEWER`, `authorization_result=ALLOWED`.
- [ ] User không có quyền tạo log `permission=NONE`, `authorization_result=DENIED`.
- [ ] `resource_id` vẫn được ghi cho request bị từ chối, nhưng không lộ metadata khác.

### 15.3. MySQL và index

- [ ] Bảng `request_logs` được tạo trong MySQL.
- [ ] Các index composite tồn tại.
- [ ] Lọc theo user/session/action/status hoạt động.
- [ ] Pandas đọc CSV export không lỗi.

### 15.4. An toàn dữ liệu

- [ ] Không có password.
- [ ] Không có cookie nguyên bản.
- [ ] Không có CSRF/session token nguyên bản.
- [ ] Không có nội dung tệp.
- [ ] Không có secret hoặc database password.

---

## 16. Tiêu chí hoàn thành tài liệu và triển khai

Thiết kế log schema được xem là hoàn thành khi:

- Tất cả trường có kiểu, nguồn, nullability và ý nghĩa rõ ràng.
- Endpoint chính ánh xạ được sang action và resource.
- Các trường đủ phục vụ ba scenario.
- Có quy tắc dữ liệu nhạy cảm không được ghi.
- Index hỗ trợ truy vấn và feature engineering.

Phần triển khai logging chỉ được xem là hoàn thành khi:

- `app/middleware/request_logging.py` không còn placeholder.
- `app/services/log_service.py` không còn placeholder.
- Middleware được đăng ký trong app factory.
- Request thật tạo dữ liệu trong bảng `request_logs`.
- Có test xác nhận một request tạo đúng một log.
