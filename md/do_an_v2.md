# XÂY DỰNG HỆ THỐNG PHÁT HIỆN HÀNH VI TRUY CẬP BẤT THƯỜNG TRÊN ỨNG DỤNG WEB BẰNG MACHINE LEARNING

---

# CHƯƠNG 1: TỔNG QUAN

## 1.1. Lý do chọn đề tài

Trong bối cảnh chuyển đổi số mạnh mẽ, các ứng dụng web lưu trữ và chia sẻ tài liệu trực tuyến (như StudyDrive) trở thành công cụ quan trọng trong học tập và làm việc. Người dùng thực hiện liên tục các thao tác như xem, tải xuống, xuất dữ liệu và quản lý tệp thông qua các HTTP Request. Tuy nhiên, rủi ro an ninh mạng ở tầng ứng dụng (Application Layer) ngày càng phức tạp, đặc biệt là nhóm nguy cơ **Lạm dụng logic nghiệp vụ (Business Logic Abuse)** và các lỗ hổng liên quan đến **Kiểm soát truy cập đối tượng (BOLA/IDOR)**.

Các hành vi tấn công logic (như xuất dữ liệu hàng loạt, xóa tệp liên tục hoặc dò quét ID tài nguyên trái phép) thường sử dụng các HTTP Request hoàn toàn hợp lệ về mặt cú pháp. Do đó, các giải pháp bảo vệ truyền thống như WAF (Web Application Firewall) dựa trên luật tĩnh (static rules) rất khó phát hiện.

Đề tài được thực hiện nhằm giải quyết bài toán trên bằng cách ứng dụng thuật toán học máy không giám sát **Isolation Forest** để phân tích nhật ký truy cập (request log) thu thập tự động từ tầng Flask Middleware của ứng dụng StudyDrive. Dữ liệu truy cập được gom nhóm theo cửa sổ thời gian 5 phút và chuyển đổi thành vector 25 đặc trưng số để học phân bố hành vi bình thường và phát hiện kịp thời các truy cập bất thường.

## 1.2. Mục tiêu nghiên cứu

### 1.2.1. Mục tiêu tổng quát
Xây dựng thành công ứng dụng web StudyDrive tích hợp hệ thống phát hiện hành vi truy cập bất thường dựa trên mô hình Machine Learning không giám sát (Isolation Forest), hỗ trợ quản trị viên phát hiện sớm các nguy cơ lạm dụng logic nghiệp vụ và truy vết trực tiếp về bản ghi log gốc.

### 1.2.2. Mục tiêu cụ thể
- Triển khai ứng dụng web StudyDrive hỗ trợ các chức năng quản lý tệp, chia sẻ, xuất dữ liệu và phân quyền tài nguyên (`OWNER`, `VIEWER`, `NONE`).
- Tích hợp Middleware ghi log tự động tại tầng ứng dụng (`after_request`), áp dụng giải pháp băm SHA-256 đối với Session ID để bảo mật thông tin phiên.
- Xây dựng công cụ giả lập hành vi người dùng bình thường và 3 kịch bản tấn công: Export Abuse, Delete Abuse và IDOR/BOLA Scan.
- Thiết kế quy trình trích xuất vector 25 đặc trưng số từ các cửa sổ thời gian 5 phút.
- Huấn luyện mô hình Isolation Forest theo chiến lược Normal-only Training và áp dụng kỹ thuật Group-aware Split để chống rò rỉ dữ liệu (Data Leakage).
- Đánh giá định lượng hiệu năng mô hình qua các chỉ số Accuracy, Precision, Recall, F1-Score, FPR và Confusion Matrix.
- Tích hợp dịch vụ Detection và giao diện Alerts Dashboard trên Web Admin cho phép quản trị viên xem cảnh báo và truy vết về log thô trong cửa sổ 5 phút.

## 1.3. Đối tượng & Phạm vi nghiên cứu

### 1.3.1. Đối tượng nghiên cứu
- Các bản ghi HTTP Request Log thu thập tại tầng ứng dụng web StudyDrive.
- Chuỗi hành vi truy cập của người dùng được biểu diễn qua vector đặc trưng định lượng trong cửa sổ thời gian 5 phút.
- Thuật toán phát hiện bất thường không giám sát Isolation Forest và quy trình xử lý dữ liệu chuỗi thời gian (time-window feature engineering).

### 1.3.2. Phạm vi nghiên cứu
- **Phạm vi kịch bản phát hiện:** Tập trung vào 3 kịch bản lạm dụng logic nghiệp vụ chính:
  1. *Export Abuse:* Gửi từ 30–50 request export CSV/ZIP liên tục trong 5 phút.
  2. *Delete Abuse:* Gửi liên tục khoảng 30 request xóa tệp hàng loạt trong 5 phút.
  3. *IDOR/BOLA Scan:* Gửi từ 100–500 request truy cập các `file_id` tăng dần không thuộc quyền sở hữu, tạo ra chuỗi phản hồi lỗi 403 (Forbidden) và 404 (Not Found).
- **Phạm vi kỹ thuật:** Mô hình xử lý theo cơ chế **Batch Processing** (định kỳ chạy phân tích trên tập log gom nhóm 5 phút), chưa triển khai xử lý luồng theo thời gian thực (Real-time Streaming). Hệ thống thực hiện phát cảnh báo (Alert Generation) để Admin kiểm tra thủ công, chưa tự động kích hoạt cơ chế chặn IP hay khóa tài khoản.

## 1.4. Phương pháp nghiên cứu
1. **Nghiên cứu lý thuyết:** Phân tích tài liệu OWASP API Security Top 10 (đặc biệt là lỗ hổng BOLA/IDOR), nguyên lý của thuật toán Isolation Forest và kỹ thuật Feature Engineering trên dữ liệu log web.
2. **Thực nghiệm xây dựng phần mềm:** Phát triển ứng dụng StudyDrive bằng Flask, SQLAlchemy, Jinja2 và Bootstrap 5.
3. **Thực nghiệm giả lập & thu thập dữ liệu:** Sử dụng thư viện `requests` của Python để tạo các kịch bản mô phỏng truy cập hợp lệ và bất thường, thu thập 5.567 bản ghi log thô.
4. **Phân tích & Huấn luyện:** Tiền xử lý dữ liệu, trích xuất 25 đặc trưng số, thực hiện Group-aware Split theo `run_id`, huấn luyện mô hình Isolation Forest trên tập Train chỉ gồm hành vi bình thường và tinh chỉnh siêu tham số (Hyperparameter Tuning) trên tập Validation.
5. **Đánh giá & Tích hợp:** Kiểm thử định lượng mô hình trên tập Test và xây dựng bộ kiểm thử tự động với Pytest (34 test cases).

## 1.5. Cấu trúc đồ án
Đồ án được tổ chức thành 6 chương:
- **Chương 1: Tổng quan** — Trình bày lý do chọn đề tài, mục tiêu, đối tượng, phạm vi, phương pháp nghiên cứu và cấu trúc báo cáo.
- **Chương 2: Cơ sở lý thuyết** — Tổng quan về logging tầng ứng dụng, Business Logic Abuse, BOLA/IDOR, khái niệm cửa sổ thời gian, Normal-only Training, thuật toán Isolation Forest, Feature Engineering, Data Leakage và các chỉ số đánh giá.
- **Chương 3: Thu thập dữ liệu và Xây dựng đặc trưng** — Chi tiết môi trường thực nghiệm, cấu trúc request log thô, 4 kịch bản giả lập hành vi, tiền xử lý dữ liệu và danh sách 25 đặc trưng số được chia thành 3 nhóm.
- **Chương 4: Huấn luyện mô hình và Đánh giá kết quả** — Thiết kế chia tập Train/Validation/Test, quá trình tinh chỉnh siêu tham số, kết quả đánh giá định lượng, phân tích trực quan và các hạn chế.
- **Chương 5: Triển khai hệ thống và Kiến trúc tích hợp** — Mô tả luồng xử lý toàn hệ thống (Pipeline), cơ chế phát hiện tự động, giao diện quản trị Alerts Dashboard và khả năng truy vết log gốc.
- **Chương 6: Kết luận và Hướng phát triển** — Tổng kết kết quả đạt được, các hạn chế còn tồn tại và đề xuất hướng nâng cấp trong tương lai.

---

# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

## 2.1. Logging tại tầng ứng dụng

### Structured Request Logging
Logging là nền tảng cho công tác giám sát an toàn thông tin. Khác với Unstructured Logging (ghi chuỗi văn bản tự do), **Structured Request Logging** ghi nhận thông tin truy cập dưới dạng các bản ghi có cấu trúc gồm các trường định sẵn (`timestamp`, `user_id`, `endpoint`, `status_code`, `response_time_ms`...). Dữ liệu log cấu trúc cho phép các thuật toán Machine Learning đọc và trích xuất đặc trưng tự động mà không cần qua các bước bóc tách cú pháp (parsing) phức tạp.

Trong Flask Framework, logging tại tầng ứng dụng được thực hiện thông qua hook `@app.after_request`. Cơ chế này cho phép bắt giữ toàn bộ thông tin của request và response ngay sau khi xử lý xong nghiệp vụ.

### Bảo mật thông tin nhạy cảm trong log
Log truy cập có thể trở thành mục tiêu tấn công nếu lưu trữ thông tin định danh nhạy cảm. Hệ thống áp dụng các nguyên tắc bảo mật:
- **Không ghi dữ liệu thô:** Mật khẩu plaintext, CSRF token và Session ID nguyên bản tuyệt đối không được ghi vào database log.
- **Băm SHA-256 cho Session ID:** Mã phiên làm việc được băm thông qua hàm SHA-256 (`session_id_hash`), đảm bảo tính ẩn danh và không thể khôi phục session ID gốc từ log.
- **Xử lý ngoại lệ an toàn:** Quá trình ghi log được bao bọc trong khối `try...except` để đảm bảo khi cơ sở dữ liệu log gặp sự cố, request của người dùng vẫn được phản hồi bình thường.

## 2.2. Hành vi bất thường và Business Logic Abuse

### 2.2.1. Định nghĩa và phân loại
Trong an toàn thông tin ứng dụng web, **Business Logic Abuse (Lạm dụng logic nghiệp vụ)** là loại hình tấn công mà kẻ tấn công sử dụng các chức năng hoàn toàn hợp lệ của ứng dụng theo những cách thức hoặc tần suất không được lường trước nhằm mục đích xấu (như thu thập dữ liệu trái phép, làm cạn kiệt tài nguyên hoặc thao tác dữ liệu hàng loạt).

Khác với các cuộc tấn công kỹ thuật thuần túy (như SQL Injection hay Cross-Site Scripting - XSS) vốn vi phạm cú pháp dữ liệu đầu vào, tấn công logic có cú pháp HTTP Request hoàn toàn đúng chuẩn.

### 2.2.2. Lỗ hổng BOLA/IDOR
Theo tài liệu **OWASP API Security Top 10 (2023)**, lỗ hổng **API1:2023 Broken Object Level Authorization (BOLA)** — hay còn gọi là **IDOR (Insecure Direct Object Reference)** — đứng vị trí số 1 về mức độ nguy hiểm. 

Lỗ hổng này xảy ra khi ứng dụng cung cấp tham chiếu trực tiếp đến đối tượng tài nguyên (như `file_id` hoặc `user_id`) trong đường dẫn URL nhưng không kiểm tra chặt chẽ quyền sở hữu ở phía máy chủ. Kẻ tấn công có thể thay đổi tuần tự ID (ví dụ: `/documents/view?file_id=101`, `102`, `103`...) để truy xuất trái phép dữ liệu của người dùng khác.

### 2.2.3. Hạn chế của phương pháp phát hiện truyền thống (WAF/IDS)
 các hệ thống phòng thủ truyền thống như WAF (Web Application Firewall) hoặc IDS (Intrusion Detection System) chủ yếu dựa trên các quy tắc tĩnh (Signature-based / Rule-based). Phương pháp này gặp các hạn chế lớn đối với Business Logic Abuse:
- **Không phát hiện được request hợp lệ:** WAF xem mỗi request riêng lẻ là hợp lệ vì không chứa mẫu mã độc (signature).
- **Dễ bị vượt qua ngưỡng tĩnh:** Kẻ tấn công chỉ cần giảm tốc độ truy cập để nằm dưới ngưỡng cảnh báo cố định.
- **Chi phí duy trì luật cao:** Phải cập nhật luật thủ công liên tục cho từng chức năng mới của ứng dụng.

## 2.3. Khái niệm Cửa sổ thời gian (Time Window) trong phân tích chuỗi hành vi
Hành vi của người dùng trên web là một chuỗi sự kiện có tính nối tiếp theo thời gian. Một request đơn lẻ không phản ánh được ý đồ của người dùng. 

Do đó, kỹ thuật **Cửa sổ thời gian (Time Windowing)** được sử dụng để gom nhóm toàn bộ các request xảy ra trong khoảng thời gian $\Delta t = 5$ phút của cùng một phiên người dùng `(user_id, session_id_hash)`. Việc phân tích trên cửa sổ 5 phút giúp:
- Tích lũy đủ dữ liệu để tính toán các chỉ số thống kê (tốc độ truy cập, tỷ lệ lỗi, độ đa dạng tài nguyên).
- Nhận diện rõ các mẫu hành vi đột biến (burst pattern) đặc trưng của công cụ tự động.

## 2.4. Học không giám sát và Normal-only Training
Trong bài toán phát hiện bất thường an ninh mạng, dữ liệu thực tế gặp phải hai thách thức:
1. Dữ liệu tấn công rất hiếm so với dữ liệu truy cập bình thường (mất cân bằng dữ liệu nghiêm trọng).
2. Các dạng tấn công logic mới xuất hiện liên tục và chưa có nhãn trước.

Do đó, đồ án lựa chọn hướng tiếp cận **Học không giám sát (Unsupervised Learning)** với chiến lược **Normal-only Training**. Mô hình chỉ được học trên tập dữ liệu gồm các cửa sổ hành vi bình thường. Qua đó, mô hình xây dựng ranh giới phân bố của "trạng thái bình thường". Khi gặp một cửa sổ mới có đặc trưng nằm ngoài phân bố này, mô hình sẽ đánh giá đó là cửa sổ bất thường.

## 2.5. Thuật toán Isolation Forest

### Cơ chế hoạt động
**Isolation Forest (iForest)** là thuật toán học máy không giám sát được thiết kế chuyên biệt cho bài toán phát hiện bất thường (Liu et al., 2008). Thuật toán dựa trên nguyên lý: *các điểm dữ liệu bất thường thường ít về số lượng và có giá trị đặc trưng khác biệt, do đó chúng dễ bị cô lập (isolate) hơn các điểm bình thường*.

Isolation Forest xây dựng một tập hợp các cây quyết định ngẫu nhiên (Isolation Trees). Tại mỗi nút của cây, thuật toán chọn ngẫu nhiên một đặc trưng $x_j$ và chọn một giá trị cắt ngẫu nhiên $p$ nằm trong khoảng $[\min(x_j), \max(x_j)]$. 

[Hình 2.1: Sơ đồ cô lập dữ liệu của thuật toán Isolation Forest]

Các điểm dữ liệu bình thường nằm trong vùng mật độ cao sẽ cần nhiều lần chia (chiều sâu cây lớn) mới bị cô lập, trong khi các điểm bất thường nằm ở vùng thưa thớt sẽ bị cô lập rất nhanh (chiều sâu cây nhỏ).

### Công thức tính Anomaly Score
Anomaly score $s(x, n)$ của mẫu dữ liệu $x$ đối với tập $n$ mẫu được định nghĩa theo công thức:

$$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$

Trong đó:
- $h(x)$ là chiều dài đường đi (path length) từ gốc đến nút lá của mẫu $x$ trên một cây.
- $E(h(x))$ là giá trị chiều dài đường đi trung bình của mẫu $x$ trên toàn bộ tập cây.
- $c(n)$ là chiều dài đường đi trung bình lý thuyết của cây tìm kiếm nhị phân không thành công tạo từ $n$ mẫu, tính bằng:

$$c(n) = 2 \left( \ln(n - 1) + 0.5772156649 \right) - \frac{2(n - 1)}{n}$$

- Nếu $E(h(x)) \to 0 \implies s \to 1$: Mẫu $x$ có chiều dài đường đi rất ngắn $\to$ Rất có khả năng là bất thường.
- Nếu $E(h(x)) \to c(n) \implies s \to 0.5$: Mẫu $x$ có đặc điểm bình thường.

Trong triển khai thực tế bằng `scikit-learn`, điểm số được biến đổi thành $Score = -\text{score\_samples}(X)$ để giá trị điểm càng cao thì mức độ bất thường càng lớn.

## 2.6. Feature Engineering
**Feature Engineering** là quá trình chuyển đổi dữ liệu thô (HTTP request log) thành các biến số định lượng biểu diễn các khía cạnh hành vi của người dùng. Trong đồ án này, 25 đặc trưng số được thiết kế nhằm phản ánh 3 trụ cột hành vi:
1. Cường độ và tốc độ phát yêu cầu (Frequency / Burst).
2. Mức độ tác động đến tài nguyên (Resource Variety / Sensitive Actions).
3. Phản hồi lỗi và phân quyền từ phía máy chủ (Error / Authorization Signals).

## 2.7. Chống rò rỉ dữ liệu (Data Leakage)
**Data Leakage (Rò rỉ dữ liệu)** là hiện tượng thông tin từ tập kiểm thử (Test Set) bị vô tình đưa vào quá trình huấn luyện mô hình, dẫn đến kết quả đánh giá cao một cách ảo tưởng.

Trong dữ liệu log theo phiên làm việc, nếu sử dụng phương pháp chia ngẫu nhiên (Random Split) ở cấp độ cửa sổ, các cửa sổ thuộc cùng một đợt thử nghiệm/cùng một phiên làm việc có thể xuất hiện đồng thời ở cả tập Train và Test. 

Để khắc phục, đồ án áp dụng kỹ thuật **Group-aware Split**: Tất cả các cửa sổ thuộc cùng một `run_id` (mã đợt giả lập) bắt buộc phải nằm trọn vẹn trong cùng một tập (Train, Validation hoặc Test).

## 2.8. Các chỉ số đánh giá
Hiệu năng của mô hình phân loại được đánh giá dựa trên **Ma trận nhầm lẫn (Confusion Matrix)**:

| | Dự đoán: Normal (0) | Dự đoán: Anomaly (1) |
|---|---|---|
| **Thực tế: Normal (0)** | True Negative (TN) | False Positive (FP) |
| **Thực tế: Anomaly (1)** | False Negative (FN) | True Positive (TP) |

Các chỉ số đánh giá chính:
- **Accuracy (Độ chính xác toàn cục):** $\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$
- **Precision (Độ chính xác của cảnh báo):** $\text{Precision} = \frac{TP}{TP + FP}$
- **Recall (Độ nhạy / Tỷ lệ phát hiện):** $\text{Recall} = \frac{TP}{TP + FN}$
- **F1-Score (Trung bình hài hòa giữa Precision và Recall):** $\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$
- **False Positive Rate (Tỷ lệ báo động giả):** $\text{FPR} = \frac{FP}{FP + TN}$

---

# CHƯƠNG 3: THU THẬP DỮ LIỆU VÀ XÂY DỰNG ĐẶC TRƯNG

## 3.1. Môi trường thực nghiệm và Chiến lược thu thập dữ liệu
Môi trường thực nghiệm gồm ứng dụng StudyDrive chạy trên nền tảng Flask 3.x với cơ sở dữ liệu SQLite/MySQL. 

Tất cả các HTTP Request gửi đến ứng dụng đều đi qua Flask Middleware `app/middleware/request_logging.py`. Khi một request hoàn tất, hook `@app.after_request` sẽ trích xuất thông tin ngữ cảnh và tự động chèn một bản ghi mới vào bảng `request_logs`.

[Hình 3.1: Kiến trúc thu thập dữ liệu log tự động tại Flask Middleware]

## 3.2. Cấu trúc dữ liệu log thô (Raw Features)
Mỗi bản ghi trong bảng `request_logs` lưu trữ 18 trường thông tin chính mô tả toàn bộ vòng đời của một request:

```text
1.  request_id           : Chuỗi UUID4 duy nhất nhận dạng request
2.  timestamp            : Thời điểm phát sinh request (chuẩn UTC)
3.  user_id              : ID người dùng (-1 nếu chưa đăng nhập)
4.  is_authenticated     : Trạng thái xác thực (True/False)
5.  role                 : Vai trò người dùng (USER / ADMIN / ANONYMOUS)
6.  session_id_hash      : Chuỗi băm SHA-256 của Session Token
7.  http_method          : Phương thức HTTP (GET, POST, DELETE...)
8.  endpoint             : Tên endpoint Flask xử lý request
9.  path                 : Đường dẫn URL chi tiết
10. action               : Tên hành động nghiệp vụ (view_file, export...)
11. action_type          : Loại hành động (read, export, delete, auth...)
12. is_sensitive         : Đánh dấu thao tác nhạy cảm (True/False)
13. resource_type        : Loại tài nguyên (file, folder, system)
14. resource_id          : ID đối tượng tài nguyên bị tác động
15. ownership_result     : Kết quả kiểm tra quyền sở hữu (OWNER, VIEWER, NONE)
16. authorization_result : Kết quả phân quyền (ALLOWED, DENIED)
17. status_code          : Mã trạng thái phản hồi HTTP (200, 403, 404, 500...)
18. response_time_ms     : Thời gian xử lý của máy chủ (tính bằng ms)
```

## 3.3. Giả lập kịch bản hành vi (Simulation)
Để tạo tập dữ liệu huấn luyện và đánh giá, đồ án xây dựng các script giả lập tự động bằng Python `requests` trong thư mục `scripts/`:

### 3.1. Hành vi người dùng hợp lệ (`simulate_normal.py`)
Mô phỏng chuỗi tương tác tự nhiên của người dùng bình thường: Đăng nhập $\to$ Duyệt danh sách thư mục $\to$ Xem chi tiết 2–3 tệp tin $\to$ Tải xuống 1 tệp $\to$ Đăng xuất. Các request phát sinh có khoảng cách thời gian ngẫu nhiên từ 3–15 giây.

### 3.2. Kịch bản Export Abuse (`simulate_export_abuse.py`)
Mô phỏng hành vi lạm dụng chức năng xuất dữ liệu (Business Logic Abuse). Script thực hiện gửi liên tục từ 30–50 request xuất báo cáo CSV/ZIP trong vòng 5 phút với khoảng thời gian giữa các request rất ngắn (< 1 giây).

### 3.3. Kịch bản Delete Abuse (`simulate_delete_abuse.py`)
Mô phỏng hành vi phá hoại tài nguyên bằng cách thực hiện xóa mềm (soft delete) liên tục khoảng 30 tệp tin khác nhau trong một cửa sổ 5 phút.

### 3.4. Kịch bản IDOR/BOLA Scan (`simulate_bola_scan.py`)
Mô phỏng hành vi rà quét thăm dò quyền truy cập đối tượng. Script thực hiện thay đổi tham số `file_id` theo thứ tự tăng dần từ 100 đến 500 để cố gắng truy cập các tệp tin không thuộc quyền sở hữu, tạo ra hàng loạt phản hồi lỗi 403 (Forbidden) và 404 (Not Found).

[Hình 3.2: Sơ đồ luồng hoạt động của các script giả lập dữ liệu]

Dữ liệu thu thập gồm **5.567 bản ghi log thô**, được gom thành **24 cửa sổ thời gian 5 phút**.

## 3.4. Tiền xử lý dữ liệu và Chống rò rỉ dữ liệu (Data Leakage)
Quy trình tiền xử lý được thực hiện qua các bước trong `ml/build_features.py`:
1. **Lọc dữ liệu rác:** Loại bỏ các request tĩnh (`/static/...`) và request kiểm tra trạng thái máy chủ (`/health`).
2. **Chuẩn hóa dtypes:** Ép kiểu `timestamp` về UTC, ép kiểu các biến boolean và chuyển `resource_id` về dạng chuỗi chuẩn.
3. **Gán nhãn Ground Truth:** Kết hợp log thô với file `ground_truth.csv` dựa trên khoảng thời gian `(started_at, ended_at)` và `user_id` để gán nhãn `label = 1` (Anomaly) hoặc `label = 0` (Normal).
4. **Chia tập dữ liệu chống rò rỉ:** Sử dụng hàm `split_features()` để nhóm các cửa sổ theo `run_id`. Tập Train chỉ giữ lại các đợt chạy Normal.

## 3.5. Trích xuất đặc trưng (Feature Engineering)
Từ các bản ghi log trong mỗi cửa sổ 5 phút `(user_id, session_id_hash)`, pipeline tính toán **25 đặc trưng số** và chia thành 3 nhóm:

### 5.1. Đặc trưng dựa trên tần suất (Frequency / Burst Features)
Các đặc trưng mô tả cường độ và tốc độ tương tác của người dùng:
1. `request_count`: Tổng số request trong cửa sổ.
2. `session_duration_sec`: Thời gian phiên (giây) = $\max(ts) - \min(ts)$.
3. `avg_inter_request_sec`: Khoảng cách thời gian trung bình giữa 2 request liên tiếp.
4. `min_inter_request_sec`: Khoảng cách thời gian nhỏ nhất giữa 2 request.
5. `burst_rate`: Tỷ lệ request có khoảng cách liên tiếp $\le 1.0$ giây.
6. `export_count`: Số lượng request export.
7. `export_ratio`: Tỷ lệ request export = $\frac{\text{export\_count}}{\text{request\_count}}$.
8. `delete_count`: Số lượng request xóa.
9. `delete_ratio`: Tỷ lệ request xóa = $\frac{\text{delete\_count}}{\text{request\_count}}$.
10. `sensitive_request_count`: Số request nhạy cảm (`is_sensitive = True`).
11. `sensitive_ratio`: Tỷ lệ request nhạy cảm.
12. `max_sensitive_streak`: Độ dài chuỗi request nhạy cảm liên tiếp dài nhất.

### 5.2. Đặc trưng dựa trên tính đa dạng tài nguyên (Resource Variety Features)
Các đặc trưng đo lường phạm vi tài nguyên mà người dùng tác động:
13. `unique_endpoint_count`: Số lượng endpoint Flask khác nhau được truy cập.
14. `unique_method_count`: Số lượng phương thức HTTP khác nhau (GET, POST...).
15. `unique_deleted_resource_count`: Số lượng `resource_id` duy nhất bị xóa.
16. `unique_resource_id_count`: Số lượng `resource_id` duy nhất được yêu cầu.
17. `resource_id_request_ratio`: Tỷ lệ đa dạng tài nguyên = $\frac{\text{unique\_resource\_id\_count}}{\text{request\_count}}$.
18. `resource_id_change_rate`: Tỷ lệ thay đổi `resource_id` giữa các request liên tiếp.

### 5.3. Đặc trưng dựa trên tỷ lệ lỗi và phân quyền (Error / Authorization Features)
Các đặc trưng phát hiện dấu hiệu bất thường về mặt phân quyền và phản hồi hệ thống:
19. `error_rate`: Tỷ lệ request có status code $\ge 400$.
20. `avg_response_time_ms`: Thời gian phản hồi trung bình của máy chủ.
21. `forbidden_count`: Số lượng request bị từ chối quyền (status code 403).
22. `forbidden_rate`: Tỷ lệ request nhận lỗi 403.
23. `not_found_count`: Số lượng request không tìm thấy tài nguyên (status code 404).
24. `not_found_rate`: Tỷ lệ request nhận lỗi 404.
25. `unique_failed_resource_id_count`: Số lượng `resource_id` duy nhất bị lỗi (403 hoặc 404).

---

# CHƯƠNG 4: HUẤN LUYỆN MÔ HÌNH VÀ ĐÁNH GIÁ KẾT QUẢ

## 4.1. Thiết kế thực nghiệm và Phân chia tập dữ liệu (Train/Validation/Test)
Tập dữ liệu gồm 24 cửa sổ 5 phút trích xuất từ 5.567 bản ghi log được phân chia theo Group Key `(run_id, session_id_hash)` theo tỷ lệ xấp xỉ 60% / 20% / 20%:
- **Tập Train (Huấn luyện):** Gồm 15 cửa sổ hoàn toàn bình thường (`label = 0`), dùng để mô hình học phân bố chuẩn.
- **Tập Validation (Thẩm định):** Gồm 3 cửa sổ (gồm cả Normal và Anomaly), dùng cho quá trình tinh chỉnh siêu tham số và xác định ngưỡng (threshold).
- **Tập Test (Kiểm thử):** Gồm 6 cửa sổ độc lập (3 Normal, 3 Anomaly), dùng để đánh giá hiệu năng cuối cùng.

## 4.2. Quá trình huấn luyện và Tinh chỉnh siêu tham số (Hyperparameter Tuning)

### Baseline Model
Cấu hình mặc định ban đầu trong `ml/train.py`:
- `n_estimators` = 200 (số lượng cây).
- `max_samples` = 'auto' ($\min(256, n)$).
- `contamination` = 'auto'.
- `random_state` = 20260706.

### Grid Tuning trên tập Validation
Thực hiện tìm kiếm trên lưới (Grid Search) qua **24 tổ hợp siêu tham số**:
- `n_estimators`: [100, 200, 300]
- `max_samples`: ['auto', 256]
- `threshold_percentile`: [90.0%, 92.5%, 95.0%, 97.5%]

Tiêu chí chọn cấu hình tối ưu dựa trên thứ tự ưu tiên: $\text{F1-Score} \to -\text{FPR} \to \text{Recall}$.

**Kết quả cấu hình tối ưu:**
- `n_estimators` = 200
- `max_samples` = 'auto'
- `threshold_percentile` = 95.0%
- Ngưỡng Anomaly Score thu được: $\text{Threshold} \approx 0.4866$

## 4.3. Kết quả đánh giá
Đánh giá mô hình trên **Tập Test độc lập (6 cửa sổ)** thu được các kết quả định lượng:

| Chỉ số đánh giá | Giá trị thu được |
|---|---|
| **Accuracy** | **66,67%** |
| **Precision** | **66,67%** |
| **Recall** | **66,67%** |
| **F1-Score** | **66,67%** |
| **False Positive Rate (FPR)** | **33,33%** |

### Ma trận nhầm lẫn (Confusion Matrix)

```text
                    Predicted Normal (0)    Predicted Anomaly (1)
Actual Normal (0)          TN = 2                  FP = 1
Actual Anomaly (1)         FN = 1                  TP = 2
```

## 4.4. Phân tích trực quan

[Hình 4.1: Biểu đồ Ma trận nhầm lẫn Confusion Matrix trên tập Test]

### Phân tích chi tiết theo từng kịch bản hành vi:
1. **Kịch bản Export Abuse (Thành công):** Mô hình phát hiện chính xác **2/2 cửa sổ Export Abuse** trong tập Test ($\text{TP} = 2$). Nguyên nhân là do nhóm đặc trưng `export_count` và `burst_rate` vượt trội so với phân bố bình thường.
2. **Kịch bản BOLA Scan (False Negative):** Có **1 cửa sổ BOLA Scan bị bỏ sót** ($\text{FN} = 1$). Qua phân tích log, cửa sổ này có quy mô request nhỏ (số lượng mẫu thử nghiệm chưa đủ lớn), làm các đặc trưng `forbidden_rate` và `resource_id_change_rate` chưa đạt ngưỡng kích hoạt cảnh báo.
3. **Hành vi người dùng hợp lệ cường độ cao (False Positive):** Có **1 cửa sổ Normal bị cảnh báo nhầm** ($\text{FP} = 1$). Nguyên nhân do người dùng hợp lệ thực hiện duyệt tệp và xuất báo cáo liên tục trong thời gian ngắn, tạo ra độ vọt `burst_rate` tiệm cận với kịch bản tấn công.

[Hình 4.2: Biểu đồ phân bố điểm Anomaly Score giữa các cửa sổ Normal và Anomaly]

## 4.5. Những hạn chế trong quá trình thực nghiệm mô hình
- **Kích thước tập kiểm thử hạn chế:** Do dữ liệu thực nghiệm gồm 24 cửa sổ (6 cửa sổ tập Test), chỉ số 66.67% mang tính chất phản ánh trên tập dữ liệu thử nghiệm hiện tại.
- **Tỷ lệ báo động giả (FPR = 33.33%):** Mô hình có xu hướng nhạy cảm với các hành vi người dùng thao tác nhanh.
- **Phụ thuộc vào kích thước cửa sổ 5 phút:** Các đợt tấn công có mật độ request quá thưa thớt trong cửa sổ 5 phút có thể chưa bị phát hiện.

---

# CHƯƠNG 5: TRIỂN KHAI HỆ THỐNG VÀ KIẾN TRÚC TÍCH HỢP

## 5.1. Luồng xử lý hệ thống (Pipeline)
Hệ thống StudyDrive được tích hợp hoàn chỉnh theo quy trình dữ liệu khép kín:

```text
[HTTP Requests]
       │
       ▼
[Flask Middleware (request_logging.py)] ──(after_request)──► [Database: request_logs]
                                                                    │
                                                                    ▼
[Admin Dashboard / Trigger] ──────────► [detection_service.py]
                                                │
                                                ├─► 1. Gom nhóm cửa sổ 5 phút
                                                ├─► 2. Trích xuất 25 đặc trưng (build_features.py)
                                                ├─► 3. Load model.joblib (Isolation Forest)
                                                └─► 4. Tính Anomaly Score & so sánh Threshold
                                                                    │
                                                                    ▼
                                                            [Database: alerts]
                                                                    │
                                                                    ▼
                                                        [Admin Alerts Dashboard]
                                                                    │
                                                                    ▼
                                                        [Truy vết Log gốc trong cửa sổ]
```

## 5.2. Cơ chế phát hiện tự động
Dịch vụ phát hiện bất thường được đóng gói tại `app/services/detection_service.py`.

```python
# Đoạn mã thực thi Detection Service chính
def run_detection_pipeline(app):
    logs_df = fetch_unprocessed_request_logs()
    clean_df, _ = clean_logs(logs_df)
    features_df = aggregate_features(clean_df)
    
    # Load mô hình đã huấn luyện
    model_artifact = joblib.load("artifacts/models/iforest_v1/model.joblib")
    model = model_artifact["model"]
    threshold = model_artifact["threshold"]
    
    # Tính điểm bất thường
    X = prepare_x(features_df, FEATURE_COLUMNS)
    scores = -model.score_samples(X)
    
    # Lưu Alert vào cơ sở dữ liệu nếu vượt ngưỡng
    for idx, score in enumerate(scores):
        if score >= threshold:
            create_alert_record(features_df.iloc[idx], score)
```

Tiến trình Detection có thể được kích hoạt theo 2 cách:
1. Quản trị viên nhấn nút **"Run Detection"** trên giao diện Admin.
2. Đã kích hoạt tự động qua dòng lệnh CLI: `python -m scripts.run_detection`.

## 5.3. Giao diện quản trị

### Alerts Dashboard
Trang quản trị Cảnh báo (`/admin/alerts`) cung cấp giao diện trực quan cho Admin:
- Danh sách cảnh báo hiển thị rõ: Thời gian phát hiện, User ID, Session ID hash, Anomaly Score, Gợi ý kịch bản (`scenario_hint`).
- Trạng thái cảnh báo: `Pending` (Mới), `Investigating` (Đang rà soát), `Resolved` (Đã xử lý), `Ignored` (Bỏ qua).

[Hình 5.1: Giao diện Alerts Dashboard quản lý các cảnh báo bất thường]

### Cơ chế truy vết Log gốc (Forensics)
Khi nhấn vào chi tiết một Alert, hệ thống trích xuất thông tin `(user_id, session_id_hash, window_start, window_end)` và cung cấp đường dẫn chuyển hướng trực tiếp đến trang **Admin Logs Filtered**.

[Hình 5.2: Giao diện truy vết chi tiết từ Alert về các bản ghi Request Log thô trong cửa sổ 5 phút]

Quản trị viên có thể xem chính xác từng HTTP Request xảy ra trong cửa sổ 5 phút bị cảnh báo, kiểm tra URL, status code, tham số request để đưa ra kết luận chính xác.

### Kiểm thử hệ thống tự động
Hệ thống được đảm bảo độ tin cậy bằng bộ kiểm thử tự động gồm **34 test cases** (sử dụng Pytest và Pytest-Flask):
- `test_health.py` & `test_blueprints.py`: 6 tests kiểm thử routing và giao diện.
- `test_documents.py`: 13 tests kiểm thử các thao tác tệp, phân quyền và bảo mật.
- `test_request_logging.py`: 8 tests kiểm thử Middleware ghi log tự động và bảo vệ dữ liệu nhạy cảm.
- `test_admin_logs.py`: 3 tests kiểm thử lọc log và phân quyền Admin.
- `test_web_freeze.py`: 4 tests kiểm thử luồng nghiệp vụ tích hợp.

**Kết quả kiểm thử:** `34 passed in 17.87s` (Tỷ lệ pass 100%).

---

# CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 6.1. Kết quả đạt được
Đồ án đã nghiên cứu và ứng dụng thành công kỹ thuật Machine Learning trong bài toán phát hiện hành vi truy cập bất thường trên ứng dụng web StudyDrive:
1. **Phần mềm Web & Logging:** Triển khai thành công web StudyDrive với cơ chế Structured Logging tự động tại Flask Middleware, áp dụng giải pháp băm SHA-256 bảo vệ thông tin phiên.
2. **Pipeline Machine Learning hoàn chỉnh:** Xây dựng quy trình khép kín từ thu thập log thô $\to$ làm sạch $\to$ gom cửa sổ 5 phút $\to$ trích xuất 25 đặc trưng số $\to$ huấn luyện mô hình Isolation Forest (Normal-only Training, Group-aware Split).
3. **Tích hợp ứng dụng:** Đưa kết quả từ mô hình ML vào CSDL và hiển thị trên giao diện quản trị Alerts Dashboard, hỗ trợ tính năng truy vết trực tiếp về bản ghi log gốc.
4. **Đánh giá & Kiểm thử:** Thực hiện đánh giá định lượng trên tập Test (F1-Score 66.67%) và vượt qua toàn bộ 34 test cases tự động bằng Pytest.

## 6.2. Hạn chế
- **Kích thước dữ liệu thực nghiệm:** Tập dữ liệu thử nghiệm còn nhỏ (24 cửa sổ 5 phút), cần mở rộng quy mô dữ liệu trong môi trường thực tế.
- **Phương thức xử lý Batch:** Hệ thống hiện tại xử lý phát hiện theo lô định kỳ, chưa đạt tới thời gian thực (Real-time Streaming).
- **Phản ứng thụ động:** Hệ thống mới dừng lại ở bước phát cảnh báo cho Admin, chưa tích hợp cơ chế tự động phản ứng (Auto-blocking IP hay tự động khóa tài khoản).

## 6.3. Hướng phát triển
1. **Nâng cấp kiến trúc phát hiện thời gian thực (Real-time Pipeline):** Tích hợp Message Broker (như Apache Kafka hoặc RabbitMQ) và Celery Workers để xử lý trích xuất đặc trưng và dự báo theo dạng dòng chảy (stream processing).
2. **Cải tiến thuật toán & Đa dạng kịch bản:** Thử nghiệm kết hợp Isolation Forest với các thuật toán Autoencoder hoặc One-Class SVM; mở rộng thêm các kịch bản tấn công như Credential Stuffing, Brute-force Login và Account Enumeration.
3. **Phát triển cơ chế tự động phản ứng (Active Response):** Xây dựng module tự động áp dụng chính sách bảo mật (khóa tạm thời session, yêu cầu xác thực OTP hoặc chặn IP) khi Anomaly Score vượt ngưỡng nguy hiểm.

---

# TÀI LIỆU THAM KHẢO

1. **OWASP Foundation (2023).** *OWASP API Security Top 10 2023 – API1:2023 Broken Object Level Authorization (BOLA)*. URL: https://owasp.org/API-Security/editions/2023/en/0xaa-api1/
2. **Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008).** *Isolation Forest*. In 2008 Eighth IEEE International Conference on Data Mining (pp. 413-422). IEEE.
3. **Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., ... & Duchesnay, É. (2011).** *Scikit-learn: Machine Learning in Python*. Journal of Machine Learning Research, 12, 2825-2830.
4. **Grinberg, M. (2018).** *Flask Web Development: Developing Web Applications with Python*. O'Reilly Media.
