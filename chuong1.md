# THÔNG TIN ĐẦU VÀO – CHƯƠNG 1

## 1. Thông tin đồ án
- **Tên đề tài:** Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning (StudyDrive).

## 2. Hệ thống được xây dựng
- **Website là:** StudyDrive - Ứng dụng web quản lý, lưu trữ và chia sẻ tệp tin trực tuyến được phát triển trên nền tảng Python Flask, CSDL MySQL / SQLite và giao diện Bootstrap 5.
- **Website dùng để:** Cung cấp môi trường làm việc trực tuyến cho người dùng lưu trữ, quản lý, chia sẻ và xuất bản tài liệu; đồng thời tích hợp cơ chế ghi nhật ký truy cập cấu trúc (Structured Request Logging) tầng ứng dụng để giám sát an ninh và phát hiện hành vi bất thường bằng Machine Learning.
- **Người dùng có thể:**
  - Đăng ký tài khoản, đăng nhập, đăng xuất và quản lý phiên làm việc bằng Session Cookie (HttpOnly).
  - Quản lý cây thư mục cá nhân (tạo mới, xem danh sách thư mục).
  - Tải lên tệp tin (upload) với giới hạn kích thước tối đa 20MB, lọc định dạng tệp an toàn (PDF, DOC/X, XLS/X, PPT/X, TXT, CSV, PNG, JPG/JPEG, ZIP; cấm tệp thực thi EXE, SH, PY, JS...; lưu trữ tệp vật lý bằng mã UUID tại `instance/uploads/`).
  - Xem thông tin chi tiết tệp, xem danh sách tệp (hỗ trợ tìm kiếm, lọc loại tệp, sắp xếp, phân trang).
  - Tải xuống (download) các tệp tin thuộc quyền sở hữu (`OWNER`) hoặc tệp tin được chia sẻ (`VIEWER`).
  - Đổi tên tệp tin (rename), di chuyển tệp tin (move) giữa các thư mục.
  - Chia sẻ từng tệp tin lẻ cho người dùng khác trong hệ thống với quyền chỉ xem (`VIEWER`).
  - Thực hiện các tác vụ xuất dữ liệu (Export): xuất danh sách metadata ra file CSV hoặc đóng gói hàng loạt tệp tin do mình sở hữu thành tệp nén ZIP.
  - Quản lý Thùng rác (Trash): thực hiện xóa mềm (soft-delete, gắn cờ `is_deleted = True`) tệp tin/thư mục, xem danh sách thùng rác, khôi phục lại dữ liệu (Restore) hoặc xóa vĩnh viễn (Permanent Delete).
- **Admin có thể:**
  - Đăng nhập vào giao diện Quản trị riêng biệt (`/admin`).
  - Xem thống kê tổng quan hệ thống (số lượng người dùng, thư mục, tệp tin, nhật ký truy cập, cảnh báo).
  - Quản lý danh sách người dùng toàn hệ thống (xem thông tin, thực hiện khóa tài khoản `is_active = False` hoặc mở khóa tài khoản).
  - Xem danh sách và metadata tệp tin toàn hệ thống (không mặc định xem hoặc tải nội dung tệp tin riêng tư của người dùng).
  - Quản lý nhật ký truy cập (`request_logs`): tìm kiếm, lọc log theo mốc thời gian, người dùng, loại hành động (`action_type`), mã trạng thái HTTP (`status_code`), cờ nhạy cảm (`is_sensitive`), từ khóa đường dẫn URI; phân trang; xem chi tiết từng log và xuất dữ liệu log ra file CSV.
  - Thực hiện chạy tiến trình phát hiện bất thường ML (`Run Detection`) trực tiếp trên giao diện web (`/admin/detection/run`) hoặc qua script (`scripts/run_detection.py`).
  - Quản lý danh sách cảnh báo (`alerts`): xem danh sách cảnh báo lọc theo trạng thái (`Pending`, `Investigating`, `Resolved`, `Ignored`), xem điểm `anomaly_score`, gợi ý kịch bản (`scenario_hint`), xem chi tiết vector 25 đặc trưng (JSON) và truy ngược về danh sách request log gốc thuộc cửa sổ thời gian 5 phút bị nghi ngờ.

## 3. Lý do chọn đề tài
- **Bối cảnh & Thách thức thực tế:** Sự bùng nổ của các ứng dụng Web lưu trữ và chia sẻ tài liệu trực tuyến đặt ra thách thức lớn về an toàn thông tin. Bên cạnh các tấn công cú pháp truyền thống, rủi ro hàng đầu hiện nay đến từ các hành vi **Lạm dụng Logic Nghiệp vụ (Business Logic Abuse)** và **Lỗ hổng Phân quyền Cấp Đối tượng (BOLA/IDOR)** — nơi kẻ tấn công sử dụng các HTTP Request hoàn toàn hợp lệ nhưng thực hiện dồn dập các thao tác như xuất dữ liệu hàng loạt (*Export Abuse*), xóa phá hoại tài nguyên (*Delete Abuse*) hoặc rà quét IDOR (*IDOR/BOLA Scan*).
- **Hạn chế của giải pháp truyền thống:** Các cơ chế bảo mật dựa trên chữ ký như WAF/IDS thường bất lực trước các đợt lạm dụng nghiệp vụ vì từng request riêng lẻ không chứa payload độc hại. Trong khi đó, việc thiết lập các quy tắc cố định (Rule-based) thường cứng nhắc, dễ tạo ra nhiều báo động giả (False Positives) hoặc bỏ sót các đợt tấn công giãn cách thời gian (low-and-slow).
- **Tính cấp thiết của Machine Learning:** Việc ứng dụng **Machine Learning không giám sát (Isolation Forest)** trên chuỗi nhật ký truy cập (request logs) là hướng đi tối ưu. Phương pháp này cho phép hệ thống tự động học phân bố hành vi bình thường của người dùng từ log, từ đó phát hiện linh hoạt các chuỗi hành vi bất thường theo cửa sổ thời gian 5 phút mà không phụ thuộc vào nhãn tấn công hay chữ ký biết trước.
- **Ý nghĩa & Đóng góp của Đề tài:** Xuất phát từ thực tiễn đó, nhóm chọn đề tài **“Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning”** trên ứng dụng **StudyDrive**. Đề tài xây dựng một **quy trình khép kín** từ thu thập log cấu trúc tại Middleware, trích xuất đặc trưng cửa sổ 5 phút, phát hiện bất thường bằng Isolation Forest đến tự động phát cảnh báo và hỗ trợ Admin truy ngược log gốc.

## 4. Bài toán
- **Input:** Dữ liệu Nhật ký truy cập cấu trúc tầng ứng dụng (`request_logs`) thu thập tự động từ mọi HTTP Request của người dùng qua Flask Middleware, chứa các trường metadata: `request_id`, `timestamp`, `user_id`, `session_id_hash`, `ip_address`, `http_method`, `endpoint`, `action`, `action_type`, `is_sensitive`, `resource_type`, `resource_id`, `authorization_result`, `status_code`, `response_time_ms`.
- **Dữ liệu được phân tích:** Chuỗi log truy cập được gom nhóm theo cửa sổ thời gian không chồng lấp **5 phút** (5-minute sliding window) dựa trên cặp nhận diện `(user_id, session_id_hash)`. Cửa sổ log này sau đó được biến đổi thành vector đặc trưng số 25 chiều (với 11 đặc trưng toán học cốt lõi).
- **Output:**
  - Nhãn phân loại cho cửa sổ 5 phút: `0: Bình thường (Normal)` hoặc `1: Bất thường (Anomaly)`.
  - Điểm bất thường (`anomaly_score` từ 0 đến 1) và so sánh với ngưỡng `threshold` phân vị (mốc 90.0% / 95.0%).
  - Gợi ý kịch bản bất thường (`scenario_hint`: Export Abuse, Delete Abuse, BOLA Scan).
  - Bản ghi Cảnh báo (`Alert`) được lưu vào CSDL và hiển thị trên Admin Alerts Dashboard.
- **ML được sử dụng ở:** Phân hệ **ML Detection Engine** (các module `ml/build_features.py`, `ml/train.py`, `ml/detect.py` và `app/services/detection_service.py`), chịu trách nhiệm trích xuất đặc trưng từ log thô trong CSDL, chạy mô hình Isolation Forest để tính điểm bất thường và tự động tạo cảnh báo cho Admin.
- **Quy trình hoạt động:**
  1. **Thu thập Log:** Người dùng/Kẻ tấn công tương tác trên Web StudyDrive -> Middleware `request_logging.py` bắt sự kiện `after_request` và ghi log cấu trúc vào bảng `request_logs` (băm SHA-256 session ID, không log password/token).
  2. **Gom nhóm Cửa sổ (Windowing):** Khi tiến trình Detection kích hoạt (thủ công từ Admin Dashboard hoặc chạy script `scripts/run_detection.py`), hệ thống đọc `request_logs` theo khoảng thời gian yêu cầu và phân chia thành các cửa sổ 5 phút theo `(user_id, session_id_hash)`.
  3. **Trích xuất Đặc trưng (Feature Engineering):** Module `build_features` tính toán vector 25 đặc trưng (tần suất request, tỷ lệ lỗi, số lượng export/delete, số tài nguyên thất bại...) cho từng cửa sổ.
  4. **Chạy Mô hình ML (Scoring):** Đưa vector đặc trưng qua mô hình Isolation Forest đã huấn luyện (`model.joblib`) để tính `anomaly_score`.
  5. **Quyết định Ngưỡng & Tạo Cảnh báo (Alerting):** Nếu `anomaly_score >= threshold`, hệ thống ghi nhận cửa sổ đó là bất thường, xác định `scenario_hint` nổi bật và tạo bản ghi `Alert` lưu vào CSDL.
  6. **Giám sát & Truy ngược (Forensics):** Admin xem cảnh báo trên web, kiểm tra thông số đặc trưng (JSON) và nhấn link để xem danh sách log thô tương ứng trong cửa sổ 5 phút đó.

## 5. Mục tiêu
- **Mục tiêu tổng quát:** Xây dựng thành công ứng dụng web lưu trữ tệp StudyDrive tích hợp hệ thống ghi log cấu trúc tự động và mô hình Machine Learning không giám sát (Isolation Forest) để phát hiện kịp thời các kịch bản lạm dụng logic nghiệp vụ và tấn công phân quyền tệp tin.
- **Mục tiêu cụ thể:**
  1. Thiết kế và phát triển ứng dụng Web StudyDrive chuẩn hóa (Python Flask, SQLAlchemy, MySQL/SQLite, Bootstrap 5) với đầy đủ chức năng quản lý tệp, chia sẻ phân quyền (OWNER/VIEWER), thùng rác, xuất dữ liệu và giao diện quản trị Admin.
  2. Xây dựng Middleware ghi log tầng ứng dụng (Structured Request Logger) tự động capture mọi HTTP Request mà không ảnh hưởng tới hiệu năng và tuân thủ nguyên tắc bảo vệ PII (băm SHA-256 session ID, không log mật khẩu/token).
  3. Phát triển 4 script mô phỏng dữ liệu (`simulate_normal.py`, `simulate_export_abuse.py`, `simulate_delete_abuse.py`, `simulate_bola_scan.py`) tạo ra bộ dữ liệu log thô > 5.500 dòng log có ground truth.
  4. Xây dựng Pipeline tiền xử lý, trích xuất 25 đặc trưng theo cửa sổ 5 phút và phân chia tập dữ liệu Train/Val/Test chống rò rỉ dữ liệu (Group-aware Anti Data Leakage).
  5. Huấn luyện, tối ưu siêu tham số bằng Grid Search và đóng gói mô hình Isolation Forest (`model.joblib`).
  6. Xây dựng giao diện Admin Logs và Alerts Dashboard cho phép Admin lọc, tìm kiếm, kích hoạt detection và truy ngược log thô từ cảnh báo.
  7. Viết bộ kiểm thử tự động (Test Suite 38 test cases với Pytest) chứng minh tính ổn định của ứng dụng và pipeline ML.

## 6. Đối tượng nghiên cứu
- Nhật ký truy cập tầng ứng dụng Web (HTTP Request Logs).
- Chuỗi hành vi người dùng trên hệ thống lưu trữ và chia sẻ tệp tin StudyDrive.
- Kỹ thuật gom nhóm theo cửa sổ thời gian (Time-Windowing 5 phút) và trích xuất đặc trưng chuỗi hành vi.
- Thuật toán Học máy không giám sát phát hiện điểm bất thường Isolation Forest (iForest).
- Các kịch bản tấn công lạm dụng logic nghiệp vụ tệp tin và lỗ hổng phân quyền cấp đối tượng (BOLA / IDOR, Export Abuse, Delete Abuse).

## 7. Phạm vi
### Có làm:
- Xây dựng ứng dụng Web Flask StudyDrive đầy đủ giao diện Jinja2/Bootstrap, kết nối CSDL MySQL/SQLite.
- Triển khai cơ chế Authentication (Đăng ký, Đăng nhập, Session cookie, CSRF Protection) và Authorization (Phân quyền cấp đối tượng OWNER/VIEWER cho từng tệp tin).
- Xây dựng Flask Middleware thu thập Structured Request Logging lưu vào bảng `request_logs`.
- Viết 4 script giả lập dữ liệu: `simulate_normal.py`, `simulate_export_abuse.py`, `simulate_delete_abuse.py`, `simulate_bola_scan.py`.
- Gom nhóm log theo cửa sổ 5 phút, trích xuất bộ đặc trưng hành vi 25 chiều (với 11 đặc trưng toán học cốt lõi).
- Thực hiện phân chia dữ liệu Train (Normal-only), Validation (Normal + Anomaly), Test (Normal + Anomaly) theo nhóm Session/Run để chống rò rỉ dữ liệu.
- Huấn luyện mô hình Isolation Forest trên dữ liệu bình thường, tuning tham số qua Grid Search trên tập Validation.
- Đánh giá hiệu năng định lượng (Accuracy, Precision, Recall, F1-Score, False Positive Rate, Confusion Matrix).
- Tích hợp tính năng Detection vào giao diện Admin (`/admin/logs`, `/alerts`, `/alerts/<id>`).
- Xây dựng bộ test tự động Pytest (38 test cases) kiểm tra Auth, Documents, Logging, ML pipeline, Alert Dashboard.

### Không làm:
- Không thực hiện phát hiện các cuộc tấn công tầng mạng/giao thức (như DDoS, SYN Flood, Port Scan, ICMP Flood) hay các lỗ hổng Injection ở mức WAF (SQLi, XSS payload filtering).
- Không hỗ trợ tính năng chia sẻ nguyên thư mục (Folder Sharing) trong phiên bản hiện tại (chỉ hỗ trợ chia sẻ từng tệp tin lẻ).
- Không xây dựng kiến trúc Real-time Event Streaming (như Apache Kafka, Apache Flink, Celery stream worker); tiến trình phát hiện hoạt động theo cơ chế Batch Processing (chạy định kỳ hoặc kích hoạt thủ công theo cửa sổ 5 phút).
- Không tự động thực hiện phản ứng tự động chặn người dùng ngay lập tức (Auto-blocking IP/User) khi phát hiện cảnh báo (hệ thống dừng lại ở mức phát cảnh báo cho Admin thẩm định).

## 8. Các hành vi bất thường
- **Scenario 1: Export Abuse (Lạm dụng tính năng xuất dữ liệu hàng loạt)**
  - *Mô tả:* Người dùng thực hiện dồn dập các yêu cầu đóng gói tệp ZIP hoặc xuất dữ liệu CSV với số lượng tệp tin lớn trong một khoảng thời gian ngắn (ví dụ: xuất 30-50 tệp tin trong 5 phút).
  - *Đặc trưng nhận diện:* `export_count` cao, `export_ratio` gần bằng 1.0, khoảng cách giữa các request (`avg_inter_request_sec`) rất ngắn.
  - *Hậu quả:* Nguy cơ thất thoát dữ liệu quy mô lớn (Data Exfiltration) hoặc gây cạn kiệt tài nguyên CPU/RAM/Disk của server.
- **Scenario 2: Delete Abuse (Lạm dụng tính năng xóa tệp tin / Phá hoại dữ liệu)**
  - *Mô tả:* Người dùng thực hiện xóa mềm (soft-delete) dồn dập hàng loạt tệp tin thuộc nhiều thư mục khác nhau trong một khoảng thời gian ngắn (ví dụ: xóa 30 tệp tin trong 5 phút).
  - *Đặc trưng nhận diện:* `delete_count` cao, `delete_ratio` cao, `unique_deleted_resource_count` lớn.
  - *Hậu quả:* Tài khoản người dùng bị chiếm đoạt (Account Takeover) hoặc kẻ phá hoại cố tinh xóa sạch dữ liệu cá nhân/tổ chức.
- **Scenario 3: IDOR / BOLA Scan (Rà quét lỗ hổng Broken Object Level Authorization)**
  - *Mô tả:* Kẻ tấn công thay đổi liên tục tham số `resource_id` trên URI/API (ví dụ `/documents/file/101`, `/102`, `/103`...) nhằm tự động dò quét và tìm kiếm các tệp tin thuộc sở hữu của người dùng khác.
  - *Đặc trưng nhận diện:* `unique_resource_id_count` tăng đột biến, `forbidden_count` (lỗi 403) và `not_found_count` (lỗi 404) chiếm tỷ lệ rất cao (`forbidden_rate`, `not_found_rate`), `unique_failed_resource_id_count` lớn.
  - *Hậu quả:* Lộ dò tài nguyên hệ thống, thu thập trái phép thông tin nhạy cảm của người dùng khác.

## 9. Machine Learning
- **Model:** Thuật toán **Isolation Forest (iForest)** (sử dụng thư viện `scikit-learn`).
- **Loại ML:** **Học không giám sát (Unsupervised Learning / Anomaly Detection)** — Huấn luyện mô hình chủ yếu trên tập dữ liệu chứa các cửa sổ hành vi bình thường (Normal-only Train set).
- **Input features:** Vector đặc trưng được trích xuất từ cửa sổ log 5 phút. Bộ 11 đặc trưng toán học cốt lõi (thuộc bộ 25 đặc trưng toàn diện trong pipeline `build_features.py`):
  1. `request_count`: Tổng số request trong cửa sổ 5 phút.
  2. `unique_endpoint_count`: Số lượng endpoint duy nhất truy cập.
  3. `avg_inter_request_sec`: Khoảng thời gian trung bình giữa 2 request liên tiếp (s).
  4. `error_rate`: Tỷ lệ request gặp lỗi HTTP (>= 400).
  5. `export_count`: Số lượng thao tác xuất dữ liệu (export).
  6. `delete_count`: Số lượng thao tác xóa tệp (delete).
  7. `unique_deleted_resource_count`: Số tài nguyên độc lập bị xóa.
  8. `unique_resource_id_count`: Tổng số `resource_id` độc lập bị tác động.
  9. `forbidden_rate`: Tỷ lệ lỗi 403 Forbidden (truy cập trái quyền).
  10. `not_found_rate`: Tỷ lệ lỗi 404 Not Found (truy cập tài nguyên không tồn tại).
  11. `unique_failed_resource_id_count`: Số tài nguyên độc lập bị truy cập thất bại (lỗi 403 hoặc 404).
  *(Cùng các đặc trưng mở rộng: `burst_rate`, `sensitive_ratio`, `resource_id_change_rate`, `max_sensitive_streak`...)*
- **Output:**
  - Điểm bất thường (`anomaly_score` trong khoảng [0, 1]).
  - Nhãn nhị phân: `0` (Normal) hoặc `1` (Anomaly) dựa trên so sánh score với `threshold` phân vị (percentile 90.0% / 95.0%).
  - Gợi ý kịch bản bất thường (`scenario_hint`: Export Abuse / Delete Abuse / BOLA Scan).
- **Cách đánh giá:** Đánh giá định lượng trên tập kiểm thử độc lập (Test Set) bằng các chỉ số:
  - **Accuracy (Độ chính xác tổng thể)**
  - **Precision (Độ xác thực cảnh báo)**
  - **Recall (Độ gợi nhớ kịch bản tấn công)**
  - **F1-Score (Trung bình hài hòa)**
  - **False Positive Rate (Tỷ lệ báo động giả - FPR)**
  - **Ma trận Nhầm lẫn (Confusion Matrix: TN, FP, FN, TP)**
- **Có model nào khác được thử không:** Có phân tích lý thuyết đối chứng và so sánh ưu/nhược điểm với 3 thuật toán phổ biến khác (One-Class SVM, Local Outlier Factor, Autoencoder), khẳng định Isolation Forest là lựa chọn tối ưu nhất cho web request log nhờ độ phức tạp $O(n \log n)$, bộ nhớ thấp $O(n)$ và không phụ thuộc giả định phân bố dữ liệu.

## 10. Phương pháp thực hiện
1. **Nghiên cứu cơ sở lý thuyết:** Phân tích các tiêu chuẩn an toàn web OWASP (Broken Access Control, BOLA/IDOR), tổng quan các kỹ thuật phát hiện bất thường và toán học thuật toán Isolation Forest.
2. **Xây dựng ứng dụng Web StudyDrive:** Lập trình Backend Flask, mô hình CSDL SQLAlchemy, phân quyền OWNER/VIEWER, giao diện HTML/Jinja2/Bootstrap.
3. **Phát triển phân hệ Structured Request Logging:** Xây dựng Flask Middleware `request_logging.py` đo đạc thời gian, giải mã context và ghi log bất đồng bộ vào bảng `request_logs` (băm SHA-256 session ID).
4. **Giả lập dữ liệu log (Data Generation):** Viết 4 script simulator đóng gói các luồng request đại diện cho người dùng bình thường và 3 kịch bản tấn công.
5. **Gom nhóm & Trích xuất đặc trưng (Feature Engineering):** Xây dựng module `ml/build_features.py` gom log thành các cửa sổ 5 phút theo `(user_id, session_id_hash)` và tính toán vector 25D.
6. **Phân chia tập dữ liệu chống rò rỉ (Group-aware Split):** Chia toàn bộ cửa sổ thành Train set (60% Normal), Validation set (20% N+A), Test set (20% N+A) dựa trên nhận diện `run_id` và `session_id_hash`.
7. **Huấn luyện & Tinh chỉnh Siêu tham số (Grid Search):** Huấn luyện Isolation Forest trên Train set, thực hiện Grid Search tìm cấu hình `n_estimators`, `max_samples`, `threshold_percentile` tối ưu trên Validation set.
8. **Tích hợp Web & Đánh giá Độc lập:** Đánh giá mô hình trên Test set, đóng gói mô hình (`model.joblib`), xây dựng dịch vụ `detection_service.py` phục vụ giao diện Admin Alerts Dashboard.
9. **Kiểm thử tự động:** Viết bộ 38 test cases với `pytest` kiểm tra tính đúng đắn toàn hệ thống.

## 11. Công nghệ
- **Ngôn ngữ lập trình:** Python 3.11+
- **Web Framework:** Flask 3.x, Werkzeug, Jinja2, Bootstrap 5
- **ORM & CSDL:** Flask-SQLAlchemy, MySQL / PyMySQL (Production), SQLite (Dev/Test local)
- **Xử lý dữ liệu & ML:** Pandas, NumPy, Scikit-Learn (`sklearn.ensemble.IsolationForest`), Joblib
- **Kiểm thử & Automation:** Pytest, Pytest-Flask, Requests
- **Môi trường & Công cụ:** PowerShell, Virtual environment (`.venv`), Git

## 12. Kết quả đã đạt được
- **Về mặt ứng dụng web:** Xây dựng hoàn chỉnh ứng dụng StudyDrive hoạt động mượt mà, giao diện trực quan, quản lý tệp/thư mục an toàn, chia sẻ phân quyền OWNER/VIEWER chuẩn xác, hỗ trợ thùng rác và xuất dữ liệu.
- **Về mặt Logging & Security:** Middleware ghi log tự động 100% request tầng ứng dụng, ghi nhận đầy đủ context (user, action, status, response time) mà không gây trễ request chính và tuân thủ quy tắc bảo mật PII (băm SHA-256 session ID).
- **Về mặt Dữ liệu & ML Pipeline:** Sinh thành công bộ dữ liệu hơn 5.500 dòng log thô có ground truth; xây dựng thành công pipeline gom nhóm cửa sổ 5 phút, trích xuất 25 đặc trưng và chia tập Train/Val/Test chống rò rỉ dữ liệu.
- **Về mặt Mô hình & Đánh giá:** Huấn luyện thành công Isolation Forest, tinh chỉnh siêu tham số bằng Grid Search. Đạt kết quả đánh giá thực nghiệm định lượng trên tập Test: **Accuracy = 66.67%**, **Precision = 66.67%**, **Recall = 66.67%**, **F1-Score = 66.67%** (phát hiện 100% kịch bản *Export Abuse* trên tập test).
- **Về mặt Tích hợp & Kiểm thử:** Tích hợp thành công tiến trình Detection vào trang Admin Alerts Dashboard; xây dựng bộ 38 bài test tự động (Pytest) chạy thành công 100% (`38 passed`).

## 13. Hạn chế hiện tại
- **Kích thước dữ liệu kiểm thử thực tế:** Số lượng mẫu trong tập dữ liệu test còn hạn chế (do thu thập trên môi trường giả lập local).
- **Cơ chế phát hiện Batch Processing:** Tiến trình phát hiện hoạt động theo lô 5 phút (Batch/Trigger), chưa đạt tốc độ phát hiện thời gian thực từng giây (Real-time Event Streaming).
- **Tỷ lệ báo động giả (False Positive Rate):** Mô hình vẫn ghi nhận một tỷ lệ báo động giả (~33% trên tập test mẫu nhỏ) đối với một số chuỗi hành vi của người dùng bình thường có tốc độ thao tác nhanh.
- **Phản ứng tự động (Active Response):** Hệ thống chưa tích hợp cơ chế tự động khóa tài khoản hoặc chặn IP ngay lập tức khi tạo Alert (Admin vẫn phải rà soát và quyết định thủ công).

## 14. Yêu cầu của giảng viên
- **Ứng dụng web thực tế:** Hệ thống phải có ứng dụng web hoàn chỉnh chạy được để người dùng thao tác thật, không chỉ làm mô hình ML rời rạc trên file CSV có sẵn.
- **Logging tự động tầng Middleware:** Việc ghi vết log phải được thực hiện tự động bằng Middleware tầng ứng dụng, không chấp nhận việc chèn code ghi log thủ công vào từng hàm controller/route.
- **Bảo mật dữ liệu Log:** Tuyệt đối không lưu mật khẩu, CSRF token hay session ID nguyên bản (plaintext) trong bảng log.
- **Chuẩn hóa phát biểu Bài toán ML:** Phải phát biểu bài toán Machine Learning chuẩn xác theo khung T-P-E (Task - Performance - Experience) của Tom Mitchell.
- **Minh bạch Pipeline & Chống rò rỉ dữ liệu:** Phải trình bày rõ công thức toán học của các đặc trưng (Feature Engineering) và có cơ chế phân chia tập Train/Val/Test chống rò rỉ dữ liệu (Anti Data Leakage).
- **Tích hợp hai chiều (Closed-Loop Integration):** Mô hình ML sau khi huấn luyện phải được tích hợp ngược trở lại giao diện Web Admin để Admin kích hoạt Detection và xem cảnh báo kèm khả năng truy ngược về request log thô.
- **Kiểm thử tự động:** Phải có bộ công cụ kiểm thử (Test Suite) tự động chứng minh tính đúng đắn của các phân hệ web và ML.

## 15. Tài liệu/mẫu tham khảo
- [docs/01_project_requirements.md](file:///d:/web-anomaly-detection/docs/01_project_requirements.md) - Yêu cầu & Phạm vi dự án StudyDrive
- [docs/02_architecture_and_design.md](file:///d:/web-anomaly-detection/docs/02_architecture_and_design.md) - Kiến trúc & Thiết kế hệ thống StudyDrive
- [docs/03_data_and_ml.md](file:///d:/web-anomaly-detection/docs/03_data_and_ml.md) - Dữ liệu & Học máy (Isolation Forest)
- [docs/04_security_guide.md](file:///d:/web-anomaly-detection/docs/04_security_guide.md) - Hướng dẫn Bảo mật & Phòng chống BOLA/IDOR
- [docs/05_development_history.md](file:///d:/web-anomaly-detection/docs/05_development_history.md) - Lịch sử phát triển & Hướng dẫn demo
- [md/baocao_thong_tin.md](file:///d:/web-anomaly-detection/md/baocao_thong_tin.md) - Báo cáo chi tiết tổng quan đồ án
- [md/HIEU_HE_THONG.md](file:///d:/web-anomaly-detection/md/HIEU_HE_THONG.md) - Hướng dẫn giải thích hệ thống chi tiết
- [Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation Forest. IEEE ICDM](https://doi.org/10.1109/ICDM.2008.17)
- [OWASP Top 10:2021 - Broken Access Control & Insecure Design](https://owasp.org/Top10/)
