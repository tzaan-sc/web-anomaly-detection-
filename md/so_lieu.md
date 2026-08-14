# XÂY DỰNG HỆ THỐNG PHÁT HIỆN HÀNH VI TRUY CẬP BẤT THƯỜNG TRÊN ỨNG DỤNG WEB BẰNG MACHINE LEARNING

---

## CHƯƠNG 1: TỔNG QUAN

### 1.1. Lý do chọn đề tài
Trong quá trình chuyển đổi số, các ứng dụng web lưu trữ và chia sẻ tài liệu trực tuyến đóng vai trò then chốt trong hoạt động hàng ngày. Người dùng thường xuyên thực hiện các thao tác như tải lên, tải xuống, chia sẻ và xuất dữ liệu thông qua các HTTP Request. Tuy nhiên, các nguy cơ bảo mật ở tầng ứng dụng (Application Layer), đặc biệt là **Lạm dụng logic nghiệp vụ (Business Logic Abuse)** và **Kiểm soát truy cập cấp đối tượng bị phá vỡ (BOLA/IDOR)**, đang trở thành mối đe dọa nghiêm trọng.

Các cuộc tấn công logic này không chứa mã độc cú pháp mà sử dụng chính các HTTP Request hợp lệ từ tài khoản người dùng bình thường. Vì vậy, các hệ thống WAF và IDS truyền thống dựa trên chữ ký tĩnh gần như hoàn toàn bất lực. Đề tài được thực hiện nhằm ứng dụng thuật toán học máy không giám sát **Isolation Forest** để phân tích chuỗi nhật ký truy cập (request log) thu thập tự động từ tầng Flask Middleware của ứng dụng StudyDrive, gom nhóm theo cửa sổ 5 phút và trích xuất **vector 25 đặc trưng số** nhằm phát hiện sớm các hành vi bất thường.

### 1.2. Mục tiêu nghiên cứu
- Xây dựng ứng dụng web StudyDrive đầy đủ các chức năng quản lý tệp, chia sẻ và phân quyền (`OWNER`, `VIEWER`).
- Tích hợp Middleware ghi log tự động 21 trường dữ liệu có cấu trúc tại tầng ứng dụng (`after_request`), băm SHA-256 đối với Session ID.
- Xây dựng bộ giả lập 4 kịch bản tương tác người dùng: Normal, Export Abuse, Delete Abuse và BOLA Scan.
- Thiết kế quy trình trích xuất vector 25 đặc trưng số từ các cửa sổ trượt 5 phút.
- Huấn luyện mô hình Isolation Forest theo chiến lược Normal-only Training và áp dụng Group-aware Split để chống rò rỉ dữ liệu.
- Đánh giá định lượng hiệu năng mô hình qua các chỉ số Accuracy, Precision, Recall, F1-Score, FPR và Confusion Matrix.
- Tích hợp dịch vụ Detection, Alerts Dashboard và cơ chế phòng thủ chủ động Active Defense tự động khóa tạm thời tài khoản vi phạm.
- Hoàn thành bộ kiểm thử tự động toàn diện với 44 test cases.

### 1.3. Đối tượng & Phạm vi nghiên cứu
- **Đối tượng:** Bản ghi HTTP Request Log tại tầng ứng dụng Flask, chuỗi hành vi người dùng trong cửa sổ 5 phút, mô hình Isolation Forest.
- **Phạm vi kịch bản:** Tập trung vào 3 kịch bản:
  1. *Export Abuse:* Gửi liên tiếp 30–50 request xuất dữ liệu trong 5 phút.
  2. *Delete Abuse:* Gửi liên tiếp 20–40 request xóa tệp hàng loạt trong 5 phút.
  3. *IDOR/BOLA Scan:* Gửi từ 100–500 request dò quét `file_id` không thuộc quyền sở hữu, gây lỗi 403 và 404 liên tiếp.
- **Phạm vi kỹ thuật:** Kiến trúc Flask 3.x, MySQL, Batch Processing Detection định kỳ và Active Defense.

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

### 2.1. Logging tầng ứng dụng & An toàn dữ liệu
Khác với log của Web Server (như Nginx hay Apache) chỉ ghi nhận URL và IP, nhật ký tầng ứng dụng (Application-level Logging) ghi lại ngữ cảnh nghiệp vụ phong phú: `user_id`, `role`, `action`, `resource_id`, `ownership_result`, `authorization_result`. Để đảm bảo an toàn thông tin, các trường nhạy cảm như mật khẩu và mã CSRF bị loại bỏ hoàn toàn, còn `session_id` được băm bằng thuật toán SHA-256.

### 2.2. Thuật toán Isolation Forest
Isolation Forest hoạt động dựa trên nguyên tắc cô lập các điểm dị biệt bằng cách chia cắt không gian dữ liệu ngẫu nhiên. Điểm bất thường bị cô lập ở độ sâu nông của cây (độ dài đường đi $h(x)$ ngắn), trong khi điểm bình thường cần nhiều phép phân chia hơn.

Công thức độ dài đường đi chuẩn hóa $c(n)$:
$$c(n) = 2 \left( \ln(n - 1) + 0.5772156649 \right) - \frac{2(n - 1)}{n}$$

Điểm bất thường (Anomaly Score) $s(x, n)$:
$$s(x, n) = 2^{-\frac{\mathbb{E}[h(x)]}{c(n)}}$$

Ngưỡng cảnh báo được chọn tại phân vị thứ 95 (Percentile 95.0%) trên tập huấn luyện hành vi bình thường.

### 2.3. Hiện tượng Rò rỉ Dữ liệu (Data Leakage) & Kỹ thuật Group-aware Split
Trong dữ liệu dạng chuỗi thời gian của ứng dụng web, các bản ghi thuộc cùng một phiên làm việc có sự phụ thuộc lẫn nhau. Nếu chia ngẫu nhiên từng dòng log, các phần của cùng một cuộc tấn công sẽ bị rải rác vào cả tập Train và Test. Kỹ thuật **Group-aware Split** gom nhóm theo cặp `user_id|session_id_hash` và `run_id`, đảm bảo tính độc lập hoàn toàn giữa các tập.

---

## CHƯƠNG 3: THU THẬP DỮ LIỆU & XÂY DỰNG ĐẶC TRƯNG

### 3.1. Dữ liệu Request Log Thô
Tập dữ liệu thô gồm 10.875 bản ghi có cấu trúc đầy đủ 21 trường: `request_id`, `timestamp`, `user_id`, `is_authenticated`, `role`, `session_id_hash`, `http_method`, `endpoint`, `path`, `action`, `action_type`, `is_sensitive`, `resource_type`, `resource_id`, `ownership_result`, `authorization_result`, `status_code`, `response_time_ms`, `ip_address`, `user_agent`.

### 3.2. Không gian 25 Đặc trưng Số
Dữ liệu được gom nhóm theo cửa sổ trượt 5 phút và trích xuất thành 25 đặc trưng số:
1. `request_count`: Tổng số request trong cửa sổ 5 phút.
2. `unique_endpoint_count`: Số endpoint duy nhất.
3. `unique_method_count`: Số phương thức HTTP duy nhất.
4. `session_duration_sec`: Thời lượng phiên hoạt động.
5. `avg_inter_request_sec`: Khoảng cách thời gian trung bình giữa 2 request.
6. `min_inter_request_sec`: Khoảng cách ngắn nhất giữa 2 request.
7. `burst_rate`: Tỷ lệ bùng nổ request theo thời gian.
8. `error_rate`: Tỷ lệ mã lỗi HTTP >= 400.
9. `forbidden_count`: Số lần lỗi 403 Forbidden.
10. `forbidden_rate`: Tỷ lệ lỗi 403.
11. `not_found_count`: Số lần lỗi 404 Not Found.
12. `not_found_rate`: Tỷ lệ lỗi 404.
13. `unique_failed_resource_id_count`: Số ID tài nguyên bị từ chối truy cập.
14. `export_count`: Số lần thực hiện xuất dữ liệu.
15. `export_ratio`: Tỷ lệ thao tác xuất dữ liệu.
16. `delete_count`: Số lần thực hiện xóa tài nguyên.
17. `delete_ratio`: Tỷ lệ thao tác xóa tài nguyên.
18. `unique_deleted_resource_count`: Số tài nguyên khác nhau bị xóa.
19. `unique_resource_id_count`: Số ID tài nguyên khác nhau được truy cập.
20. `resource_id_request_ratio`: Tỷ lệ request tương tác với tài nguyên.
21. `resource_id_change_rate`: Tần suất chuyển đổi ID tài nguyên.
22. `sensitive_request_count`: Số request nhạy cảm.
23. `sensitive_ratio`: Tỷ lệ request nhạy cảm.
24. `max_sensitive_streak`: Chuỗi thao tác nhạy cảm liên tiếp dài nhất.
25. `avg_response_time_ms`: Thời gian phản hồi trung bình của hệ thống.

---

## CHƯƠNG 4: HUẤN LUYỆN MÔ HÌNH & ĐÁNH GIÁ KẾT QUẢ

### 4.1. Phân chia Tập dữ liệu & Tối ưu Siêu tham số
- **Train Set:** 8 cửa sổ (100% Normal).
- **Validation Set:** 6 cửa sổ (3 Normal, 3 Anomaly).
- **Test Set:** 5 cửa sổ độc lập (2 Normal, 3 Anomaly).
- **Siêu tham số tối ưu:** $n_{\text{estimators}} = 100$, $\text{max\_samples} = \text{'auto'}$, $\text{threshold} = \text{Percentile 95.0\%}$.

### 4.2. Kết quả Đánh giá Thực nghiệm
- **Accuracy:** 100.0%
- **Precision:** 100.0%
- **Recall:** 100.0%
- **F1-Score:** 1.000
- **False Positive Rate:** 0.0%

Mô hình phân định rõ ràng giữa hành vi người dùng bình thường và các kịch bản tấn công:
- **Export Abuse:** Điểm bất thường $s = 0.684$ (vượt ngưỡng $\tau = 0.512$).
- **Delete Abuse:** Điểm bất thường $s = 0.662$.
- **BOLA Scan:** Điểm bất thường $s = 0.718$.

---

## CHƯƠNG 5: TRIỂN KHAI HỆ THỐNG & KIẾN TRÚC TÍCH HỢP

### 5.1. Thiết kế Hệ thống & Cơ sở Dữ liệu
Hệ thống gồm 5 phân hệ Blueprints (`auth`, `documents`, `admin`, `alerts`, `main`) và 7 bảng CSDL MySQL (`users`, `folders`, `stored_files`, `file_shares`, `export_jobs`, `request_logs`, `alerts`).

### 5.2. Bảng điều khiển Cảnh báo & Phòng thủ Chủ động (Active Defense)
- **Alerts Dashboard:** Cho phép quản trị viên xem danh sách cảnh báo, phân tích Top 3 đặc trưng và truy ngược trực tiếp về các request log thô trong cửa sổ 5 phút.
- **Active Defense:** Tự động khóa tạm thời tài khoản vi phạm trong 60 phút khi phát hiện bất thường, ngăn chặn kịp thời các hành vi phá hoại tiếp diễn.
- **Kiểm thử tự động:** Hoàn thành **44 / 44 test cases (100% Passed)** với Pytest.

---

## CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 6.1. Kết luận
Đề tài đã hoàn thành xuất sắc toàn bộ các mục tiêu đặt ra: Xây dựng ứng dụng web StudyDrive hoàn chỉnh, tích hợp hệ thống ghi nhật ký có cấu trúc không gây suy giảm hiệu năng, thiết kế không gian 25 đặc trưng số, huấn luyện mô hình Isolation Forest đạt độ chính xác 100% trên các kịch bản thực nghiệm, tích hợp bảng điều khiển cảnh báo và cơ chế phòng thủ chủ động.

### 6.2. Hướng phát triển
- Triển khai xử lý luồng thời gian thực (Real-time Streaming) với Apache Kafka.
- Bổ sung các thuật toán học sâu (Autoencoders / LSTM) để phân tích chuỗi hành vi phức tạp dài hạn.

---

## TÀI LIỆU THAM KHẢO

1. F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation Forest," in *Proceedings of the 2008 Eighth IEEE International Conference on Data Mining*, 2008, pp. 413–422.
2. OWASP Foundation, "OWASP API Security Top 10 - 2023," *OWASP Project*, 2023.
3. T. M. Mitchell, *Machine Learning*, McGraw-Hill, 1997.
4. P. Pedregosa *et al.*, "Scikit-learn: Machine learning in Python," *JMLR*, vol. 12, pp. 2825–2830, 2011.
5. M. Grinberg, *Flask Web Development*, 2nd ed. O'Reilly Media, 2018.
