# Ground truth schema

File: `data/raw/ground_truth.csv`

| Cột | Bắt buộc | Ví dụ | Ghi chú |
|---|---:|---|---|
| `scenario_id` | Có | `export_abuse:raw_v1_20260628:user1` | ID duy nhất cho scenario run |
| `scenario` | Có | `normal`, `export_abuse`, `delete_abuse`, `bola_scan` | Tên scenario |
| `label` | Có | `0` hoặc `1` | 0 normal, 1 anomaly |
| `run_id` | Có | `raw_v1_20260628_101500` | Dùng để split chống leakage |
| `user_id` | Có | `2` | User trong DB |
| `username` | Có | `user1` | Dễ audit thủ công |
| `session_name` | Có | `casual`, `active`, `burst` | Profile/mode |
| `severity` | Có | `normal`, `mild`, `medium`, `high` | Mức độ scenario |
| `started_at` | Có | `2026-06-28T03:00:00+00:00` | ISO UTC |
| `ended_at` | Có | `2026-06-28T03:04:30+00:00` | ISO UTC |
| `request_count` | Có | `120` | Số request ước lượng do simulator tạo |
| `notes` | Không | `target_ids=[...]` | Ghi chú phục vụ audit |
