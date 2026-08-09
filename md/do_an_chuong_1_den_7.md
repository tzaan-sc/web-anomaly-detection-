# ĐỒ ÁN

# XÂY DỰNG HỆ THỐNG PHÁT HIỆN HÀNH VI TRUY CẬP BẤT THƯỜNG TRÊN ỨNG DỤNG WEB BẰNG MACHINE LEARNING

> **Ghi chú:** Nội dung dưới đây được xây dựng dựa hoàn toàn trên "Hồ sơ
> thông tin toàn bộ đồ án" do nhóm cung cấp. Những thông tin chưa được
> cung cấp cụ thể được đánh dấu `[CẦN BỔ SUNG]`.

------------------------------------------------------------------------

# CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI

## 1.1. Lý do chọn đề tài

Trong các ứng dụng web lưu trữ và chia sẻ tệp tin, người dùng thực hiện
nhiều thao tác thông qua các HTTP Request như đăng nhập, duyệt thư mục,
xem tệp, tải xuống, xuất dữ liệu, xóa và khôi phục tệp. Các thao tác này
có thể hoàn toàn hợp lệ về mặt cú pháp HTTP nhưng vẫn bị lạm dụng để
thực hiện các hành vi gây ảnh hưởng đến dữ liệu và tài nguyên của hệ
thống.

Đề tài tập trung vào nhóm hành vi **lạm dụng logic nghiệp vụ (Business
Logic Abuse)**. Các trường hợp được nghiên cứu trong hệ thống StudyDrive
gồm xuất dữ liệu với tần suất bất thường (Export Abuse), xóa nhiều tệp
liên tục (Delete Abuse) và rà quét quyền truy cập đối tượng thông qua
IDOR/BOLA Scan. Đây là các hành vi khó được phát hiện chỉ bằng cách kiểm
tra cú pháp request, bởi request của người dùng vẫn có thể là những
request hợp lệ đối với ứng dụng.

Trong hệ thống, mỗi HTTP Request được ghi nhận tự động tại tầng Flask
Middleware bằng hook `after_request`. Dữ liệu log được lưu dưới dạng cấu
trúc trong bảng `request_logs`, sau đó được gom thành các cửa sổ thời
gian 5 phút và chuyển thành vector 25 đặc trưng số. Mô hình Isolation
Forest được sử dụng để học phân bố hành vi bình thường và phát hiện các
cửa sổ có đặc điểm khác biệt.

Việc xây dựng hệ thống theo hướng này giúp kết hợp ba thành phần trong
một quy trình thống nhất: ứng dụng web thực tế, cơ chế thu thập nhật ký
truy cập và mô hình Machine Learning. Kết quả phát hiện được đưa trở lại
giao diện quản trị dưới dạng cảnh báo, đồng thời cho phép quản trị viên
truy ngược từ cảnh báo về các request log gốc trong đúng cửa sổ 5 phút.

Vì vậy, đề tài được lựa chọn nhằm xây dựng một hệ thống có khả năng thu
thập dữ liệu truy cập, phân tích hành vi và hỗ trợ quản trị viên phát
hiện các hành vi truy cập bất thường trong chính môi trường ứng dụng web
StudyDrive.

## 1.2. Mục tiêu của đề tài

### 1.2.1. Mục tiêu tổng quát

Xây dựng ứng dụng web StudyDrive tích hợp hệ thống phát hiện hành vi
truy cập bất thường bằng Machine Learning, trong đó dữ liệu truy cập
được tự động thu thập từ tầng ứng dụng, xử lý thành các đặc trưng hành
vi và phân tích bằng mô hình Isolation Forest để phát hiện các cửa sổ
hành vi bất thường, tạo cảnh báo và hỗ trợ quản trị viên truy ngược về
log gốc.

### 1.2.2. Mục tiêu cụ thể

-   Xây dựng ứng dụng web StudyDrive phục vụ lưu trữ và chia sẻ tệp tin.
-   Xây dựng cơ chế xác thực và phân quyền người dùng với các vai trò
    `USER` và `ADMIN`, đồng thời hỗ trợ quyền tệp `OWNER`, `VIEWER` và
    `NONE`.
-   Xây dựng cơ chế ghi nhật ký truy cập tự động tại Flask Middleware.
-   Bảo vệ thông tin nhạy cảm trong log bằng cách băm Session ID bằng
    SHA-256 và không lưu password, CSRF token hoặc session token dạng
    plaintext.
-   Xây dựng dữ liệu giả lập gồm hành vi bình thường và ba kịch bản bất
    thường: Export Abuse, Delete Abuse và IDOR/BOLA Scan.
-   Gom nhóm request log theo cửa sổ 5 phút dựa trên
    `(user_id, session_id_hash)`.
-   Trích xuất 25 đặc trưng số mô tả tần suất, tốc độ, thao tác nhạy
    cảm, thao tác export/delete và các dấu hiệu 403/404.
-   Huấn luyện mô hình Isolation Forest trên dữ liệu hành vi bình
    thường.
-   Thực hiện tuning một số siêu tham số và lựa chọn ngưỡng phát hiện
    dựa trên percentile.
-   Áp dụng Group-aware Split để hạn chế rò rỉ dữ liệu giữa các tập
    Train, Validation và Test.
-   Đánh giá mô hình bằng Accuracy, Precision, Recall, F1-Score, FPR và
    Confusion Matrix.
-   Tích hợp tiến trình Detection vào giao diện Admin thông qua chức
    năng `Run Detection`.
-   Lưu cảnh báo vào bảng `alerts`, hiển thị trên Alerts Dashboard và hỗ
    trợ truy ngược về request log gốc.
-   Xây dựng bộ kiểm thử tự động bằng Pytest.

## 1.3. Đối tượng và phạm vi nghiên cứu

### 1.3.1. Đối tượng nghiên cứu

Đối tượng nghiên cứu của đề tài gồm:

-   Hành vi truy cập của người dùng trên ứng dụng web StudyDrive.
-   Nhật ký HTTP Request được thu thập tại tầng ứng dụng.
-   Các đặc trưng định lượng biểu diễn hành vi truy cập trong cửa sổ 5
    phút.
-   Phương pháp phát hiện bất thường sử dụng Isolation Forest.
-   Quy trình từ thu thập log, xây dựng đặc trưng, phát hiện, tạo cảnh
    báo đến truy vết log.

### 1.3.2. Phạm vi nghiên cứu

Đề tài được triển khai trên ứng dụng web StudyDrive, một hệ thống lưu
trữ và chia sẻ tệp tin trực tuyến.

Phạm vi chức năng web gồm đăng ký, đăng nhập, quản lý thư mục và tệp,
upload/download, chia sẻ, export, thùng rác và các chức năng quản trị.

Phạm vi phát hiện bất thường tập trung vào ba kịch bản:

1.  **Export Abuse:** gửi liên tục khoảng 30--50 request export CSV/ZIP
    trong 5 phút.
2.  **Delete Abuse:** gửi liên tục khoảng 30 request xóa mềm nhiều tệp
    trong 5 phút.
3.  **IDOR/BOLA Scan:** gửi khoảng 100--500 request truy cập các
    `file_id` tăng dần không thuộc quyền sở hữu và tạo chuỗi lỗi
    403/404.

Hệ thống Machine Learning hiện tại xử lý theo **Batch
Processing/Trigger**, sử dụng cửa sổ 5 phút không chồng lấp và chưa thực
hiện phát hiện theo luồng thời gian thực.

Hệ thống chỉ tạo cảnh báo để quản trị viên giám sát và rà soát thủ công;
chưa có cơ chế tự động khóa tài khoản hoặc chặn IP.

## 1.4. Phương pháp thực hiện

Quy trình thực hiện đề tài được tổ chức thành các bước:

1.  Xây dựng ứng dụng StudyDrive bằng Flask, SQLAlchemy, Jinja2 và
    Bootstrap.
2.  Xây dựng xác thực, phân quyền và các chức năng quản lý tệp.
3.  Tích hợp Middleware ghi log tự động bằng hook `after_request`.
4.  Thu thập dữ liệu từ các script mô phỏng hành vi bình thường và bất
    thường.
5.  Làm sạch dữ liệu, loại bỏ request `static/` và `health`.
6.  Gom request theo `(user_id, session_id_hash)` trong cửa sổ 5 phút.
7.  Trích xuất vector gồm 25 đặc trưng.
8.  Chia dữ liệu thành Train, Validation và Test theo Group Key
    `(run_id, session_id_hash)` để hạn chế data leakage.
9.  Huấn luyện Isolation Forest bằng các cửa sổ Normal-only.
10. Tuning một số siêu tham số trên Validation.
11. Xác định threshold theo percentile.
12. Đánh giá mô hình trên Test Set.
13. Tích hợp model vào `detection_service.py`.
14. Sinh Alert khi điểm bất thường đạt ngưỡng.
15. Hiển thị cảnh báo và cho phép truy ngược về log gốc.
16. Kiểm thử toàn hệ thống bằng Pytest.

## 1.5. Nội dung và kết quả đạt được

Hệ thống đã hoàn thành các thành phần chính gồm ứng dụng StudyDrive, xác
thực và phân quyền, quản lý tệp/thư mục, Middleware logging, pipeline dữ
liệu Machine Learning, Isolation Forest, cơ chế Detection, Alerts
Dashboard và bộ kiểm thử tự động.

Dữ liệu thô gồm **5.567 request log**, được gom thành **24 cửa sổ 5
phút**. Pipeline xây dựng vector 25 đặc trưng và áp dụng Group-aware
Split.

Kết quả thực nghiệm trên Test Set:

  Chỉ số        Kết quả
  ----------- ---------
  Accuracy       66.67%
  Precision      66.67%
  Recall         66.67%
  F1-Score       66.67%
  FPR            33.33%

Ma trận nhầm lẫn gồm TN = 2, FP = 1, FN = 1 và TP = 2. Hai cửa sổ Export
Abuse được phát hiện chính xác; một cửa sổ Normal có tốc độ thao tác
nhanh bị dự đoán nhầm và một cửa sổ BOLA Scan mẫu nhỏ chưa được phát
hiện.

Bộ kiểm thử tự động gồm **38 test cases** và kết quả thực thi là **38
passed in 17.87s**.

## 1.6. Cấu trúc của đồ án

Đồ án được tổ chức thành 7 chương:

-   **Chương 1 -- Tổng quan đề tài:** Trình bày lý do chọn đề tài, mục
    tiêu, đối tượng, phạm vi, phương pháp, kết quả và cấu trúc đồ án.
-   **Chương 2 -- Cơ sở lý thuyết:** Trình bày các khái niệm và cơ sở
    liên quan đến ứng dụng web, logging, hành vi bất thường, Machine
    Learning và Isolation Forest.
-   **Chương 3 -- Phân tích và thiết kế hệ thống:** Trình bày yêu cầu,
    kiến trúc, các thành phần, cơ sở dữ liệu, logging và luồng phát
    hiện.
-   **Chương 4 -- Xây dựng hệ thống và pipeline Machine Learning:**
    Trình bày quá trình triển khai StudyDrive, thu thập dữ liệu, Feature
    Engineering và xây dựng mô hình.
-   **Chương 5 -- Thực nghiệm và đánh giá mô hình:** Trình bày dữ liệu,
    cách chia tập, tuning, threshold và kết quả đánh giá.
-   **Chương 6 -- Kiểm thử và tích hợp hệ thống:** Trình bày kiểm thử tự
    động, tích hợp Detection, Alerts Dashboard và truy vết log.
-   **Chương 7 -- Kết luận và hướng phát triển:** Tổng kết kết quả, hạn
    chế và hướng phát triển.

## 1.7. Tiểu kết chương

Chương 1 đã trình bày tổng quan về đề tài xây dựng hệ thống phát hiện
hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning. Đề
tài tập trung vào việc phát hiện các hành vi lạm dụng logic nghiệp vụ
thông qua dữ liệu request log của StudyDrive. Hệ thống sử dụng Isolation
Forest để phân tích các đặc trưng hành vi trong cửa sổ 5 phút, sau đó
tạo cảnh báo và hỗ trợ truy vết về log gốc. Các chương tiếp theo trình
bày cơ sở lý thuyết, thiết kế, triển khai, thực nghiệm, đánh giá và kiểm
thử hệ thống.

------------------------------------------------------------------------

# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT

## 2.1. Tổng quan về ứng dụng web

Ứng dụng web StudyDrive được xây dựng theo mô hình ứng dụng web với
Flask ở phía máy chủ, Jinja2 và Bootstrap 5 ở tầng giao diện,
Flask-SQLAlchemy làm lớp ORM và MySQL/SQLite làm hệ quản trị cơ sở dữ
liệu tùy môi trường.

Người dùng tương tác với hệ thống thông qua các HTTP Request. Request
được xử lý qua route, kiểm tra xác thực và phân quyền, thực hiện nghiệp
vụ tương ứng rồi tạo HTTP Response.

Trong phạm vi đề tài, request không chỉ là dữ liệu phục vụ xử lý chức
năng mà còn là nguồn dữ liệu để quan sát hành vi người dùng. Do đó, việc
thu thập và chuẩn hóa request log là cơ sở cho pipeline phát hiện bất
thường.

## 2.2. Xác thực và phân quyền

StudyDrive sử dụng hai vai trò chính là `USER` và `ADMIN`. Đối với tài
nguyên tệp, hệ thống phân biệt quyền `OWNER`, `VIEWER` và `NONE`.

Cơ chế phân quyền có vai trò quan trọng đối với bài toán BOLA/IDOR. Một
request có thể có cấu trúc hợp lệ nhưng tài nguyên mà người dùng yêu cầu
không thuộc phạm vi được phép truy cập. Trong trường hợp đó, hệ thống
trả về kết quả từ chối như 403 hoặc 404. Chuỗi các request như vậy là
nguồn tín hiệu để xây dựng đặc trưng phục vụ phát hiện.

## 2.3. Logging tại tầng ứng dụng

Logging là cơ chế ghi lại thông tin của các request và hoạt động diễn ra
trên hệ thống.

StudyDrive thực hiện Structured Request Logging tại Middleware
`app/middleware/request_logging.py` bằng hook `after_request`. Mỗi
request được ghi nhận với các trường như `timestamp`, `user_id`,
`session_id_hash`, `endpoint`, `action_type`, `resource_id`,
`authorization_result`, `status_code` và `response_time_ms`.

Cách ghi log tập trung tại Middleware giúp tránh việc chèn logic logging
thủ công vào từng route.

## 2.4. Bảo vệ thông tin trong log

Log có thể chứa các thông tin liên quan đến phiên và người dùng. Vì vậy
hệ thống không lưu password plaintext, CSRF token hoặc raw session
token.

Session ID được băm bằng SHA-256 và lưu dưới dạng `session_id_hash`. Nội
dung tệp tin của người dùng cũng không được ghi vào request log.

Ngoài ra, cơ chế logging được đặt trong `try...except` để lỗi ghi log
không làm gián đoạn request chính.

## 2.5. Hành vi bất thường và Business Logic Abuse

Trong đề tài, hành vi bất thường được xem xét ở cấp độ chuỗi hành động
thay vì chỉ kiểm tra một request đơn lẻ.

Ba nhóm hành vi chính là:

-   **Export Abuse:** tần suất export cao bất thường.
-   **Delete Abuse:** số lượng thao tác xóa và số tài nguyên bị tác động
    tăng bất thường.
-   **IDOR/BOLA Scan:** nhiều request đến các resource ID khác nhau và
    tạo chuỗi phản hồi 403/404.

Các hành vi này có thể sử dụng HTTP Request hợp lệ, vì vậy việc phân
tích đặc điểm hành vi theo thời gian có vai trò quan trọng.

## 2.6. Machine Learning trong phát hiện bất thường

Machine Learning được sử dụng trong đề tài để phân tích vector đặc trưng
được tạo từ request log. Mục tiêu không phải xử lý trực tiếp toàn bộ
request thô bằng mô hình mà là chuyển chuỗi request thành các đặc trưng
định lượng.

Pipeline gồm:

``` text
Request Logs
    ↓
5-minute Window
    ↓
25 Features
    ↓
Isolation Forest
    ↓
Anomaly Score
    ↓
Normal / Anomaly
```

## 2.7. Học không giám sát và Normal-only Training

Dữ liệu huấn luyện của mô hình chỉ gồm các cửa sổ hành vi bình thường.
Cách tiếp cận này phù hợp với mục tiêu học phân bố hành vi bình thường
thay vì yêu cầu số lượng lớn nhãn tấn công.

Dữ liệu Validation và Test có cả Normal và Anomaly để phục vụ tuning và
đánh giá.

## 2.8. Isolation Forest

Isolation Forest là mô hình được sử dụng trong hệ thống thông qua
`sklearn.ensemble.IsolationForest`.

Ý tưởng của mô hình là sử dụng các cây ngẫu nhiên để cô lập các mẫu dữ
liệu. Các mẫu có đặc điểm khác biệt thường được cô lập nhanh hơn so với
các mẫu nằm trong vùng hành vi phổ biến.

Trong đồ án, Isolation Forest được sử dụng để tính điểm `score_samples`,
sau đó chuyển điểm thành `anomaly_score` và so sánh với threshold để xác
định nhãn.

## 2.9. Threshold

Hệ thống sử dụng percentile của điểm trên tập huấn luyện để xác định
threshold. Các mức percentile được khảo sát gồm 90.0%, 92.5%, 95.0% và
97.5%.

Cấu hình thực tế có threshold percentile 90.0%/95.0%, với threshold
score được ghi nhận xấp xỉ 0.4866.

Theo quy tắc triển khai của hệ thống:

``` text
anomaly_score >= threshold
        ↓
    Anomaly = 1

anomaly_score < threshold
        ↓
    Normal = 0
```

## 2.10. Feature Engineering

Hai mươi lăm đặc trưng được chia thành các nhóm:

-   Quy mô và tốc độ request.
-   Đặc trưng session.
-   Đặc trưng request nhạy cảm.
-   Đặc trưng Export.
-   Đặc trưng Delete.
-   Đặc trưng resource ID.
-   Đặc trưng lỗi 403/404.
-   Đặc trưng chuỗi thao tác.

Các đặc trưng được xây dựng từ log trong cửa sổ 5 phút.

## 2.11. Chống rò rỉ dữ liệu

Dữ liệu được chia theo Group Key `(run_id, session_id_hash)`. Toàn bộ
cửa sổ thuộc cùng một đợt mô phỏng được giữ trong cùng một tập.

Cách chia này nhằm tránh trường hợp các cửa sổ có nguồn gốc từ cùng một
phiên hoặc cùng một lần mô phỏng xuất hiện đồng thời trong Train và
Test, từ đó hạn chế đánh giá quá lạc quan.

## 2.12. Các chỉ số đánh giá

Đồ án sử dụng Accuracy, Precision, Recall, F1-Score và False Positive
Rate (FPR). Confusion Matrix được dùng để phân tích TN, FP, FN và TP.

Công thức tính các chỉ số:

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

$$\text{Precision} = \frac{TP}{TP + FP}$$

$$\text{Recall} = \frac{TP}{TP + FN}$$

$$\text{F1-Score} = \frac{2 \times \text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

$$\text{FPR} = \frac{FP}{FP + TN}$$

Trong đó:

-   **TP (True Positive):** Cửa sổ bất thường được phát hiện đúng.
-   **TN (True Negative):** Cửa sổ bình thường được phân loại đúng.
-   **FP (False Positive):** Cửa sổ bình thường bị cảnh báo nhầm.
-   **FN (False Negative):** Cửa sổ bất thường không được phát hiện.

## 2.13. Tiểu kết chương

Chương 2 đã trình bày các cơ sở cần thiết để xây dựng hệ thống, từ ứng
dụng web, xác thực và phân quyền, logging, hành vi bất thường đến
Machine Learning và Isolation Forest. Đặc biệt, chương làm rõ vai trò
của Feature Engineering, cửa sổ thời gian và Group-aware Split trong
pipeline phát hiện bất thường.

------------------------------------------------------------------------

# CHƯƠNG 3. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

## 3.1. Mô tả hệ thống

StudyDrive là ứng dụng web lưu trữ và chia sẻ tệp tin trực tuyến. Hệ
thống cung cấp chức năng cho người dùng và quản trị viên, đồng thời tích
hợp pipeline phát hiện hành vi bất thường.

Hệ thống được thiết kế theo hướng dữ liệu phát hiện đi từ request log
đến Machine Learning và quay trở lại giao diện quản trị dưới dạng Alert.

## 3.2. Yêu cầu chức năng

### 3.2.1. Đối với User

-   Đăng ký, đăng nhập và đăng xuất.
-   Quản lý thư mục.
-   Upload và quản lý tệp.
-   Xem, tìm kiếm, lọc và phân trang.
-   Download.
-   Chia sẻ tệp với quyền Viewer.
-   Export dữ liệu.
-   Xóa, khôi phục và xóa vĩnh viễn tệp.

### 3.2.2. Đối với Admin

-   Xem thống kê.
-   Quản lý tài khoản.
-   Xem metadata tệp.
-   Tra cứu và lọc request log.
-   Export log.
-   Chạy Detection.
-   Xem và quản lý Alert.
-   Truy ngược từ Alert đến log gốc.

## 3.3. Yêu cầu phi chức năng

-   Logging phải được thực hiện tự động tại Middleware.
-   Thông tin nhạy cảm không được lưu plaintext.
-   Hệ thống ML phải có pipeline xử lý dữ liệu rõ ràng.
-   Dữ liệu phải được chia theo Group Key để hạn chế leakage.
-   Hệ thống phải có kiểm thử tự động.
-   Detection hiện tại không yêu cầu realtime.

## 3.4. Kiến trúc tổng thể

``` text
+----------------------+
| User / Attacker      |
+----------+-----------+
           |
           v
+----------------------+
| Flask Routes         |
| Authentication       |
| Authorization        |
+----------+-----------+
           |
           v
+----------------------+
| Business Logic       |
| File / Export /      |
| Delete / Share       |
+----------+-----------+
           |
           v
+----------------------+
| Middleware           |
| Structured Logging   |
+----------+-----------+
           |
           v
+----------------------+
| request_logs         |
+----------+-----------+
           |
           v
+----------------------+
| Feature Engineering  |
| 5-minute Windows     |
| 25 Features          |
+----------+-----------+
           |
           v
+----------------------+
| Isolation Forest     |
+----------+-----------+
           |
           v
+----------------------+
| alerts               |
+----------+-----------+
           |
           v
+----------------------+
| Admin Alerts         |
| Dashboard            |
+----------------------+
```

## 3.5. Thiết kế cơ sở dữ liệu

Hệ thống gồm 7 bảng:

  Bảng             Vai trò
  ---------------- ------------------------------------------------
  `users`          Tài khoản, mật khẩu băm, vai trò và trạng thái
  `folders`        Cây thư mục
  `stored_files`   Metadata tệp
  `file_shares`    Chia sẻ tệp
  `export_jobs`    Lịch sử export
  `request_logs`   Nhật ký truy cập
  `alerts`         Cảnh báo từ ML

Hai bảng trung tâm của pipeline ML là `request_logs` và `alerts`.

## 3.6. Thiết kế Request Log

Một bản ghi log gồm các trường chính:

``` text
request_id          -- ID duy nhất của request
timestamp           -- Thời điểm ghi log (UTC)
user_id             -- ID người dùng
is_authenticated    -- Trạng thái xác thực
role                -- Vai trò (USER / ADMIN)
session_id_hash     -- SHA-256 của session token
http_method         -- Phương thức HTTP
endpoint            -- Tên endpoint Flask
path                -- Đường dẫn URL
action              -- Tên hành động
action_type         -- Loại hành động (export, delete...)
is_sensitive        -- Đánh dấu thao tác nhạy cảm
resource_type       -- Loại tài nguyên
resource_id         -- ID tài nguyên
ownership_result    -- Kết quả kiểm tra sở hữu
authorization_result-- Kết quả phân quyền
status_code         -- HTTP status code
response_time_ms    -- Thời gian phản hồi (ms)
```

## 3.7. Thiết kế Alert

Một Alert gồm:

``` text
id
created_at
user_id
session_id_hash
window_start
window_end
anomaly_score
scenario_hint
status
feature_vector_json
```

Alert liên kết với cửa sổ phát hiện để Admin có thể truy ngược về
request log.

## 3.8. Thiết kế Feature Engineering

Request log được lọc bỏ các request tĩnh `static/` và health check. Sau
đó dữ liệu được nhóm theo `(user_id, session_id_hash)` trong cửa sổ 5
phút.

Vector đầu ra gồm 25 đặc trưng:

1.  `request_count`
2.  `unique_endpoint_count`
3.  `unique_method_count`
4.  `session_duration_sec`
5.  `avg_inter_request_sec`
6.  `min_inter_request_sec`
7.  `burst_rate`
8.  `error_rate`
9.  `avg_response_time_ms`
10. `sensitive_request_count`
11. `sensitive_ratio`
12. `export_count`
13. `export_ratio`
14. `delete_count`
15. `delete_ratio`
16. `unique_deleted_resource_count`
17. `unique_resource_id_count`
18. `resource_id_request_ratio`
19. `forbidden_count`
20. `forbidden_rate`
21. `not_found_count`
22. `not_found_rate`
23. `unique_failed_resource_id_count`
24. `resource_id_change_rate`
25. `max_sensitive_streak`

## 3.9. Thiết kế Detection

Detection được kích hoạt khi Admin chọn `Run Detection` hoặc chạy
script.

``` text
Admin
 ↓
Run Detection
 ↓
Query request_logs
 ↓
Build 5-minute windows
 ↓
Create 25D features
 ↓
Load model.joblib
 ↓
Calculate score
 ↓
Compare threshold
 ↓
Create Alert
 ↓
Admin reviews
```

## 3.10. Thiết kế truy vết

Alert lưu `user_id`, `session_id_hash`, `window_start` và `window_end`.
Các thông tin này cho phép giao diện quản trị lọc request log thuộc đúng
cửa sổ đã phát hiện.

Cơ chế này giúp chuyển từ kết quả ML sang dữ liệu gốc để Admin kiểm tra
nguyên nhân của cảnh báo.

## 3.11. Tiểu kết chương

Chương 3 đã phân tích yêu cầu và thiết kế kiến trúc của StudyDrive, cơ
sở dữ liệu, logging, Feature Engineering, Detection và Alert. Thiết kế
tập trung vào việc tạo một pipeline khép kín từ request log đến cảnh báo
và truy vết log gốc.

------------------------------------------------------------------------

# CHƯƠNG 4. XÂY DỰNG HỆ THỐNG VÀ PIPELINE MACHINE LEARNING

## 4.1. Môi trường và công nghệ

Hệ thống sử dụng:

-   Python 3.11+.
-   Flask 3.x.
-   Werkzeug.
-   Flask-SQLAlchemy.
-   MySQL với PyMySQL; SQLite được sử dụng cho Dev và Unit Test local.
-   HTML5, Jinja2, Bootstrap 5 và Custom CSS.
-   Pandas, NumPy, Scikit-Learn và Joblib.
-   Pytest, Pytest-Flask và Requests.
-   Git.

## 4.2. Xây dựng ứng dụng StudyDrive

Ứng dụng được tổ chức thành các Blueprint cho Auth, Documents, Admin,
Alerts và Main. Các model dữ liệu được đặt trong `app/models`, các
nghiệp vụ được tổ chức trong `app/services`, Middleware logging được đặt
trong `app/middleware`.

Cấu trúc chính:

``` text
app/
├── blueprints/
├── models/
├── services/
├── middleware/
├── templates/
└── static/
```

## 4.3. Xây dựng cơ chế logging

Middleware `request_logging.py` sử dụng `after_request` để thu thập
metadata của request sau khi xử lý.

Session ID không được lưu trực tiếp mà được băm SHA-256. Các trường nhạy
cảm như password, CSRF token và raw session token không được ghi.

Logging được xử lý trong `try...except`, bảo đảm lỗi ghi log không làm
request chính thất bại.

## 4.4. Xây dựng dữ liệu giả lập

Bốn script mô phỏng dữ liệu:

``` text
simulate_normal.py
simulate_export_abuse.py
simulate_delete_abuse.py
simulate_bola_scan.py
```

Hành vi Normal mô phỏng chuỗi đăng nhập, duyệt thư mục, xem file,
download một số file và đăng xuất.

Các script còn lại tạo ra ba nhóm hành vi bất thường.

## 4.5. Xây dựng Ground Truth

`generate_raw_dataset_v1.py` tạo nhãn dựa trên `run_id`,
`scenario_name`, thời gian bắt đầu/kết thúc và cặp
`(user_id, session_id_hash)`.

Nhãn sử dụng:

``` text
0 = Normal
1 = Anomaly
```

## 4.6. Xây dựng Feature Engineering

Module `ml/build_features.py` thực hiện:

1.  Đọc log.
2.  Lọc request không cần thiết.
3.  Chuẩn hóa dữ liệu.
4.  Gom nhóm theo user/session.
5.  Tạo cửa sổ 5 phút.
6.  Tính 25 đặc trưng.
7.  Xuất dữ liệu feature.

Các phép chia có thể dẫn đến mẫu số bằng 0 được xử lý bằng giá trị mặc
định `0.0`.

## 4.7. Xây dựng tập dữ liệu

Dữ liệu thô gồm 5.567 log. Sau quá trình gom nhóm thu được 24 cửa sổ.

Các file dữ liệu chính:

``` text
data/raw/request_logs_raw.csv
ground_truth.csv
features_all.csv
train_features.csv
validation_features.csv
test_features.csv
```

## 4.8. Huấn luyện Isolation Forest

Model được triển khai bằng:

``` text
sklearn.ensemble.IsolationForest
```

Cấu hình baseline mặc định:

``` text
n_estimators = 200
max_samples  = 'auto'
contamination = 'auto'
random_state = 20260706
```

Dữ liệu Train chỉ gồm cửa sổ Normal.

Model được đóng gói tại:

``` text
artifacts/models/iforest_v1/model.joblib
```

## 4.9. Tuning

Pipeline hỗ trợ tuning:

``` text
n_estimators:
100, 200, 300

max_samples:
auto, 256

threshold_percentile:
90.0, 92.5, 95.0, 97.5
```

Việc tuning được thực hiện trên Validation.

## 4.10. Triển khai Detection

Module `detection_service.py` chịu trách nhiệm:

-   Truy vấn request log.
-   Xây dựng feature.
-   Load model.
-   Tính điểm.
-   So sánh threshold.
-   Tạo Alert.

Chức năng này được gọi từ Admin UI hoặc script:

``` text
python -m scripts.run_detection
```

## 4.11. Tích hợp Alerts Dashboard

Dashboard hiển thị:

-   Thời điểm cảnh báo.
-   User.
-   Anomaly score.
-   Scenario hint.
-   Trạng thái.
-   Vector đặc trưng.
-   Link truy ngược request log.

Các trạng thái Alert gồm:

``` text
Pending
Investigating
Resolved
Ignored
```

## 4.12. Tiểu kết chương

Chương 4 đã trình bày quá trình xây dựng ứng dụng StudyDrive, cơ chế
logging, dữ liệu giả lập, Feature Engineering, huấn luyện Isolation
Forest và tích hợp Detection vào hệ thống web.

------------------------------------------------------------------------

# CHƯƠNG 5. THỰC NGHIỆM VÀ ĐÁNH GIÁ MÔ HÌNH

## 5.1. Mục tiêu thực nghiệm

Thực nghiệm nhằm kiểm tra khả năng của pipeline Machine Learning trong
việc phân biệt các cửa sổ hành vi bình thường và bất thường, đồng thời
đánh giá khả năng phát hiện ba scenario được xây dựng.

## 5.2. Dữ liệu thực nghiệm

Dữ liệu gồm:

-   5.567 request log thô.
-   24 cửa sổ 5 phút.
-   Ba scenario bất thường.
-   Các cửa sổ Normal dùng để mô hình học phân bố hành vi bình thường.

## 5.3. Thiết kế chia dữ liệu

Dữ liệu được chia:

  Tập            Tỷ lệ Nội dung
  ------------ ------- ------------------
  Train            60% Normal-only
  Validation       20% Normal + Anomaly
  Test             20% Normal + Anomaly

Việc chia được thực hiện theo `(run_id, session_id_hash)`.

Mục tiêu là bảo đảm các cửa sổ thuộc cùng một đợt mô phỏng không bị chia
sang nhiều tập.

## 5.4. Các nhóm đặc trưng

### 5.4.1. Export Abuse

Các đặc trưng quan trọng:

-   `export_count`
-   `export_ratio`
-   `sensitive_request_count`
-   `avg_inter_request_sec`

Những đặc trưng này mô tả tần suất và tốc độ của thao tác export.

### 5.4.2. Delete Abuse

Các đặc trưng:

-   `delete_count`
-   `delete_ratio`
-   `unique_deleted_resource_count`

Nhóm đặc trưng phản ánh mức độ và phạm vi thao tác xóa.

### 5.4.3. IDOR/BOLA Scan

Các đặc trưng:

-   `unique_resource_id_count`
-   `forbidden_count`
-   `forbidden_rate`
-   `not_found_count`
-   `not_found_rate`
-   `unique_failed_resource_id_count`
-   `resource_id_change_rate`

Nhóm đặc trưng phản ánh việc thay đổi resource ID và chuỗi truy cập thất
bại.

## 5.5. Kết quả thực nghiệm

Kết quả trên Test Set:

  Chỉ số        Giá trị
  ----------- ---------
  Accuracy       66.67%
  Precision      66.67%
  Recall         66.67%
  F1-Score       66.67%
  FPR            33.33%

Confusion Matrix:

                     Predicted Normal   Predicted Anomaly
  ---------------- ------------------ -------------------
  Actual Normal                TN = 2              FP = 1
  Actual Anomaly               FN = 1              TP = 2

## 5.6. Phân tích kết quả

Kết quả cho thấy mô hình có khả năng phát hiện một phần các hành vi bất
thường trong tập thử nghiệm. Hai cửa sổ Export Abuse được phát hiện
chính xác.

Một cửa sổ Normal có tốc độ thao tác nhanh bị đánh dấu nhầm thành
Anomaly. Điều này thể hiện vấn đề False Positive đối với hành vi người
dùng hợp lệ nhưng có cường độ cao.

Một cửa sổ BOLA Scan có quy mô mẫu nhỏ chưa được phát hiện, tạo ra False
Negative. Điều này cho thấy lượng dữ liệu và kích thước mẫu thực nghiệm
hiện tại còn hạn chế đối với các hành vi có cường độ thấp.

## 5.7. Đánh giá theo mục tiêu

  Mục tiêu               Kết quả
  ---------------------- -----------------------------
  Thu thập log tự động   Đạt
  Xây dựng 25 feature    Đạt
  Normal-only training   Đạt
  Group-aware split      Đạt
  Isolation Forest       Đạt
  Detection              Đạt
  Alert Dashboard        Đạt
  Truy vết log           Đạt
  Đánh giá định lượng    Đạt
  Real-time detection    Chưa thuộc phạm vi hiện tại

## 5.8. Hạn chế của thực nghiệm

Tập Test hiện tại chỉ có số lượng cửa sổ nhỏ. Do đó các chỉ số 66.67%
phản ánh kết quả của bộ dữ liệu thực nghiệm hiện tại và không nên được
diễn giải như khả năng tổng quát trên mọi môi trường web.

FPR khoảng 33.33% cho thấy mô hình còn có thể phát cảnh báo nhầm đối với
người dùng thao tác nhanh.

Hệ thống hiện tại cũng chưa thực hiện Detection theo thời gian thực.

## 5.9. Tiểu kết chương

Chương 5 đã trình bày thiết kế thực nghiệm, cách chia dữ liệu, các nhóm
đặc trưng và kết quả đánh giá Isolation Forest. Kết quả cho thấy
pipeline có khả năng phát hiện các mẫu bất thường trong dữ liệu thử
nghiệm, đồng thời chỉ ra các hạn chế về kích thước Test Set, False
Positive và khả năng phát hiện các mẫu BOLA có quy mô nhỏ.

------------------------------------------------------------------------

# CHƯƠNG 6. KIỂM THỬ VÀ TÍCH HỢP HỆ THỐNG

## 6.1. Mục tiêu kiểm thử

Kiểm thử nhằm xác nhận các chức năng chính của ứng dụng, Middleware
logging, pipeline Machine Learning và giao diện quản trị hoạt động đúng
theo thiết kế.

## 6.2. Công cụ kiểm thử

Hệ thống sử dụng:

-   Pytest.
-   Pytest-Flask.
-   Requests.

Tổng cộng có **34 test cases**, phân bổ trong 6 file kiểm thử.

## 6.3. Kiểm thử giao diện và routing

`test_health.py` và `test_blueprints.py` gồm 6 test:

-   Health endpoint trả về HTTP 200.
-   Trang chủ sử dụng base layout.
-   Navbar hiển thị đúng theo vai trò (USER/ADMIN).
-   Custom 404 handler hoạt động đúng.
-   Blueprint được đăng ký đủ và đúng tên.
-   Route công khai và route được bảo vệ đều có thể truy cập.

## 6.4. Kiểm thử quản lý tài liệu

`test_documents.py` gồm 13 test:

-   Tạo thư mục và upload tệp hợp lệ.
-   Từ chối tệp vượt giới hạn 20 MB mà không để lại file rác.
-   Từ chối phần mở rộng tệp bị cấm.
-   Ngăn upload vào thư mục của người dùng khác.
-   Làm sạch tên tệp đặc biệt, không cho thoát khỏi thư mục upload.
-   Từ chối MIME type hoặc file signature không khớp.
-   Xóa file vật lý khi gặp lỗi cơ sở dữ liệu.
-   Tìm kiếm, lọc, sắp xếp, phân trang và cô lập dữ liệu giữa user.
-   Owner xem/download và API ẩn metadata lưu trữ.
-   Viewer chỉ xem/download; người không có quyền nhận 404.
-   Xóa mềm, thùng rác, khôi phục và tệp bị xóa không truy cập được.
-   Chia sẻ, thu hồi và thay đổi quyền có hiệu lực ngay lập tức.
-   Xóa mềm lặp lại là idempotent; xóa vĩnh viễn xóa file vật lý.

## 6.5. Kiểm thử Request Logging

`test_request_logging.py` gồm 8 test nhằm xác nhận:

-   Middleware ghi log có cấu trúc cho mọi request được xử lý.
-   Login thất bại không ghi password hay form body vào log.
-   Lỗi ghi log không làm request chính thất bại.
-   Log tệp có resource ID và thông tin owner context đúng.
-   Truy cập tệp không có quyền được đánh dấu `is_sensitive`.
-   Log thao tác xóa có `action_type` đúng và context nhạy cảm.
-   Request 404 được ghi với `authorization_result = DENIED`.
-   `request_id` là duy nhất và các trường boolean ổn định.

## 6.6. Kiểm thử Admin Log

`test_admin_logs.py` gồm 3 test:

-   Admin có thể lọc log và mở trang chi tiết.
-   Export CSV log áp dụng đúng bộ lọc hiện tại.
-   User thường bị chặn khỏi trang Admin Logs (trả về 403).

## 6.7. Kiểm thử luồng nghiệp vụ tích hợp

`test_web_freeze.py` gồm 4 test kiểm thử các luồng liên kết nhiều thành phần:

-   Export CSV có BOM, header `Content-Disposition` đúng và không lộ
    tệp của người dùng khác hoặc tệp đã xóa.
-   10 lần export liên tiếp tạo ra đúng 10 export job.
-   Xóa mềm, thùng rác, khôi phục và Viewer mất quyền truy cập.
-   Admin xem danh sách user, metadata tệp và có thể khóa tài khoản.

## 6.8. Kết quả kiểm thử

Kết quả thực thi:

``` text
34 passed in 17.87s
```

Tỷ lệ test pass:

``` text
100%
```

Kết quả cho thấy các test case được xây dựng đều vượt qua trong lần chạy
được ghi nhận.

## 6.9. Kiểm thử luồng tích hợp

Luồng tích hợp chính:

``` text
HTTP Request
    ↓
Middleware
    ↓
request_logs
    ↓
Run Detection
    ↓
Feature Engineering
    ↓
Isolation Forest
    ↓
Threshold
    ↓
Alert
    ↓
Alerts Dashboard
    ↓
Original Request Logs
```

Điểm quan trọng của hệ thống là kết quả ML không dừng ở một file kết quả
offline. Alert được lưu trong CSDL và hiển thị trên giao diện quản trị.

## 6.10. Kiểm thử truy vết

Khi Admin xem một Alert, hệ thống cung cấp thông tin về user/session và
cửa sổ thời gian. Từ đó Admin có thể truy ngược về danh sách request log
thuộc cửa sổ 5 phút được phát hiện.

Cơ chế này hỗ trợ quá trình kiểm tra nguyên nhân của cảnh báo và đối
chiếu giữa kết quả Machine Learning với request thực tế.

## 6.11. Tiểu kết chương

Chương 6 đã trình bày chiến lược kiểm thử và kết quả thực thi của 38
test cases. Bên cạnh kiểm thử từng phân hệ, chương cũng mô tả luồng tích
hợp từ request log đến ML Alert và khả năng truy vết về dữ liệu gốc.

------------------------------------------------------------------------

# CHƯƠNG 7. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 7.1. Kết luận

Đồ án đã xây dựng được một hệ thống StudyDrive có tích hợp cơ chế phát
hiện hành vi truy cập bất thường bằng Machine Learning.

Về phía ứng dụng web, hệ thống đã hoàn thành các chức năng lưu trữ và
chia sẻ tệp, xác thực, phân quyền, quản lý thư mục, export, thùng rác và
các chức năng quản trị.

Về phía giám sát, hệ thống đã xây dựng Structured Request Logging tại
Middleware. Log được thu thập tự động và bảo vệ thông tin nhạy cảm bằng
cách không lưu password, CSRF token và raw session token; Session ID
được băm SHA-256.

Về phía Machine Learning, hệ thống đã xây dựng pipeline từ request log
đến cửa sổ 5 phút và vector 25 đặc trưng. Mô hình Isolation Forest được
huấn luyện trên hành vi bình thường và sử dụng threshold percentile để
xác định mẫu bất thường.

Ba kịch bản được nghiên cứu là Export Abuse, Delete Abuse và IDOR/BOLA
Scan. Kết quả Detection được tích hợp trở lại Web Admin thông qua Alerts
Dashboard, cho phép xem điểm bất thường, scenario hint, vector đặc trưng
và truy ngược về request log gốc.

Thực nghiệm trên Test Set cho kết quả Accuracy, Precision, Recall và
F1-Score đều đạt 66.67%, FPR đạt 33.33%. Bộ kiểm thử tự động gồm 38 test
cases và toàn bộ test đều vượt qua.

Như vậy, mục tiêu xây dựng một pipeline phát hiện bất thường tích hợp
trực tiếp với ứng dụng web đã được triển khai. Tuy nhiên, kết quả thực
nghiệm hiện tại vẫn cần được xem xét trong phạm vi dữ liệu thử nghiệm
nhỏ.

## 7.2. Những hạn chế

### 7.2.1. Hạn chế về dữ liệu

Số lượng cửa sổ Test còn nhỏ. Điều này hạn chế khả năng đánh giá mức độ
tổng quát của mô hình trên các hành vi và người dùng khác nhau.

### 7.2.2. Hạn chế về thời gian phát hiện

Detection hiện tại sử dụng Batch Processing với cửa sổ 5 phút không
chồng lấp. Hệ thống chưa phát hiện bất thường theo thời gian thực.

### 7.2.3. Hạn chế về False Positive

FPR trong Test Set đạt khoảng 33.33%. Một nguyên nhân được ghi nhận là
người dùng hợp lệ có thể thao tác với tốc độ cao và tạo đặc trưng gần
với hành vi bất thường.

### 7.2.4. Hạn chế về phản ứng

Khi phát hiện bất thường, hệ thống mới tạo cảnh báo để Admin rà soát.
Chưa có cơ chế tự động khóa tài khoản hoặc chặn IP.

## 7.3. Hướng phát triển

### 7.3.1. Phát hiện thời gian thực

Có thể chuyển pipeline từ Batch Processing sang Data Pipeline Real-time
Streaming, với các công nghệ được đề xuất trong phạm vi dự án như Apache
Kafka hoặc Celery.

### 7.3.2. Mở rộng mô hình

Có thể nghiên cứu kết hợp Isolation Forest với Autoencoder để đánh giá
khả năng cải thiện Detection.

### 7.3.3. Mở rộng scenario

Có thể bổ sung các kịch bản lạm dụng logic nghiệp vụ khác để tăng phạm
vi phát hiện.

### 7.3.4. Tự động phản ứng

Có thể phát triển cơ chế Auto-blocking đối với IP hoặc tài khoản khi mức
độ cảnh báo đạt điều kiện xác định.

### 7.3.5. Mở rộng dữ liệu đánh giá

Có thể tăng số lượng phiên, người dùng, cửa sổ thời gian và mức độ đa
dạng của hành vi để đánh giá mô hình đáng tin cậy hơn.

## 7.4. Tiểu kết chương

Chương 7 đã tổng kết kết quả xây dựng hệ thống, kết quả thực nghiệm và
các hạn chế hiện tại. Đồ án đã hình thành được quy trình từ thu thập
request log, xây dựng đặc trưng, phát hiện bằng Isolation Forest đến tạo
Alert và truy vết log. Các hướng phát triển tập trung vào Detection thời
gian thực, mở rộng dữ liệu và scenario, cải thiện mô hình và bổ sung cơ
chế phản ứng tự động.
