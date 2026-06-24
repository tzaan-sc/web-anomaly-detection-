# LOG SCHEMA — STRUCTURED + SEMANTIC REQUEST LOGGING

## 1. Mục đích

Tài liệu này quy định cấu trúc log chuẩn cho StudyDrive để phục vụ:

- Theo dõi request theo user, session, endpoint và tài nguyên.
- Điều tra các request bị từ chối bởi authorization.
- Sinh feature cho Machine Learning, đặc biệt là Export Abuse, Delete Abuse và IDOR/BOLA Scan.
- Làm nền cho trang Admin Logs và export dataset.

Nguyên tắc an toàn: log chỉ lưu metadata. Không ghi password, cookie nguyên bản, CSRF token, session token nguyên bản, request body, query string nhạy cảm, nội dung tệp hoặc đường dẫn vật lý `storage_path`.

---

## 2. Luồng ghi log

```text
before_request
→ tạo request_id UUID
→ lưu request_start_time

after_request
→ tính response_time_ms
→ đọc metadata an toàn: user/session/method/path/endpoint/status/IP/user_agent
→ lấy resource_id từ request.view_args
→ map endpoint thành action và action_type
→ suy ra security context: is_authenticated, ownership_result, authorization_result, is_sensitive
→ ghi một dòng RequestLog
```

Yêu cầu:

1. Mỗi HTTP request tạo tối đa một dòng `request_logs`.
2. Request trả `401`, `403`, `404`, `413`, `500` vẫn phải được ghi nếu app đã xử lý request.
3. Lỗi ghi log không được làm request nghiệp vụ chính crash.
4. Middleware không được đọc `request.form`, `request.data`, `request.get_json()`, file upload stream, cookie thô hoặc token.
5. URL được ghi bằng `request.path`, không gồm query string.

---

## 3. Bảng `request_logs`

| Trường | Kiểu dự kiến | Null | Nguồn | Ý nghĩa |
|---|---|---:|---|---|
| `id` | `INT` | Không | DB | Khóa chính nội bộ |
| `request_id` | `VARCHAR(64)` | Không | Middleware | UUID duy nhất cho từng request |
| `timestamp` | `DATETIME` | Không | Model default UTC | Thời điểm ghi log |
| `user_id` | `INT` | Có | `g.current_user`/session | User gửi request; null nếu chưa đăng nhập |
| `is_authenticated` | `BOOLEAN` | Không | Session/current user | Request có user đăng nhập hay không |
| `role` | `VARCHAR(20)` | Có | User/session | `USER`, `ADMIN`, hoặc null |
| `session_id_hash` | `VARCHAR(128)` | Có | Session | Hash phiên làm việc; không phải token thô |
| `ip_address` | `VARCHAR(45)` | Có | Request | IPv4/IPv6 hoặc local IP |
| `user_agent` | `VARCHAR(512)` | Có | Header | Browser/Postman/simulator |
| `http_method` | `VARCHAR(10)` | Không | Request | `GET`, `POST`, ... |
| `endpoint` | `VARCHAR(255)` | Có | Flask | Tên endpoint dạng `blueprint.function` |
| `path` | `VARCHAR(1024)` | Có | Request | URL path không gồm query string |
| `action` | `VARCHAR(80)` | Có | Mapping endpoint | Hành động chi tiết, ví dụ `rename_file`, `download_file` |
| `action_type` | `VARCHAR(80)` | Có | Mapping endpoint | Nhóm hành vi cho ML: `login`, `list`, `create`, `view_detail`, `edit`, `export`, `delete`, `restore`, `admin`, `other` |
| `is_sensitive` | `BOOLEAN` | Không | Log service | Request nhạy cảm: export/delete/restore/admin hoặc detail trái quyền |
| `resource_type` | `VARCHAR(50)` | Có | `request.view_args` | `file`, `folder`, `user`, `share`, hoặc null |
| `resource_id` | `VARCHAR(100)` | Có | `request.view_args` | ID tài nguyên từ route, không lấy bằng regex URL |
| `owner_id` | `INT` | Có | Context lookup | Chủ sở hữu tài nguyên nếu xác định được |
| `permission` | `VARCHAR(20)` | Có | Context lookup | Quyền tại thời điểm request: `OWNER`, `VIEWER`, `NONE`, `ADMIN`, ... |
| `ownership_result` | `VARCHAR(20)` | Có | Context lookup | Kết quả ownership: `OWNER`, `VIEWER`, `NONE`, `NOT_FOUND`, `ADMIN`, `ANONYMOUS`, `UNKNOWN` |
| `authorization_result` | `VARCHAR(20)` | Có | Response status | `allowed`, `denied`, hoặc `error` |
| `status_code` | `INT` | Không | Response | HTTP status code |
| `response_time_ms` | `FLOAT` | Không | Middleware | Thời gian xử lý request theo ms |
| `file_size` | `BIGINT` | Có | File context | Kích thước file liên quan nếu có |
| `export_item_count` | `INT` | Có | Export context | Số item export nếu có |
| `export_total_size` | `BIGINT` | Có | Export context | Tổng dung lượng export nếu có |

---

## 4. Giá trị chuẩn

### 4.1. `action_type`

`action_type` là nhóm hành vi chính dùng cho feature engineering. Danh sách chuẩn:

```text
login
list
create
view_detail
edit
export
delete
restore
admin
other
```

Ví dụ mapping:

| Endpoint | action | action_type |
|---|---|---|
| `auth.login` | `login` | `login` |
| `documents.index` | `list_files` | `list` |
| `documents.create_folder` | `create_folder` | `create` |
| `documents.upload_file` | `upload_file` | `create` |
| `documents.file_detail` | `view_file_detail` | `view_detail` |
| `documents.download_file` | `download_file` | `view_detail` |
| `documents.rename_file` | `rename_file` | `edit` |
| `documents.move_file` | `move_file` | `edit` |
| `documents.share_file` | `share_file` | `edit` |
| `documents.export_files_csv` | `export_files_csv` | `export` |
| `documents.delete_file` | `delete_file` | `delete` |
| `documents.restore_file` | `restore_file` | `restore` |
| `admin.*` | `admin_*` | `admin` |

### 4.2. `resource_type` và `resource_id`

Không parse URL bằng regex rải rác. Log service chỉ lấy từ `request.view_args`:

```text
/files/<int:file_id>                  → resource_type=file, resource_id=file_id
/files/<int:file_id>/delete           → resource_type=file, resource_id=file_id
/files/<int:file_id>/restore          → resource_type=file, resource_id=file_id
/folders/<int:folder_id>              → resource_type=folder, resource_id=folder_id
/admin/users/<int:user_id>/toggle...  → resource_type=user, resource_id=user_id
```

### 4.3. `ownership_result`

```text
OWNER       User hiện tại là chủ tài nguyên
VIEWER      User hiện tại có share VIEWER còn hiệu lực
NONE        Tài nguyên tồn tại nhưng user không có quyền
NOT_FOUND   Không tìm thấy tài nguyên
ADMIN       Request của admin/admin endpoint
ANONYMOUS   Chưa đăng nhập
UNKNOWN     Không suy ra được do lỗi context lookup
```

### 4.4. `authorization_result`

```text
allowed   status_code từ 200 đến 399
denied    status_code là 401, 403 hoặc 404
error     status_code còn lại, ví dụ 500
```

StudyDrive có thể trả `404` cho file không tồn tại, file đã xóa hoặc file trái quyền để tránh xác nhận tài nguyên của user khác. Vì vậy cần dùng thêm `ownership_result` để phân tích.

### 4.5. `is_sensitive`

`is_sensitive = true` khi:

- `action_type` là `export`, `delete`, `restore`, `admin`; hoặc
- request thuộc endpoint admin/alerts; hoặc
- `action_type=view_detail` nhưng bị từ chối hoặc `ownership_result` là `NONE`, `NOT_FOUND`, `ANONYMOUS`.

Mục tiêu là giúp lọc nhanh hành vi phục vụ Export Abuse, Delete Abuse và IDOR/BOLA Scan.

---

## 5. Index bắt buộc

Các index cần có trong model/database:

```text
request_id unique
(timestamp)
(user_id, timestamp)
(session_id_hash, timestamp)
(action_type, timestamp)
(status_code, timestamp)
(session_id_hash, action_type, status_code)
(resource_type, resource_id)
(authorization_result, timestamp)
(is_sensitive, timestamp)
```

Nếu dùng MySQL đã có bảng cũ, cần `ALTER TABLE` để thêm cột mới trước khi query bằng model mới.

---

## 6. Kiểm tra sample 50 dòng

Sau khi thao tác web 50+ request, xuất sample:

```powershell
python -m scripts.export_request_log_sample --limit 50 --output samples/request_log_sample.csv
```

Kiểm tra thủ công:

```text
☐ 100% endpoint chính có action_type khác null
☐ /files/<id>, /download, /delete, /restore có resource_type=file và resource_id
☐ export/delete/admin/detail trái quyền có is_sensitive=1
☐ login fail có user_id null, is_authenticated=0
☐ request đã login có user_id, role, session_id_hash
☐ không có password, CSRF token, cookie thô, request body hoặc storage_path
```

---

## 7. Feature tương ứng cho ML

| Feature tương lai | Cột log liên quan |
|---|---|
| `request_count` | `request_id` |
| `unique_endpoint_count` | `endpoint` |
| `export_count`, `export_ratio` | `action_type=export` |
| `delete_count`, `delete_ratio` | `action_type=delete` |
| `sensitive_request_count` | `is_sensitive` |
| `forbidden_count`, `not_found_count` | `status_code` |
| `unique_resource_id_count` | `resource_id` |
| `resource_id_request_ratio` | `resource_id`, `request_id` |
| `avg_response_time_ms` | `response_time_ms` |
| `ownership_denied_count` | `ownership_result in NONE/NOT_FOUND/ANONYMOUS` |
