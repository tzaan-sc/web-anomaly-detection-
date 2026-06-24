# Data generation plan — Week 3 raw logs v1

## 1. Mục tiêu

Sinh `request_logs_raw.csv` khoảng 5.000–10.000 dòng, có normal và 3 anomaly: Export Abuse, Delete Abuse, IDOR/BOLA Scan. Dữ liệu phải có biến thiên theo user/session, không quá đều, và có `ground_truth.csv` để đối chiếu nhãn.

## 2. Time window và nhãn

- Cửa sổ feature chính: 5 phút.
- Group key đề xuất: `user_id + session_id_hash + window_start`.
- `ground_truth.csv` ghi theo khoảng `started_at` → `ended_at` của từng scenario run.
- Khi build feature, một window được gắn anomaly nếu overlap với scenario có `label=1`.

## 3. Normal profiles

| Profile | Hành vi chính | Tín hiệu mong muốn |
|---|---|---|
| `casual` | list/search/detail/download nhẹ | request đều vừa, ít sensitive |
| `active` | detail/download/upload/rename thỉnh thoảng | đa dạng endpoint nhưng không burst cực đoan |
| `reviewer` | xem và tải nhiều file được share/owned | view_detail/download cao nhưng vẫn hợp lệ |

Normal được phép có export/delete rất hiếm, nhưng không tạo nhiều 403/404 liên tiếp.

## 4. Anomaly scripts

| Script | Mục tiêu | Tín hiệu log |
|---|---|---|
| `simulate_export_abuse.py` | Export metadata nhiều lần liên tục | `action_type=export`, `is_sensitive=1`, burst cao |
| `simulate_delete_abuse.py` | Soft delete nhiều file của chính user | `action_type=delete`, nhiều `resource_id`, sensitive cao |
| `simulate_bola_scan.py` | Thử file ID của user khác/không tồn tại | nhiều `404`, `ownership_result=NONE/NOT_FOUND`, unique resource cao |

Tất cả script chỉ chạy trên `http://127.0.0.1:5000` hoặc base URL local do mình truyền vào.

## 5. Lệnh chạy thử nhỏ

Terminal 1:

```powershell
python run.py
```

Terminal 2:

```powershell
python -m scripts.reset_demo
python -m scripts.simulate_normal --fast --requests 300
python -m scripts.simulate_export_abuse --fast --severity mild
python -m scripts.simulate_delete_abuse --fast --severity mild
python -m scripts.simulate_bola_scan --fast --mode burst
python -m scripts.export_logs --output data/raw/request_logs_raw.csv
python -m scripts.audit_logs --input data/raw/request_logs_raw.csv --output docs/data_audit.md
```

## 6. Lệnh sinh raw v1

```powershell
python -m scripts.generate_raw_dataset_v1 --fast --normal-requests 5000
```

Đầu ra:

```text
data/raw/request_logs_raw.csv
data/raw/ground_truth.csv
data/raw/generation_metadata.json
docs/data_audit.md
```

## 7. Tiêu chí khóa raw v1

```text
☐ 5.000–10.000 log
☐ đủ normal + export_abuse + delete_abuse + bola_scan
☐ request_id không trùng
☐ timestamp hợp lệ
☐ Pandas đọc CSV không lỗi
☐ không có secret/password/token/cookie/body
☐ ground_truth đối chiếu được bằng user_id + started_at/ended_at
```
