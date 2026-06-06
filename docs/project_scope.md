# PROJECT SCOPE

## 1. Thông tin đề tài

**Tên đề tài:**
**Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning**

**Thời gian thực hiện:** 06/06/2026 – 19/07/2026

---

## 2. Mô tả vấn đề

Các cuộc tấn công web có dấu hiệu rõ ràng như gửi quá nhiều request trong thời gian ngắn thường có thể được phát hiện bằng rule-based, rate limiting, firewall hoặc WAF. Tuy nhiên, một số hành vi nguy hiểm không vượt qua các ngưỡng cố định nên khó phát hiện chỉ bằng luật. Ví dụ, một người dùng thường chỉ xem dữ liệu nhưng đột ngột thực hiện nhiều thao tác export hoặc delete trong một phiên đăng nhập. Kẻ tấn công cũng có thể thay đổi lần lượt các ID tài nguyên với tốc độ thấp để tránh cơ chế giới hạn request. Vì vậy, đề tài tập trung xây dựng hồ sơ hành vi bình thường của người dùng và sử dụng Machine Learning để nhận diện các hành vi lệch khỏi hồ sơ đó. Hệ thống sẽ sử dụng mô hình Isolation Forest để tính điểm bất thường và hỗ trợ phát hiện các hành vi có tính ngữ cảnh mà khó đặt một ngưỡng cố định.

---

## 3. Mục tiêu đề tài

Xây dựng một hệ thống web demo có khả năng:

1. Cho phép người dùng đăng nhập và sử dụng một số API cơ bản.
2. Thu thập log hành vi truy cập của người dùng.
3. Chuyển log thành các đặc trưng phục vụ Machine Learning.
4. Huấn luyện mô hình Isolation Forest trên dữ liệu hành vi bình thường.
5. Phát hiện các hành vi bất thường thuộc ba scenario đã xác định.
6. Hiển thị kết quả phát hiện gồm điểm bất thường, loại hành vi và thông tin request liên quan.
7. Đánh giá khả năng phát hiện của mô hình trên dữ liệu kiểm thử.

---

## 4. Sản phẩm cuối cùng

Sản phẩm cuối cùng phải bao gồm đầy đủ các thành phần sau:

### 4.1. Ứng dụng web demo

Ứng dụng web đơn giản được xây dựng bằng Python, cung cấp:

* Chức năng đăng nhập và đăng xuất.
* Danh sách tài nguyên thuộc quyền sở hữu của người dùng.
* Chức năng xem chi tiết tài nguyên.
* Chức năng export dữ liệu.
* Chức năng delete dữ liệu.
* Các API nhận tham số ID tài nguyên.

Giao diện chỉ cần HTML, CSS và Bootstrap cơ bản, không yêu cầu React.

### 4.2. Hệ thống thu thập log

Mỗi request quan trọng cần ghi lại ít nhất các trường:

| Trường        | Ý nghĩa                            |
| ------------- | ---------------------------------- |
| timestamp     | Thời điểm request                  |
| user_id       | Người dùng gửi request             |
| session_id    | Phiên đăng nhập                    |
| ip_address    | Địa chỉ IP                         |
| http_method   | GET, POST, DELETE                  |
| endpoint      | API được truy cập                  |
| action        | Hành động view, export hoặc delete |
| resource_id   | ID tài nguyên được yêu cầu         |
| status_code   | Mã phản hồi HTTP                   |
| response_time | Thời gian xử lý request            |
| user_agent    | Thông tin trình duyệt hoặc client  |

### 4.3. Bộ dữ liệu hành vi

Bộ dữ liệu phải bao gồm:

* Dữ liệu hành vi bình thường.
* Dữ liệu Export Abuse.
* Dữ liệu Delete Abuse.
* Dữ liệu IDOR/BOLA Scan.
* Nhãn scenario dùng để kiểm thử và đánh giá.

Mô hình Isolation Forest được huấn luyện chủ yếu trên dữ liệu bình thường. Nhãn bất thường chỉ được sử dụng để kiểm thử và đánh giá kết quả.

### 4.4. Module Machine Learning

Module Machine Learning phải thực hiện được:

* Đọc dữ liệu log.
* Tiền xử lý dữ liệu.
* Tạo đặc trưng theo cửa sổ thời gian.
* Huấn luyện Isolation Forest.
* Lưu và tải mô hình.
* Tính anomaly score.
* Phân loại request hoặc phiên hoạt động là bình thường hay bất thường.
* Ghi kết quả phát hiện vào cơ sở dữ liệu hoặc file kết quả.

### 4.5. Màn hình kết quả

Màn hình kết quả cần hiển thị:

* Thời gian phát hiện.
* User ID.
* Session ID.
* Endpoint hoặc hành động liên quan.
* Anomaly score.
* Kết quả Normal hoặc Anomaly.
* Scenario dự kiến.
* Thông tin hỗ trợ giải thích lý do bị đánh dấu.

Hệ thống không yêu cầu dashboard realtime phức tạp. Một trang HTML đơn giản hoặc bảng kết quả là đủ.

### 4.6. Tài liệu và báo cáo

* Tài liệu mô tả phạm vi dự án.
* Tài liệu kiến trúc hệ thống.
* Tài liệu thiết kế cơ sở dữ liệu.
* Tài liệu mô tả log và đặc trưng.
* Tài liệu mô tả ba scenario.
* Kết quả huấn luyện và đánh giá mô hình.
* Hướng dẫn cài đặt và chạy chương trình.
* Kịch bản demo sản phẩm.

---

## 5. Ba scenario bắt buộc

### 5.1. Scenario 1 – Export Abuse

#### Hành vi bình thường

Người dùng chủ yếu xem dữ liệu và chỉ thỉnh thoảng export một báo cáo hoặc một nhóm dữ liệu nhỏ.

#### Hành vi bất thường

Người dùng đột ngột:

* Thực hiện nhiều lần export trong một khoảng thời gian ngắn.
* Export nhiều loại dữ liệu mà trước đó ít hoặc chưa từng truy cập.
* Export dữ liệu ngay sau khi đăng nhập.
* Chuyển từ hành vi chỉ xem dữ liệu sang export liên tục.

#### Dữ liệu cần quan sát

* Số lần export trong một cửa sổ thời gian.
* Tỷ lệ request export trên tổng request.
* Số endpoint export khác nhau.
* Thời gian từ khi đăng nhập đến lần export đầu tiên.
* Mức độ khác biệt so với hành vi trước đó của người dùng.

#### Kết quả mong đợi

Hệ thống ghi nhận phiên hoạt động có anomaly score cao và đánh dấu là hành vi Export Abuse tiềm năng.

---

### 5.2. Scenario 2 – Delete Abuse

#### Hành vi bình thường

Người dùng thường xem hoặc cập nhật dữ liệu và rất ít khi thực hiện thao tác delete.

#### Hành vi bất thường

Người dùng đột ngột:

* Gửi nhiều request delete trong một phiên.
* Xóa liên tiếp nhiều tài nguyên.
* Chuyển từ hành vi chỉ đọc sang hành vi xóa dữ liệu.
* Thực hiện delete ngay sau khi đăng nhập.
* Có tỷ lệ request delete cao bất thường so với lịch sử.

#### Dữ liệu cần quan sát

* Số request delete trong một cửa sổ thời gian.
* Tỷ lệ delete trên tổng request.
* Số resource ID khác nhau bị tác động.
* Khoảng thời gian giữa các request delete.
* Hành động phổ biến trước đó của người dùng.
* Thời gian từ lúc đăng nhập đến lần delete đầu tiên.

#### Kết quả mong đợi

Hệ thống phát hiện sự thay đổi hành vi và đánh dấu phiên hoạt động là Delete Abuse tiềm năng.

---

### 5.3. Scenario 3 – IDOR/BOLA Scan

#### Hành vi bình thường

Người dùng chỉ truy cập các tài nguyên thuộc quyền sở hữu hoặc được cấp quyền cho mình.

#### Hành vi bất thường

Người dùng hoặc script:

* Thay đổi liên tiếp giá trị resource ID.
* Truy cập nhiều ID không thuộc quyền sở hữu.
* Thử các ID gần nhau hoặc có tính tuần tự.
* Gửi request với tốc độ thấp để tránh rate limiting.
* Nhận nhiều phản hồi 403 hoặc 404.
* Truy cập nhiều tài nguyên duy nhất trong một phiên.

#### Dữ liệu cần quan sát

* Số resource ID khác nhau.
* Tỷ lệ tài nguyên không thuộc quyền sở hữu.
* Tỷ lệ status code 403 và 404.
* Mức độ tuần tự của resource ID.
* Số endpoint có chứa tham số ID.
* Số request truy cập tài nguyên trong một cửa sổ thời gian.

#### Kết quả mong đợi

Hệ thống đánh dấu phiên hoạt động có dấu hiệu dò quét IDOR/BOLA, kể cả khi số request chưa vượt qua ngưỡng rate limiting.

> Lưu ý: ứng dụng vẫn phải kiểm tra quyền truy cập và trả về 403 khi người dùng truy cập tài nguyên không thuộc quyền sở hữu. Machine Learning đóng vai trò phát hiện hành vi dò quét, không thay thế cơ chế authorization.

---

## 6. Phạm vi thực hiện

### 6.1. Phạm vi bắt buộc

* Web demo bằng Python Flask hoặc FastAPI.
* Giao diện HTML, CSS hoặc Bootstrap cơ bản.
* Đăng nhập bằng session hoặc JWT đơn giản.
* API xem, export và delete dữ liệu.
* Kiểm tra quyền sở hữu tài nguyên.
* Thu thập structured log.
* Lưu log bằng SQLite, MySQL hoặc file CSV/JSON.
* Tạo dữ liệu hành vi bình thường và bất thường.
* Feature engineering.
* Mô hình Isolation Forest.
* Phát hiện ba scenario đã chốt.
* Trang hiển thị kết quả phát hiện.
* Đánh giá mô hình.
* Viết báo cáo và kịch bản demo.

### 6.2. Phạm vi không thực hiện

Đề tài không thực hiện các nội dung sau:

* Không xây dựng frontend bằng React.
* Không triển khai hệ thống lên cloud.
* Không sử dụng deep learning.
* Không sử dụng Autoencoder trong phiên bản chính.
* Không xây dựng hệ thống realtime phức tạp.
* Không xử lý luồng dữ liệu bằng Kafka hoặc hệ thống streaming.
* Không xây dựng kiến trúc microservices.
* Không xây dựng ứng dụng thương mại hoàn chỉnh.
* Không phát triển scenario Session Hijacking.
* Không phát hiện SQL Injection, XSS hoặc CSRF.
* Không xây dựng WAF hoặc Firewall.
* Không thay thế authorization bằng Machine Learning.
* Không thu thập dữ liệu từ hệ thống thật hoặc dữ liệu cá nhân của người dùng.
* Không mở ứng dụng demo có chủ ý chứa lỗ hổng ra Internet công khai.

Mọi chức năng ngoài danh sách phạm vi bắt buộc đều được xem là nội dung mở rộng và chỉ thực hiện sau khi phiên bản chính đã hoàn thành.

---

## 7. Công nghệ dự kiến

| Thành phần        | Công nghệ                   |
| ----------------- | --------------------------- |
| Ngôn ngữ chính    | Python                      |
| Web framework     | Flask hoặc FastAPI          |
| Giao diện         | HTML, CSS, Bootstrap        |
| Cơ sở dữ liệu     | SQLite                      |
| Xử lý dữ liệu     | Pandas, NumPy               |
| Machine Learning  | Scikit-learn                |
| Mô hình chính     | Isolation Forest            |
| Biểu đồ           | Matplotlib                  |
| Quản lý mã nguồn  | Git và GitHub               |
| Quản lý công việc | GitHub Projects hoặc Trello |

Ưu tiên sử dụng Flask và SQLite để giảm độ phức tạp của dự án.

---

## 8. Tiêu chí hoàn thành

Đề tài được xem là hoàn thành khi đáp ứng đủ các điều kiện:

* [ ] Ứng dụng web có thể đăng nhập và sử dụng các chức năng cơ bản.
* [ ] Có API view, export và delete.
* [ ] Có kiểm tra quyền sở hữu tài nguyên.
* [ ] Tất cả request quan trọng được ghi log.
* [ ] Có dữ liệu hành vi bình thường.
* [ ] Có dữ liệu kiểm thử cho ba scenario.
* [ ] Có pipeline tạo đặc trưng.
* [ ] Huấn luyện và lưu được mô hình Isolation Forest.
* [ ] Hệ thống trả về anomaly score và kết quả phát hiện.
* [ ] Có thể chạy thử Export Abuse.
* [ ] Có thể chạy thử Delete Abuse.
* [ ] Có thể chạy thử IDOR/BOLA Scan.
* [ ] Có bảng hiển thị kết quả.
* [ ] Có số liệu đánh giá mô hình.
* [ ] Có README hướng dẫn chạy.
* [ ] Có báo cáo và kịch bản demo.
* [ ] Hoàn thành trước hoặc trong ngày 19/07/2026.

---

## 9. Quy tắc kiểm soát phạm vi

Trước khi thêm một chức năng mới, phải trả lời ba câu hỏi:

1. Chức năng này có trực tiếp phục vụ một trong ba scenario không?
2. Chức năng này có nằm trong danh sách sản phẩm cuối cùng không?
3. Nếu không làm chức năng này thì sản phẩm có mất khả năng demo chính không?

Nếu cả ba câu trả lời đều là “không”, chức năng đó không được đưa vào phiên bản chính.

---

## 10. Deadline

**Deadline cuối cùng: Chủ nhật, ngày 19/07/2026.**

Đến deadline, hệ thống phải chạy được toàn bộ luồng:

**Người dùng thao tác → Web ghi log → Tạo đặc trưng → Mô hình chấm điểm → Hiển thị cảnh báo → Đánh giá kết quả.**
