# Feature dictionary — features_v1

Các feature được tính ở cấp `user_id + session_id_hash + 5-minute window`.
`label`, `scenario`, `run_id`, `timestamp` và các identifier không được đưa vào X_train.

| Feature | Ý nghĩa |
|---|---|
| `request_count` | Số request trong cửa sổ. |
| `unique_endpoint_count` | Số endpoint khác nhau được gọi. |
| `unique_method_count` | Số HTTP method khác nhau. |
| `session_duration_sec` | Khoảng cách từ request đầu đến request cuối trong window. |
| `avg_inter_request_sec` | Khoảng cách trung bình giữa hai request liên tiếp. |
| `min_inter_request_sec` | Khoảng cách nhỏ nhất giữa hai request liên tiếp. |
| `burst_rate` | Tỷ lệ khoảng cách request <= 1 giây. |
| `error_rate` | Tỷ lệ status_code >= 400. |
| `avg_response_time_ms` | Thời gian xử lý trung bình. |
| `sensitive_request_count` | Số request nhạy cảm: export/delete/admin/detail trái quyền. |
| `sensitive_ratio` | Tỷ lệ request nhạy cảm. |
| `export_count` | Số request thuộc action export. |
| `export_ratio` | Tỷ lệ export trong window. |
| `delete_count` | Số request thuộc action delete. |
| `delete_ratio` | Tỷ lệ delete trong window. |
| `unique_deleted_resource_count` | Số resource_id khác nhau bị delete. |
| `unique_resource_id_count` | Số resource_id khác nhau xuất hiện. |
| `resource_id_request_ratio` | unique_resource_id_count / request_count. |
| `forbidden_count` | Số request trả 403. |
| `forbidden_rate` | Tỷ lệ request trả 403. |
| `not_found_count` | Số request trả 404. |
| `not_found_rate` | Tỷ lệ request trả 404. |
| `unique_failed_resource_id_count` | Số resource_id khác nhau trong request 403/404. |
| `resource_id_change_rate` | Tỷ lệ resource_id thay đổi giữa request liên tiếp. |
| `max_sensitive_streak` | Chuỗi request nhạy cảm liên tiếp dài nhất. |