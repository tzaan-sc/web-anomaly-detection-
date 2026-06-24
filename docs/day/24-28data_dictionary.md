# Data dictionary — `request_logs` và `ground_truth`

Tài liệu này dùng cho ngày 25/06/2026: chứng minh log đầy đủ, nhất quán, an toàn và sẵn sàng sinh dataset lớn.

## 1. Quy tắc an toàn dữ liệu

- Không lưu password, cookie nguyên bản, CSRF token, session token nguyên bản, request body hoặc nội dung file.
- `path` chỉ là `request.path`, không gồm query string.
- `session_id_hash` là hash/định danh phiên do app tạo, không phải cookie thô.
- `storage_path` không xuất hiện trong log/dataset.
- Simulator chỉ chạy trên StudyDrive local.

## 2. Bảng `request_logs`

| Cột | Kiểu CSV/Pandas | Nguồn | Ý nghĩa | Dùng cho feature |
|---|---|---|---|---|
| `id` | int | DB | Khóa chính log nội bộ | không dùng train |
| `request_id` | string | middleware `before_request` | UUID duy nhất cho từng request | kiểm tra duplicate, mapping log |
| `timestamp` | datetime ISO | model default UTC | Thời điểm request/log | tạo cửa sổ 5 phút |
| `user_id` | int/null | session/current user | User gửi request; null nếu anonymous/login fail | group user/window |
| `username` | string/null | join users khi export | Tên user để audit thủ công | không dùng train |
| `is_authenticated` | bool 0/1 | session/current user | Request có đăng nhập hay không | lọc anonymous |
| `role` | string/null | user/session | USER/ADMIN/null | lọc admin khỏi train nếu cần |
| `session_id_hash` | string/null | session | Định danh phiên đã hash | group session/window |
| `ip_address` | string/null | request | IP local/client | audit, không bắt buộc feature |
| `user_agent` | string/null | request header | Browser/simulator | audit simulator |
| `http_method` | string | request | GET/POST/... | `unique_method_count` |
| `endpoint` | string/null | Flask endpoint | Route logic | `unique_endpoint_count` |
| `path` | string/null | request path | URL path không query | điều tra/filter |
| `action` | string/null | mapping endpoint | Hành động chi tiết | audit |
| `action_type` | category | mapping endpoint | Nhóm: login/list/create/view_detail/edit/export/delete/restore/admin/other | `export_count`, `delete_count`, ratios |
| `is_sensitive` | bool 0/1 | log service | Export/delete/restore/admin/detail trái quyền | `sensitive_request_count`, `sensitive_ratio` |
| `resource_type` | category/null | `request.view_args` | file/folder/user/share/null | feature resource |
| `resource_id` | string/null | `request.view_args` | ID tài nguyên theo route | `unique_resource_id_count`, BOLA |
| `owner_id` | int/null | context lookup | Chủ tài nguyên nếu xác định được | audit authorization |
| `permission` | category/null | context lookup | OWNER/VIEWER/NONE/ADMIN/... | audit |
| `ownership_result` | category/null | context lookup | OWNER/VIEWER/NONE/NOT_FOUND/ADMIN/ANONYMOUS/UNKNOWN | BOLA/error feature |
| `authorization_result` | category | status code | allowed/denied/error | `denied_count`, audit |
| `status_code` | int | response | HTTP status | `error_rate`, `forbidden_rate`, `not_found_rate` |
| `response_time_ms` | float | middleware timer | Thời gian xử lý ms | `avg_response_time_ms` |
| `file_size` | int/null | context file | Dung lượng file liên quan | tổng/avg file size nếu dùng |
| `export_item_count` | int/null | export context | Số item export nếu có | optional export feature |
| `export_total_size` | int/null | export context | Tổng dung lượng export nếu có | optional export feature |

## 3. Bảng `ground_truth.csv`

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `scenario_id` | string | ID duy nhất cho một scenario run cụ thể |
| `scenario` | category | `normal`, `export_abuse`, `delete_abuse`, `bola_scan` |
| `label` | int | `0` normal, `1` anomaly |
| `run_id` | string | ID lần sinh dữ liệu, dùng để split chống leakage |
| `user_id` | int | User chạy scenario |
| `username` | string | Username demo |
| `session_name` | string | Profile normal hoặc mode anomaly |
| `severity` | category | normal/mild/medium/high hoặc mode tương ứng |
| `started_at` | datetime ISO | Bắt đầu scenario |
| `ended_at` | datetime ISO | Kết thúc scenario |
| `request_count` | int | Số request ước lượng do script tạo |
| `notes` | string | Ghi chú: target IDs, profile, điều kiện chạy |

## 4. Checklist audit ngày 25

```text
☐ Pandas đọc CSV không lỗi
☐ request_id không trùng
☐ timestamp parse được sang datetime
☐ response_time_ms là numeric
☐ is_authenticated/is_sensitive chỉ gồm 0/1 hoặc True/False
☐ login fail có user_id null
☐ 403/404 vẫn có dòng log
☐ không có password/token/cookie/body/storage_path trong CSV
```

## 5. Lệnh kiểm tra nhanh

```powershell
python -m scripts.export_logs --output data/raw/logs_test.csv
python -m scripts.audit_logs --input data/raw/logs_test.csv --output docs/data_audit.md
```
