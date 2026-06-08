# PROJECT SCOPE

## 1. Thông tin đề tài

**Tên đề tài:**
**Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning**

**Ứng dụng nghiệp vụ:**  
**Hệ thống quản lý tài liệu nội bộ với hai vai trò User và Admin.**

**Thời gian thực hiện:** 06/06/2026 – 19/07/2026

---

## 2. Mô tả vấn đề

Các cuộc tấn công web có dấu hiệu rõ ràng như gửi quá nhiều request trong thời gian ngắn thường có thể được phát hiện bằng rule-based, rate limiting, firewall hoặc WAF. Tuy nhiên, một số hành vi nguy hiểm không vượt qua các ngưỡng cố định nên khó phát hiện chỉ bằng luật. Ví dụ, một người dùng thường chỉ xem dữ liệu nhưng đột ngột thực hiện nhiều thao tác export hoặc delete trong một phiên đăng nhập. Kẻ tấn công cũng có thể thay đổi lần lượt các ID tài nguyên với tốc độ thấp để tránh cơ chế giới hạn request. Vì vậy, đề tài tập trung xây dựng hồ sơ hành vi bình thường của người dùng và sử dụng Machine Learning để nhận diện các hành vi lệch khỏi hồ sơ đó. Hệ thống sẽ sử dụng mô hình Isolation Forest để tính điểm bất thường và hỗ trợ phát hiện các hành vi có tính ngữ cảnh mà khó đặt một ngưỡng cố định.

---

## 3. Mục tiêu đề tài

Xây dựng một hệ thống web quản lý tài liệu nội bộ có khả năng:

1. Cho phép người dùng đăng nhập, đăng xuất và sử dụng các chức năng quản lý tài liệu thông qua giao diện web.
2. Phân quyền hai vai trò User và Admin.
3. Cho phép User tạo, xem, cập nhật, tìm kiếm, lọc, phân trang, export, xóa và khôi phục tài liệu của mình.
4. Cho phép Admin quản lý người dùng, tài liệu, request log và cảnh báo bất thường.
5. Thu thập structured log về hành vi truy cập của người dùng.
6. Cho phép Admin tìm kiếm, lọc, xem chi tiết và export log.
7. Chuyển log thành các đặc trưng phục vụ Machine Learning.
8. Huấn luyện mô hình Isolation Forest trên dữ liệu hành vi bình thường.
9. Phát hiện các hành vi bất thường thuộc ba scenario đã xác định.
10. Hiển thị kết quả phát hiện gồm điểm bất thường, scenario nghi ngờ, feature nổi bật và thông tin request liên quan.
11. Đánh giá khả năng phát hiện của mô hình trên dữ liệu kiểm thử.

### 3.1. Định nghĩa “web hoàn chỉnh” trong phạm vi đồ án

Trong đề tài này, “web hoàn chỉnh” không có nghĩa là hệ thống doanh nghiệp quy mô lớn. Web được xem là hoàn chỉnh khi:

* Có giao diện để người dùng thao tác, không chỉ gồm một số API dùng để sinh log.
* Có database, dữ liệu mẫu, đăng nhập, session và phân quyền.
* Có luồng quản lý tài liệu từ tạo mới đến xóa và khôi phục.
* Có tìm kiếm, lọc, phân trang và xử lý lỗi.
* Có trang quản trị người dùng, tài liệu, log và cảnh báo.
* Có thể kiểm thử và demo theo một luồng nghiệp vụ hoàn chỉnh.

---

## 4. Sản phẩm cuối cùng

Sản phẩm cuối cùng phải bao gồm đầy đủ các thành phần sau:

### 4.1. Ứng dụng web quản lý tài liệu nội bộ

Ứng dụng được xây dựng bằng Python Flask, sử dụng HTML, CSS, Jinja2 và Bootstrap. Web không chỉ là nơi sinh log mà phải có luồng nghiệp vụ sử dụng được.

#### Vai trò User

User được phép:

* Đăng nhập và đăng xuất.
* Xem dashboard cá nhân.
* Xem danh sách và chi tiết tài liệu thuộc quyền sở hữu.
* Tạo và cập nhật tài liệu.
* Tìm kiếm tài liệu theo tiêu đề hoặc từ khóa.
* Lọc tài liệu theo trạng thái hoặc thời gian.
* Phân trang danh sách tài liệu.
* Export tài liệu hoặc danh sách tài liệu thuộc quyền sở hữu.
* Xóa mềm tài liệu và xem thùng rác.
* Khôi phục hoặc xóa vĩnh viễn tài liệu sau bước xác nhận.
* Xem profile và đổi mật khẩu.

#### Vai trò Admin

Admin được phép:

* Xem dashboard quản trị.
* Xem, tìm kiếm, khóa hoặc mở tài khoản người dùng.
* Xem và lọc tài liệu trong toàn hệ thống.
* Xem, tìm kiếm, lọc, phân trang và export request log.
* Chạy quá trình phát hiện bất thường.
* Xem chi tiết cảnh báo và các feature liên quan.
* Cập nhật trạng thái cảnh báo thành New, Reviewing hoặc Resolved.

#### Nguyên tắc phân quyền

* User chỉ được truy cập và thay đổi tài liệu thuộc quyền sở hữu của mình.
* Request truy cập tài liệu không thuộc sở hữu phải bị từ chối bằng 403 hoặc 404 theo quy ước đã chọn.
* Admin không được xem password, cookie hoặc session token nguyên bản.
* Machine Learning chỉ phát hiện hành vi bất thường, không thay thế authorization.

#### Bảng chức năng và tiêu chí hoàn thành

| Mã | Chức năng | Actor | Đầu vào | Kết quả | Tiêu chí hoàn thành |
| --- | --------- | ----- | ------- | ------- | ------------------- |
| U01 | Đăng nhập/đăng xuất | User/Admin | Username, password hoặc session | Tạo hoặc xóa session | Đăng nhập đúng; sai thông tin báo lỗi; logout chặn lại route bảo vệ |
| U02 | Dashboard cá nhân | User | User hiện tại | Thống kê tài liệu | Chỉ hiển thị dữ liệu của user hiện tại |
| U03 | CRUD tài liệu | User | Tiêu đề, nội dung, document ID | Tạo/xem/sửa tài liệu | Không thao tác được tài liệu của user khác |
| U04 | Search/filter/pagination | User | Từ khóa, bộ lọc, số trang | Danh sách phù hợp | Giữ nguyên điều kiện khi chuyển trang |
| U05 | Trash/restore | User | Document ID | Xóa mềm hoặc khôi phục | Chỉ chủ sở hữu được thực hiện |
| U06 | Export tài liệu | User | Document ID hoặc bộ lọc | File tải xuống | Chỉ export dữ liệu thuộc quyền sở hữu |
| U07 | Profile/đổi mật khẩu | User | Dữ liệu profile, mật khẩu | Cập nhật tài khoản | Password được hash, không lưu plaintext |
| A01 | Quản lý user | Admin | User ID, trạng thái | Danh sách/khóa/mở user | User bị khóa không đăng nhập được |
| A02 | Quản lý tài liệu | Admin | User, trạng thái, từ khóa | Danh sách tài liệu | Có lọc và phân trang |
| A03 | Quản lý log | Admin | Bộ lọc log | Danh sách/chi tiết/export log | Không hiển thị dữ liệu nhạy cảm |
| A04 | Chạy detection | Admin | Log hoặc khoảng thời gian | Anomaly score, prediction | Không tạo alert trùng cho cùng window/model |
| A05 | Quản lý alert | Admin | Alert ID, trạng thái | Chi tiết và trạng thái alert | Truy ngược được về log gốc |

### 4.2. Hệ thống thu thập log

Mỗi request quan trọng cần ghi lại ít nhất các trường:

| Trường        | Ý nghĩa                            |
| ------------- | ---------------------------------- |
| timestamp     | Thời điểm request                  |
| user_id       | Người dùng gửi request             |
| session_id_hash | Giá trị nhận diện phiên đã được hash/rút gọn |
| ip_address    | Địa chỉ IP                         |
| http_method   | GET, POST, DELETE                  |
| endpoint      | API được truy cập                  |
| action        | Hành động view, export hoặc delete |
| resource_id   | ID tài nguyên được yêu cầu         |
| ownership_match | Người dùng có quyền sở hữu hoặc được cấp quyền với tài nguyên hay không |
| status_code   | Mã phản hồi HTTP                   |
| response_time | Thời gian xử lý request            |
| user_agent    | Thông tin trình duyệt hoặc client  |

Ngoài việc thu thập log, hệ thống phải có trang quản lý log dành cho Admin, gồm:

* Xem danh sách và chi tiết log.
* Tìm kiếm/lọc theo user, thời gian, method, endpoint, action và status code.
* Phân trang, sắp xếp theo thời gian.
* Export log thành CSV để phục vụ xử lý dữ liệu và Machine Learning.
* Truy ngược từ một alert về các log thuộc cùng cửa sổ hành vi.

Không được ghi password, request body nhạy cảm, cookie hoặc session token nguyên bản. Nên lưu `session_id_hash` thay cho session ID thô.

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

#### Trường log dùng để chứng minh

* `timestamp`: xác định số lần export trong cửa sổ thời gian và thời gian từ lúc đăng nhập đến lần export đầu tiên.
* `user_id`, `session_id`: nhóm các request theo đúng người dùng và phiên hoạt động.
* `endpoint`, `action`: xác định request nào là export và số endpoint export khác nhau.
* `http_method`, `status_code`: kiểm tra loại request và export có được thực hiện thành công hay không.

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

#### Trường log dùng để chứng minh

* `timestamp`: xác định số lần delete, khoảng cách thời gian giữa các lần delete và thời gian từ lúc đăng nhập đến lần delete đầu tiên.
* `user_id`, `session_id`: nhóm các request theo đúng người dùng và phiên hoạt động.
* `http_method`, `endpoint`, `action`: xác định request delete và tỷ lệ delete trên tổng request.
* `resource_id`: xác định số tài nguyên khác nhau bị tác động.
* `ownership_match`, `status_code`: kiểm tra quyền với tài nguyên và kết quả xử lý request.

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

#### Trường log dùng để chứng minh

* `timestamp`: xác định chuỗi request theo thời gian, kể cả khi tốc độ gửi request thấp.
* `user_id`, `session_id`: nhóm các lần thử truy cập trong cùng một người dùng hoặc phiên hoạt động.
* `endpoint`, `resource_id`: xác định số ID khác nhau, thứ tự thay đổi ID và mức độ tuần tự của chúng.
* `ownership_match`: xác định tài nguyên có thuộc quyền sở hữu hoặc được cấp quyền cho người dùng hay không.
* `status_code`: tính tỷ lệ phản hồi 403 và 404.
* `ip_address`, `user_agent`: hỗ trợ đối chiếu các request phát sinh từ cùng một client hoặc script.

#### Kết quả mong đợi

Hệ thống đánh dấu phiên hoạt động có dấu hiệu dò quét IDOR/BOLA, kể cả khi số request chưa vượt qua ngưỡng rate limiting.

> Lưu ý: ứng dụng vẫn phải kiểm tra quyền truy cập và trả về 403 khi người dùng truy cập tài nguyên không thuộc quyền sở hữu. Machine Learning đóng vai trò phát hiện hành vi dò quét, không thay thế cơ chế authorization.

---

## 6. Phạm vi thực hiện

### 6.1. Phạm vi bắt buộc

* Web quản lý tài liệu nội bộ bằng Python Flask.
* Giao diện HTML, CSS, Jinja2 và Bootstrap.
* Hai vai trò User và Admin.
* Đăng nhập, đăng xuất, session và phân quyền.
* Dashboard User và dashboard Admin ở mức cơ bản.
* CRUD tài liệu.
* Tìm kiếm, lọc và phân trang tài liệu.
* Kiểm tra quyền sở hữu tài nguyên.
* Soft delete, thùng rác, khôi phục và xóa vĩnh viễn có xác nhận.
* Export tài liệu.
* Profile và đổi mật khẩu.
* Quản lý user và tài liệu ở phía Admin.
* Thu thập structured log.
* Trang quản lý, tìm kiếm, lọc, xem chi tiết và export log.
* Tạo dữ liệu hành vi bình thường và bất thường.
* Feature engineering.
* Mô hình Isolation Forest.
* Phát hiện ba scenario đã chốt.
* Trang hiển thị và quản lý cảnh báo.
* Đánh giá mô hình.
* README, báo cáo, slide và kịch bản demo.

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
| Web framework     | Flask                       |
| Giao diện         | Jinja2, HTML, CSS, Bootstrap |
| Cơ sở dữ liệu/ORM | SQLite, SQLAlchemy           |
| Xử lý dữ liệu     | Pandas, NumPy               |
| Machine Learning  | Scikit-learn                |
| Mô hình chính     | Isolation Forest            |
| Biểu đồ           | Matplotlib                  |
| Quản lý mã nguồn  | Git và GitHub               |
| Quản lý công việc | GitHub Projects hoặc Trello |

Sử dụng Flask và SQLite để dùng chung hệ sinh thái Python với phần xử lý dữ liệu và Machine Learning, từ đó giảm độ phức tạp khi tích hợp.

---

## 8. Tiêu chí hoàn thành

Đề tài được xem là hoàn thành khi đáp ứng đủ các điều kiện:

### 8.1. Web và phân quyền

* [ ] Ứng dụng có thể đăng nhập, đăng xuất và quản lý session.
* [ ] Có hai vai trò User và Admin.
* [ ] User có dashboard và CRUD tài liệu.
* [ ] Có tìm kiếm, lọc và phân trang tài liệu.
* [ ] Có export, soft delete, thùng rác và khôi phục.
* [ ] Có profile và đổi mật khẩu.
* [ ] Admin có thể quản lý user và xem tài liệu toàn hệ thống.
* [ ] Có kiểm tra quyền sở hữu tài nguyên.
* [ ] Request trái quyền không làm lộ dữ liệu.

### 8.2. Logging và dữ liệu

* [ ] Tất cả request quan trọng được ghi structured log.
* [ ] Log không chứa password, cookie hoặc token nguyên bản.
* [ ] Admin có thể xem, tìm kiếm, lọc, phân trang và export log.
* [ ] Có dữ liệu hành vi bình thường.
* [ ] Có dữ liệu kiểm thử cho ba scenario.
* [ ] Có ground truth phục vụ đánh giá.

### 8.3. Machine Learning và cảnh báo

* [ ] Có pipeline tạo đặc trưng theo cửa sổ thời gian.
* [ ] Train set chủ yếu chứa dữ liệu bình thường.
* [ ] Huấn luyện và lưu được mô hình Isolation Forest.
* [ ] Hệ thống trả về anomaly score và prediction.
* [ ] Chạy thử được Export Abuse, Delete Abuse và IDOR/BOLA Scan.
* [ ] Có bảng hiển thị và quản lý cảnh báo.
* [ ] Alert có thể truy ngược về log gốc.
* [ ] Có Precision, Recall, F1-score, False Positive Rate và Confusion Matrix.
* [ ] Có detection rate theo từng scenario.

### 8.4. Tài liệu và đóng gói

* [ ] Có README hướng dẫn cài đặt và chạy.
* [ ] Có script seed/reset dữ liệu.
* [ ] Có báo cáo, slide và kịch bản demo.
* [ ] Có video demo dự phòng.
* [ ] Có bản backup source, dữ liệu mẫu và model.
* [ ] Hoàn thành trước hoặc trong ngày 19/07/2026.

---

## 9. Quy tắc kiểm soát phạm vi

Trước khi thêm một chức năng mới, phải trả lời ba câu hỏi:

1. Chức năng này có trực tiếp phục vụ nghiệp vụ quản lý tài liệu, hệ thống logging hoặc một trong ba scenario không?
2. Chức năng này có nằm trong danh sách sản phẩm cuối cùng không?
3. Nếu không làm chức năng này thì sản phẩm có mất khả năng demo chính không?

Nếu cả ba câu trả lời đều là “không”, chức năng đó không được đưa vào phiên bản chính.

---

## 10. Deadline

**Deadline cuối cùng: Chủ nhật, ngày 19/07/2026.**

Đến deadline, hệ thống phải chạy được toàn bộ luồng:

**Người dùng thao tác trên web quản lý tài liệu → Web ghi structured log → Tạo đặc trưng → Mô hình chấm điểm → Lưu và hiển thị cảnh báo → Đánh giá kết quả.**

### 10.1. Deadline chi tiết cho từng task

Các deadline dưới đây được dùng để gắn vào trường `Deadline` trên GitHub Projects hoặc Trello. Deadline cuối cùng của toàn bộ dự án vẫn là ngày **19/07/2026**.

| Mã task | Công việc | Deadline |
| ------- | --------- | -------- |
| T01 | Tạo cấu trúc thư mục dự án | 08/06/2026 |
| T02 | Cập nhật `docs/project_scope.md` theo web quản lý tài liệu hoàn chỉnh | 08/06/2026 |
| T03 | Đặc tả Export Abuse | 08/06/2026 |
| T04 | Đặc tả Delete Abuse | 08/06/2026 |
| T05 | Đặc tả IDOR/BOLA Scan | 08/06/2026 |
| T06 | Thiết kế use case User/Admin và kiến trúc hệ thống | 10/06/2026 |
| T07 | Thiết kế cơ sở dữ liệu và log schema | 12/06/2026 |
| T08 | Khởi tạo Flask, layout và database seed | 13/06/2026 |
| T09 | Xây dựng đăng nhập, session và phân quyền | 14/06/2026 |
| T10 | Xây dựng dashboard User và CRUD tài liệu | 16/06/2026 |
| T11 | Xây dựng search, filter và pagination | 17/06/2026 |
| T12 | Xây dựng trash, restore và xóa vĩnh viễn | 18/06/2026 |
| T13 | Xây dựng export tài liệu, profile và đổi mật khẩu | 19/06/2026 |
| T14 | Xây dựng chức năng quản trị user và tài liệu | 20/06/2026 |
| T15 | Kiểm thử và khóa chức năng web nghiệp vụ | 21/06/2026 |
| T16 | Xây dựng structured request logging | 23/06/2026 |
| T17 | Xây dựng trang quản lý và export log | 24/06/2026 |
| T18 | Sinh dữ liệu hành vi bình thường | 25/06/2026 |
| T19 | Sinh dữ liệu Export Abuse | 26/06/2026 |
| T20 | Sinh dữ liệu Delete Abuse | 27/06/2026 |
| T21 | Sinh dữ liệu IDOR/BOLA Scan | 28/06/2026 |
| T22 | Audit và khóa raw dataset | 29/06/2026 |
| T23 | Tiền xử lý dữ liệu và tạo feature | 03/07/2026 |
| T24 | Chia train/validation/test và thực hiện EDA | 05/07/2026 |
| T25 | Huấn luyện và tuning Isolation Forest | 08/07/2026 |
| T26 | Đánh giá mô hình và phân tích lỗi | 10/07/2026 |
| T27 | Đóng gói và tích hợp model vào web | 12/07/2026 |
| T28 | Xây dựng trang quản lý alerts | 13/07/2026 |
| T29 | Kiểm thử toàn bộ ba scenario | 15/07/2026 |
| T30 | Hoàn thiện README và báo cáo | 16/07/2026 |
| T31 | Làm slide và kịch bản demo | 17/07/2026 |
| T32 | Quay video, đóng gói và backup | 18/07/2026 |
| T33 | Tổng kiểm tra và hoàn thành bản nộp cuối | 19/07/2026 |

---

## 11. Danh sách feature tối thiểu dự kiến

### 11.1. Hoạt động chung

* `request_count`
* `unique_endpoint_count`
* `unique_method_count`
* `session_duration_sec`
* `avg_inter_request_sec`
* `min_inter_request_sec`
* `burst_rate`
* `avg_response_time_ms`
* `error_rate`

### 11.2. Export/Delete Abuse

* `sensitive_request_count`
* `sensitive_ratio`
* `export_count`
* `export_ratio`
* `delete_count`
* `delete_ratio`
* `unique_deleted_resource_count`
* `time_to_first_export_sec`
* `time_to_first_delete_sec`

### 11.3. IDOR/BOLA Scan

* `unique_resource_id_count`
* `unique_failed_resource_id_count`
* `resource_id_change_rate`
* `ownership_mismatch_rate`
* `forbidden_count`
* `forbidden_rate`
* `not_found_count`
* `not_found_rate`

Không bắt buộc giữ toàn bộ feature. Chỉ sử dụng các feature có công thức rõ ràng, không chứa nhãn và có ý nghĩa trong phân tích hành vi.

---

## 12. Ba điều cần xác nhận với giảng viên

1. Với ba scenario Export Abuse, Delete Abuse và IDOR/BOLA Scan, nên huấn luyện một mô hình Isolation Forest chung trên dữ liệu bình thường rồi xác định tên scenario dựa trên action, endpoint và các đặc trưng liên quan, hay nên xây dựng mô hình riêng cho từng scenario?
2. Đối với IDOR/BOLA Scan, các trường log `user_id`, `session_id_hash`, `resource_id`, `status_code` và `ownership_match` đã đủ để chứng minh hành vi bất thường chưa, hay cần bổ sung thêm trường hoặc đặc trưng nào?
3. Khi đánh giá mô hình, nên tập trung vào Precision, Recall, F1-score và False Positive Rate trên bộ dữ liệu kiểm thử có nhãn, hay chỉ cần anomaly score và kết quả demo ba scenario là đủ trong phạm vi đồ án?

---

## 13. Kết quả cần đạt trong ngày cập nhật scope

* [ ] File `docs/project_scope.md` đã mô tả rõ web quản lý tài liệu nội bộ.
* [ ] Đã xác định hai vai trò User và Admin.
* [ ] Mỗi nhóm chức năng có actor, đầu vào, kết quả và tiêu chí hoàn thành.
* [ ] Ba scenario vẫn có mô tả normal, anomaly, log chứng minh và kết quả mong đợi.
* [ ] GitHub Project đã được cập nhật theo danh sách task mới.
* [ ] Không còn dùng cụm “web demo” theo nghĩa chỉ có vài API sinh log.
