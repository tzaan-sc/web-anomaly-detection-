# BÁO CÁO TỔNG KẾT ĐỒ ÁN CÔNG NGHỆ THÔNG TIN 3
## XÂY DỰNG HỆ THỐNG PHÁT HIỆN HÀNH VI TRUY CẬP BẤT THƯỜNG TRÊN ỨNG DỤNG WEB BẰNG MACHINE LEARNING

**TRƯỜNG ĐẠI HỌC KỸ THUẬT - CÔNG NGHỆ CẦN THƠ**  
**KHOA CÔNG NGHỆ THÔNG TIN**  

* **Cán bộ hướng dẫn:** ThS. Nguyễn Trung Kiên  
* **Sinh viên thực hiện:** Ngô Thu Vân  
* **Mã số sinh viên:** CNTT2311044  
* **Năm thực hiện:** 2026  

---

## TỔNG QUAN NỘI DUNG NGHIÊN CỨU

### 1. Bối cảnh & Mục tiêu
Các hệ thống web lưu trữ và chia sẻ tệp tin trực tuyến thường xuyên phải đối mặt với nguy cơ tấn công Lạm dụng logic nghiệp vụ (Business Logic Abuse) và lỗ hổng Kiểm soát truy cập đối tượng (BOLA/IDOR). Các cuộc tấn công này sử dụng các HTTP Request hoàn toàn hợp lệ về cú pháp nên dễ dàng vượt qua các hệ thống tường lửa WAF và IDS truyền thống.

Đề tài giải quyết vấn đề trên bằng cách phát triển nền tảng web **StudyDrive** (Flask, MySQL), tích hợp cơ chế ghi nhật ký có cấu trúc (**Structured Request Logging**) tại tầng Middleware và áp dụng thuật toán học máy không giám sát **Isolation Forest** trên các cửa sổ trượt 5 phút với **vector 25 đặc trưng số** để phát hiện sớm các hành vi dị biệt.

---

## 2. Không gian 25 Đặc trưng Hành vi

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   DANH MỤC 25 ĐẶC TRƯNG HÀNH VI (ml/build_features.py)           │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. Nhóm Lưu lượng & Tần suất (Traffic & Velocity):                               │
│    - x1: request_count (Tổng số request trong cửa sổ 5 phút)                     │
│    - x2: unique_endpoint_count (Số endpoint duy nhất được gọi)                  │
│    - x3: unique_method_count (Số phương thức HTTP sử dụng)                      │
│    - x4: session_duration_sec (Thời lượng phiên hoạt động trong cửa sổ)         │
│    - x5: avg_inter_request_sec (Khoảng cách thời gian trung bình giữa 2 request) │
│    - x6: min_inter_request_sec (Khoảng cách ngắn nhất giữa 2 request liên tiếp) │
│    - x7: burst_rate (Tốc độ bùng nổ: request_count / session_duration_sec)      │
│                                                                                  │
│ 2. Nhóm Lỗi & Phân quyền (Errors & Authorization):                               │
│    - x8: error_rate (Tỷ lệ request có mã phản hồi HTTP >= 400)                  │
│    - x9: forbidden_count (Số lượng mã lỗi 403 Forbidden)                         │
│    - x10: forbidden_rate (Tỷ lệ lỗi 403 trên tổng số request)                   │
│    - x11: not_found_count (Số lượng mã lỗi 404 Not Found)                       │
│    - x12: not_found_rate (Tỷ lệ lỗi 404 trên tổng số request)                   │
│    - x13: unique_failed_resource_id_count (Số ID tài nguyên bị từ chối truy cập) │
│                                                                                  │
│ 3. Nhóm Lạm dụng Nghiệp vụ (Business Logic Abuse):                               │
│    - x14: export_count (Số lượng thao tác xuất/tải dữ liệu)                      │
│    - x15: export_ratio (Tỷ lệ thao tác xuất dữ liệu trên tổng request)          │
│    - x16: delete_count (Số lượng thao tác xóa tài nguyên)                       │
│    - x17: delete_ratio (Tỷ lệ thao tác xóa tài nguyên trên tổng request)        │
│    - x18: unique_deleted_resource_count (Số lượng tài nguyên khác nhau bị xóa)  │
│                                                                                  │
│ 4. Nhóm Dò quét Tài nguyên (Resource Exploration):                               │
│    - x19: unique_resource_id_count (Số lượng ID tài nguyên khác nhau được gọi)  │
│    - x20: resource_id_request_ratio (Tỷ lệ request có tương tác với tài nguyên) │
│    - x21: resource_id_change_rate (Tần suất chuyển đổi giữa các resource_id)    │
│                                                                                  │
│ 5. Nhóm Nhạy cảm & Hiệu năng (Sensitivity & Latency):                            │
│    - x22: sensitive_request_count (Số lượng thao tác nhạy cảm)                   │
│    - x23: sensitive_ratio (Tỷ lệ thao tác nhạy cảm trên tổng request)           │
│    - x24: max_sensitive_streak (Chuỗi dài nhất các thao tác nhạy cảm liên tiếp)│
│    - x25: avg_response_time_ms (Thời gian phản hồi trung bình của máy chủ)       │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Kiến trúc Huấn luyện & Đánh giá Mô hình

1. **Chiến lược Huấn luyện (Normal-only Training):** Mô hình chỉ học trên tập dữ liệu hành vi bình thường để thiết lập đường cơ sở (baseline) mà không phụ thuộc vào nhãn tấn công.
2. **Kỹ thuật Chống Rò rỉ Dữ liệu (Group-aware Split):** Toàn bộ các cửa sổ thời gian được phân chia theo cặp `user_id|session_id_hash` và `run_id`, đảm bảo phiên của cùng một người dùng không bị phân mảnh vào các tập khác nhau.
3. **Phân bố Dữ liệu Thực nghiệm:**
   - **Tập Train:** 8 cửa sổ (100% Normal).
   - **Tập Validation:** 6 cửa sổ (3 Normal, 3 Anomaly) phục vụ Grid Search siêu tham số ($n_{\text{estimators}}=100$, $\text{max\_samples}=\text{'auto'}$, $\text{threshold}=\text{Percentile 95.0\%}$).
   - **Tập Test:** 5 cửa sổ độc lập (2 Normal, 3 Anomaly).
4. **Kết quả Đánh giá Định lượng:**
   - **Accuracy:** 100.0%
   - **Precision:** 100.0%
   - **Recall:** 100.0%
   - **F1-Score:** 1.000
   - **False Positive Rate:** 0.0%

---

## 4. Tích hợp Hệ thống & Phòng thủ Chủ động (Active Defense)

- **Alerts Dashboard:** Cung cấp giao diện trực quan cho quản trị viên theo dõi các cảnh báo dị biệt, phân tích Top 3 đặc trưng ảnh hưởng và truy vết ngược về từng bản ghi request log gốc.
- **Active Defense:** Khi phát hiện hành vi vượt ngưỡng bất thường, hệ thống tự động khóa tạm thời tài khoản vi phạm trong 60 phút (`user.is_locked = True`, `user.locked_until = now + 60min`), lập tức ngăn chặn nguy cơ phá hoại tiếp theo thông qua middleware `active_defense.py`.
- **Bộ Kiểm thử Tự động:** Hoàn thành **44 / 44 test cases** (100% Passed) kiểm tra toàn diện chức năng web, bảo mật phân quyền, ghi log middleware và pipeline Machine Learning.
