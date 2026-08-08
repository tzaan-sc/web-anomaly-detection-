# 05. LỊCH SỬ PHÁT TRIỂN & HƯỚNG DẪN (DEVELOPMENT HISTORY & GUIDES)

## 1. Ghi chú Quá trình Phát triển (Development History)
Dự án được thực hiện qua các tuần với các mốc chính:

- **Tuần 1-2:** Hoàn thiện cơ chế Authentication, Session, CSRF, và Authorization (OWNER/VIEWER). Xây dựng ứng dụng web StudyDrive quản lý tệp, chia sẻ, thùng rác, export.
- **Tuần 3:** Xây dựng hệ thống Log (Structured Request Logging). Sinh dữ liệu normal và anomaly (Export Abuse, Delete Abuse, BOLA Scan).
- **Tuần 4:** Tiền xử lý dữ liệu (Data Cleaning & Windowing). Feature Engineering (tính toán các đặc trưng trên cửa sổ thời gian 5 phút). Chia tập Train/Val/Test.
- **Tuần 5:** Huấn luyện mô hình Isolation Forest, tuning tham số, đánh giá trên test set. Đóng gói mô hình.
- **Tuần 6:** Tích hợp Detection vào web (Admin Alerts Dashboard). Kiểm thử hồi quy toàn bộ hệ thống.

## 2. Kịch bản Demo & Testing
Để chạy toàn bộ quá trình demo hệ thống, sử dụng các script trong thư mục `scripts/`:

1. **Reset Database:**
   ```powershell
   python -m scripts.reset_demo
   ```
2. **Khởi động Server:**
   ```powershell
   python run.py
   ```
3. **Sinh dữ liệu kịch bản (Scenario Data Generation):**
   ```powershell
   python -m scripts.run_demo_scenario --scenario all --fast --normal-requests 500
   ```
4. **Phân tích Alerts (trên Giao diện):**
   - Đăng nhập Admin.
   - Mở menu `Alerts`, chạy "Run Detection".
   - Xem chi tiết cảnh báo, kiểm tra log gốc bị đánh dấu là bất thường.

## 3. Các quyết định thiết kế đã chốt (Consistency Report)
- File vật lý đặt trong `instance/uploads/`.
- Database chính là `instance/app.db` (SQLite dùng cho local/demo).
- Log được lưu qua middleware và không chặn request chính nếu ghi log bị lỗi.
- Chỉ Bulk export tệp do người dùng sở hữu (OWNER).
- Admin export log ra CSV, không được tải nội dung tệp của User.
