# Báo Cáo Tiến Độ Đồ Án — Tổng Kết Toàn Diện Dự Án

> **Tên đề tài:** Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning  
> **Sinh viên thực hiện:** Ngô Thu Vân (MSSV: CNTT2311044)  
> **Cán bộ hướng dẫn:** ThS. Nguyễn Trung Kiên  
> **Trạng thái:** ✅ **HOÀN THÀNH 100% CÁC HẠNG MỤC**

---

## 1. Bảng Tổng Hợp Trạng Thái Các Giai Đoạn Triển Khai

| Giai đoạn | Hạng mục công việc chính | Kết quả & Minh chứng kỹ thuật | Trạng thái |
|---|---|---|---|
| **Tuần 1: Nền tảng Ứng dụng & Xác thực** | - Khởi tạo kiến trúc Flask Blueprint đa tầng.<br>- Thiết kế các Model cơ sở dữ liệu SQLAlchemy.<br>- Xây dựng chức năng Xác thực (Login, Logout, Register).<br>- Tích hợp Middleware, Decorators kiểm tra phiên. | - `app/models/` đầy đủ 7 entities.<br>- `app/blueprints/auth/` hỗ trợ đăng nhập & đăng ký.<br>- Hashing mật khẩu an toàn với Werkzeug. | ✅ Hoàn thành 100% |
| **Tuần 2: Ứng dụng Web StudyDrive Hoàn Chỉnh** | - Quản lý tệp tin vật lý (`instance/uploads/`).<br>- Tạo thư mục cha - con đa cấp.<br>- Cơ chế phân quyền cấp đối tượng (`OWNER`, `VIEWER`).<br>- Xóa mềm (Soft Delete) & Thùng rác (Trash).<br>- Xuất danh sách tệp tin dạng CSV (`export_jobs`). | - `app/services/document_service.py` (22 KB).<br>- `app/blueprints/documents/` đầy đủ CRUD.<br>- Giao diện Bootstrap 5 tương thích cao. | ✅ Hoàn thành 100% |
| **Tuần 3: Structured Logging & Simulators** | - Xây dựng Middleware ghi log tự động 21 trường.<br>- Băm SHA-256 đối với Session ID.<br>- Phát triển 4 bộ mô phỏng hành vi truy cập.<br>- Thu thập bộ dữ liệu thô chuẩn hóa. | - `app/middleware/request_logging.py`.<br>- 4 script giả lập (`simulate_*.py`).<br>- Tập dữ liệu thô `request_logs_raw.csv` (10.875 logs). | ✅ Hoàn thành 100% |
| **Tuần 4: Feature Engineering & Chống rò rỉ dữ liệu** | - Thuật toán cửa sổ trượt 5 phút (5-min sliding window).<br>- Trích xuất vector 25 đặc trưng số.<br>- Kỹ thuật chia tập Group-aware Split (theo phiên/người dùng).<br>- Phân tích dữ liệu khám phá (EDA). | - `ml/build_features.py` (28 KB).<br>- `data/processed/features_v1/` gồm 19 cửa sổ.<br>- `train_features.csv`, `validation_features.csv`, `test_features.csv`. | ✅ Hoàn thành 100% |
| **Tuần 5: Huấn luyện, Tối ưu & Tích hợp ML** | - Huấn luyện mô hình Isolation Forest (Normal-only).<br>- Tối ưu hóa siêu tham số (Grid Tuning) trên tập Validation.<br>- Đánh giá định lượng trên tập Test.<br>- Xuất biểu đồ Confusion Matrix & Score Distribution.<br>- Tích hợp dịch vụ phát hiện (`detection_service.py`). | - `artifacts/models/iforest_v1/model.joblib`.<br>- `artifacts/metrics/test_metrics.json`.<br>- `artifacts/metrics/confusion_matrix.png`.<br>- `app/services/detection_service.py`. | ✅ Hoàn thành 100% |
| **Tuần 6: Dashboard, Active Defense & Kiểm thử** | - Xây dựng Alerts Dashboard trực quan hóa.<br>- Tích hợp cơ chế Phòng thủ chủ động (Active Defense).<br>- Tính năng truy vết ngược từ Alert về Request Log thô.<br>- Viết toàn bộ 44 test cases tự động bằng Pytest. | - `app/blueprints/alerts/` & `templates/alerts/`.<br>- `app/middleware/active_defense.py` (khóa tự động 60 phút).<br>- **44/44 bài test tự động PASSED**. | ✅ Hoàn thành 100% |

---

## 2. Số Liệu Kỹ Thuật Đạt Được

- **Dữ liệu thực nghiệm:** 10.875 bản ghi HTTP Request Log thô có cấu trúc đầy đủ.
- **Không gian đặc trưng:** 25 đặc trưng số phản ánh toàn diện tốc độ, lỗi phân quyền, lạm dụng logic và dò quét tài nguyên.
- **Phân chia tập dữ liệu:** 19 cửa sổ thời gian 5 phút được chia thành Train (8 cửa sổ Normal), Validation (6 cửa sổ) và Test (5 cửa sổ) theo phương pháp **Group-aware Split** chống rò rỉ dữ liệu tuyệt đối.
- **Mô hình học máy:** Isolation Forest (Normal-only Training), ngưỡng phát hiện Percentile 95.0%, lưu trữ dạng artifact `model.joblib`.
- **Kiểm thử tự động:** **44 / 44 tests passed** (100% đạt chuẩn) trên toàn bộ các tầng Web, Service, Middleware và ML Pipeline.

---

## 3. Lời Trình Bày Chuẩn Bị Báo Cáo Với Hội Đồng Chấm

> *"Kính thưa quý Thầy Cô trong Hội đồng, em đã hoàn thành 100% toàn bộ các mục tiêu nghiên cứu và phát triển của đề tài. Hệ thống StudyDrive được xây dựng hoàn chỉnh với đầy đủ các phân hệ nghiệp vụ, phân quyền tài nguyên, bảo mật thông tin và ghi nhật ký có cấu trúc tại tầng Middleware. Pipeline Machine Learning sử dụng thuật toán Isolation Forest với 25 đặc trưng hành vi và chiến lược huấn luyện Normal-only đã được huấn luyện, tinh chỉnh siêu tham số và đánh giá nghiêm ngặt theo kỹ thuật Group-aware Split để chống rò rỉ dữ liệu. Các cảnh báo bất thường liên quan đến Export Abuse, Delete Abuse và BOLA/IDOR Scan được tích hợp trực tiếp lên giao diện Alerts Dashboard kèm cơ chế phòng thủ chủ động Active Defense tự động khóa tạm thời tài khoản nghi vấn. Toàn bộ hệ thống đã vượt qua 44 bài kiểm thử tự động với tỷ lệ đạt 100% và sẵn sàng cho buổi bảo vệ đồ án."*
