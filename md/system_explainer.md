# CẨM NANG BẢO VỆ ĐỒ ÁN — GIẢI THÍCH TOÀN BỘ HỆ THỐNG
## ĐỀ TÀI: XÂY DỰNG HỆ THỐNG PHÁT HIỆN HÀNH VI TRUY CẬP BẤT THƯỜNG TRÊN ỨNG DỤNG WEB BẰNG MACHINE LEARNING

> **Tài liệu chuẩn bị bảo vệ đồ án:** Được thiết kế theo dạng hỏi - đáp trực diện, phân tích sâu từng luồng kỹ thuật, bám sát 100% mã nguồn thực tế của dự án StudyDrive.

---

## PHẦN 1: KỊCH BẢN ĐỐI ĐÁP NHANH VỚI HỘI ĐỒNG CHẤM

### Kịch bản 1: Thầy/Cô hỏi "Em đã hoàn thành đồ án đến đâu rồi?"
> **Câu trả lời chuẩn:**  
> *"Dạ thưa Thầy/Cô, em đã hoàn thành 100% toàn bộ các hạng mục của đồ án. Phần ứng dụng web StudyDrive (Flask, MySQL) đã hoàn thiện đầy đủ các chức năng quản lý tệp, chia sẻ phân quyền OWNER/VIEWER, xóa mềm, thùng rác và trang quản trị. Phần Machine Learning với thuật toán Isolation Forest (25 đặc trưng số) đã được huấn luyện, tinh chỉnh siêu tham số và đánh giá nghiêm ngặt theo phương pháp Group-aware Split để chống rò rỉ dữ liệu. Các cảnh báo phát hiện bất thường (Export Abuse, Delete Abuse, BOLA Scan) đã được tích hợp hiển thị trực quan trên Alerts Dashboard kèm cơ chế phòng thủ chủ động Active Defense tự động khóa tạm thời tài khoản vi phạm. Toàn bộ hệ thống đã vượt qua 44 bài kiểm thử tự động với tỷ lệ đạt 100%."*

---

### Kịch bản 2: Thầy/Cô hỏi "Em hãy trình bày luồng hoạt động tổng thể của hệ thống?"
> **Câu trả lời chuẩn:**  
> *"Dạ, hệ thống hoạt động khép kín qua 5 bước chính:*  
> 1. *Người dùng tương tác trên ứng dụng web StudyDrive (tải tệp, xóa, chia sẻ, xuất dữ liệu).*  
> 2. *Tầng Flask Middleware (`request_logging.py`) tự động ghi nhận từng HTTP Request với 21 trường dữ liệu có cấu trúc vào bảng `request_logs` trong MySQL, trong đó Session ID được băm SHA-256 để bảo vệ tính riêng tư.*  
> 3. *Pipeline Machine Learning định kỳ quét dữ liệu log, gom nhóm theo cửa sổ trượt 5 phút theo từng người dùng/phiên, trích xuất vector 25 đặc trưng số.*  
> 4. *Mô hình Isolation Forest (huấn luyện Normal-only) tính toán Anomaly Score. Nếu điểm số vượt ngưỡng Percentile 95%, hệ thống xác định đây là hành vi bất thường.*  
> 5. *Hệ thống tự động ghi nhận cảnh báo vào bảng `alerts`, kích hoạt cơ chế Active Defense khóa tạm thời tài khoản 60 phút và hiển thị chi tiết trên Alerts Dashboard để quản trị viên truy ngược về các log gốc."*

---

### Kịch bản 3: Thầy/Cô hỏi "Tại sao dùng Isolation Forest mà không dùng các thuật toán học có giám sát?"
> **Câu trả lời chuẩn:**  
> *"Dạ thưa Thầy/Cô, trong thực tế an toàn thông tin, các cuộc tấn công lạm dụng nghiệp vụ diễn ra rất đa dạng và dữ liệu tấn công có nhãn luôn cực kỳ khan hiếm. Nếu dùng học có giám sát (như Random Forest, SVM), mô hình sẽ phụ thuộc vào các nhãn đã biết và không thể phát hiện các kiểu tấn công mới (Zero-day). Isolation Forest là mô hình học không giám sát, chỉ cần học phân bố của hành vi bình thường để phát hiện các điểm dị biệt (outliers). Ngoài ra, iForest có độ phức tạp tính toán tuyến tính $O(n \cdot t)$, chạy rất nhẹ và cho tốc độ suy luận dưới 1ms mỗi cửa sổ, rất phù hợp triển khai tích hợp trên web."*

---

### Kịch bản 4: Thầy/Cô hỏi "Làm thế nào hệ thống phát hiện được lỗ hổng BOLA/IDOR?"
> **Câu trả lời chuẩn:**  
> *"Dạ, BOLA (Broken Object Level Authorization) hay IDOR là hành vi kẻ tấn công thay đổi liên tiếp tham số `file_id` trên URI để dò quét tệp tin của người khác. Hệ thống phát hiện hành vi này thông qua sự kết hợp của các đặc trưng trong cửa sổ 5 phút: `forbidden_count` (lỗi 403) và `not_found_count` (lỗi 404) tăng đột biến, `unique_failed_resource_id_count` lớn và `resource_id_change_rate` cao vượt trội so với người dùng bình thường."*

---

### Kịch bản 5: Thầy/Cô hỏi "Hiện tượng rò rỉ dữ liệu (Data Leakage) trong bài toán này là gì và em đã xử lý thế nào?"
> **Câu trả lời chuẩn:**  
> *"Dạ, dữ liệu log truy cập có tính phụ thuộc chuỗi thời gian theo phiên làm việc. Nếu chia ngẫu nhiên từng dòng log vào tập Train và Test, các request thuộc cùng một phiên tấn công sẽ bị rải rác ở cả hai tập, khiến mô hình 'học thuộc' và cho kết quả đánh giá bị lạc quan ảo. Để giải quyết, em áp dụng kỹ thuật **Group-aware Split**: gom nhóm toàn bộ các cửa sổ theo cặp `user_id|session_id_hash` và `run_id`, tập Train chỉ chứa 100% các phiên bình thường (Normal-only), còn tập Test chứa các phiên người dùng và kịch bản tấn công hoàn toàn độc lập."*

---

## PHẦN 2: BẢNG TỔNG HỢP 25 ĐẶC TRƯNG HÀNH VI

| STT | Tên đặc trưng | Nhóm đặc trưng | Mục đích phát hiện bất thường |
|---|---|---|---|
| 1 | `request_count` | Lưu lượng & Tần suất | Phát hiện các hành vi gửi request dồn dập, tự động hóa bằng script. |
| 2 | `unique_endpoint_count` | Lưu lượng & Tần suất | Đo lường mức độ đa dạng của các route được gọi. |
| 3 | `unique_method_count` | Lưu lượng & Tần suất | Đo lường sự đa dạng của các phương thức HTTP (GET, POST,...). |
| 4 | `session_duration_sec` | Lưu lượng & Tần suất | Thời lượng phiên hoạt động trong cửa sổ 5 phút. |
| 5 | `avg_inter_request_sec` | Lưu lượng & Tần suất | Khoảng cách thời gian trung bình giữa 2 request liên tiếp. |
| 6 | `min_inter_request_sec` | Lưu lượng & Tần suất | Khoảng cách ngắn nhất giữa 2 request (giá trị < 0.05s là dấu hiệu rõ ràng của bot). |
| 7 | `burst_rate` | Lưu lượng & Tần suất | Tốc độ bùng nổ: Tỷ lệ số request chia cho thời lượng phiên. |
| 8 | `error_rate` | Lỗi & Phân quyền | Tỷ lệ các request gặp lỗi HTTP (mã phản hồi >= 400). |
| 9 | `forbidden_count` | Lỗi & Phân quyền | Số lần bị chặn với mã lỗi 403 Forbidden (truy cập trái phép). |
| 10 | `forbidden_rate` | Lỗi & Phân quyền | Tỷ lệ lỗi 403 trên tổng số request trong cửa sổ. |
| 11 | `not_found_count` | Lỗi & Phân quyền | Số lần gặp lỗi 404 Not Found do đoán sai ID tệp tin. |
| 12 | `not_found_rate` | Lỗi & Phân quyền | Tỷ lệ lỗi 404 trên tổng số request trong cửa sổ. |
| 13 | `unique_failed_resource_id_count` | Lỗi & Phân quyền | Số lượng ID tài nguyên khác nhau bị từ chối truy cập (dấu hiệu BOLA Scan). |
| 14 | `export_count` | Lạm dụng Nghiệp vụ | Số lần thực hiện hành động xuất/tải dữ liệu (Export Abuse). |
| 15 | `export_ratio` | Lạm dụng Nghiệp vụ | Tỷ lệ thao tác xuất dữ liệu trên tổng request. |
| 16 | `delete_count` | Lạm dụng Nghiệp vụ | Số lần thực hiện hành động xóa tài nguyên (Delete Abuse). |
| 17 | `delete_ratio` | Lạm dụng Nghiệp vụ | Tỷ lệ thao tác xóa tài nguyên trên tổng request. |
| 18 | `unique_deleted_resource_count` | Lạm dụng Nghiệp vụ | Số lượng tài nguyên khác nhau bị xóa (phát hiện hành vi xóa diện rộng). |
| 19 | `unique_resource_id_count` | Dò quét Tài nguyên | Số lượng ID tài nguyên khác nhau được truy cập trong cửa sổ. |
| 20 | `resource_id_request_ratio` | Dò quét Tài nguyên | Tỷ lệ các request có tương tác trực tiếp với mã định danh tài nguyên. |
| 21 | `resource_id_change_rate` | Dò quét Tài nguyên | Tần suất thay đổi liên tục giữa các ID tài nguyên (dấu hiệu dò quét tuần tự). |
| 22 | `sensitive_request_count` | Nhạy cảm & Hiệu năng | Số lượng các thao tác nhạy cảm (tải nhiều, xóa, thay đổi quyền). |
| 23 | `sensitive_ratio` | Nhạy cảm & Hiệu năng | Tỷ lệ thao tác nhạy cảm trên tổng số request. |
| 24 | `max_sensitive_streak` | Nhạy cảm & Hiệu năng | Chuỗi dài nhất các thao tác nhạy cảm được thực hiện liên tiếp. |
| 25 | `avg_response_time_ms` | Nhạy cảm & Hiệu năng | Thời gian phản hồi trung bình của máy chủ (phát hiện dấu hiệu làm cạn kiệt tài nguyên). |

---

## PHẦN 3: CÂU HỎI CHUYÊN SÂU CỦA HỘI ĐỒNG & CÁCH TRẢ LỜI ĐẠT ĐIỂM TỐI ĐA

### Q1: Công thức tính toán Anomaly Score trong Isolation Forest hoạt động như thế nào?
> **Trả lời:**  
> Điểm Anomaly Score được tính theo công thức:
> $$s(x, n) = 2^{-\frac{\mathbb{E}[h(x)]}{c(n)}}$$
> Trong đó $\mathbb{E}[h(x)]$ là độ sâu trung bình mà mẫu $x$ bị cô lập trên $t$ cây iTree, và $c(n)$ là độ dài đường đi trung bình của cây tìm kiếm nhị phân không thành công:
> $$c(n) = 2 \left( \ln(n - 1) + 0.5772156649 \right) - \frac{2(n - 1)}{n}$$
> - Nếu mẫu $x$ có $\mathbb{E}[h(x)] \to 0$ (bị cô lập rất nhanh ở gần gốc cây) $\implies s \to 1$ (Bất thường rõ rệt).
> - Nếu mẫu $x$ có $\mathbb{E}[h(x)] \to c(n)$ $\implies s \to 0.5$ (Không có tính dị biệt).
> - Nếu mẫu $x$ có $\mathbb{E}[h(x)] \to n - 1$ $\implies s \to 0$ (Hoàn toàn bình thường).

---

### Q2: Cơ chế Phòng thủ Chủ động (Active Defense) hoạt động ra sao khi phát hiện tấn công?
> **Trả lời:**  
> Khi module `detection_service.py` phát hiện một cửa sổ có $s(x) \ge \tau$ (ngưỡng Percentile 95%):
> 1. Lưu bản ghi vào bảng `alerts` kèm thông tin top đặc trưng và gợi ý kịch bản.
> 2. Cập nhật trường `is_locked = True` và `locked_until = datetime.utcnow() + timedelta(minutes=60)` của đối tượng `User` trong cơ sở dữ liệu.
> 3. Tầng Middleware `app/middleware/active_defense.py` kiểm tra ở mỗi request tiếp theo: nếu tài khoản đang bị khóa, lập tức hủy session, ngăn chặn truy cập và chuyển hướng người dùng đến trang thông báo bị khóa tạm thời.

---

### Q3: Em đã xây dựng những bài test nào để kiểm tra tính đúng đắn của hệ thống?
> **Trả lời:**  
> Hệ thống được kiểm thử tự động toàn diện bằng `pytest` với **44 bài test**, phân bổ qua các nhóm:
> - **Kiểm thử Xác thực & Đăng ký (`test_auth_register.py`):** Kiểm tra đăng ký thành công, bắt lỗi trùng email/username, kiểm tra băm mật khẩu.
> - **Kiểm thử Nghiệp vụ Tài liệu & Phân quyền (`test_documents.py`):** Kiểm tra tạo thư mục, upload file, phân quyền OWNER/VIEWER, soft delete, trash và ngăn chặn hành vi xóa trái phép tệp của người khác.
> - **Kiểm thử Logging tầng Middleware (`test_request_logging.py`):** Đảm bảo 100% request được ghi vết đầy đủ 21 trường, kiểm tra băm SHA-256 session và loại bỏ mật khẩu.
> - **Kiểm thử Tích hợp ML & Active Defense (`test_web_freeze.py`):** Kiểm tra luồng phát hiện bất thường và cơ chế khóa tài khoản tự động.
> - **Kiểm thử Quản trị viên (`test_admin_logs.py`):** Kiểm tra trang tra cứu và lọc nhật ký.
> Kết quả: Toàn bộ 44/44 bài test đều vượt qua (100% PASSED).
