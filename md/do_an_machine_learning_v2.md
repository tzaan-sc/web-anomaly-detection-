# ĐỒ ÁN CÔNG NGHỆ THÔNG TIN 3
## XÂY DỰNG HỆ THỐNG PHÁT HIỆN HÀNH VI TRUY CẬP BẤT THƯỜNG TRÊN ỨNG DỤNG WEB BẰNG MACHINE LEARNING

**TRƯỜNG ĐẠI HỌC KỸ THUẬT - CÔNG NGHỆ CẦN THƠ**  
**KHOA CÔNG NGHỆ THÔNG TIN**  

| CÁN BỘ HƯỚNG DẪN | SINH VIÊN THỰC HIỆN | MSSV |
| :--- | :--- | :--- |
| ThS. Nguyễn Trung Kiên | Ngô Thu Vân | CNTT2311044 |

**Cần Thơ, 2026**

---

## NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN
*(Dành cho giáo viên hướng dẫn nhận xét)*

## NHẬN XÉT CỦA GIÁO VIÊN PHẢN BIỆN
*(Dành cho giáo viên phản biện nhận xét)*

## LỜI CAM ĐOAN
Em xin cam đoan đồ án “Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning” là công trình nghiên cứu của riêng em dưới sự hướng dẫn của ThS. Nguyễn Trung Kiên.
Các nội dung, số liệu, kết quả và sản phẩm được trình bày trong đồ án hoàn toàn do em tự thực hiện. Các tài liệu tham khảo, trích dẫn trong đồ án đều được ghi rõ nguồn gốc và tuân thủ đúng quy định về trích dẫn tại phần Tài liệu tham khảo.
Em xin chịu hoàn toàn trách nhiệm về tính trung thực và nội dung của đồ án này trước khoa và nhà trường.

## LỜI CẢM ƠN
Lời đầu tiên, em xin gửi lời tri ân sâu sắc đến quý thầy, cô giảng viên Trường Đại học Kỹ thuật – Công nghệ Cần Thơ. Những kiến thức chuyên môn quý báu được tiếp thu trên giảng đường chính là hành trang vững chắc để em thực hiện đồ án này.

Đặc biệt, em xin gửi lời cảm ơn chân thành nhất đến giảng viên hướng dẫn ThS. Nguyễn Trung Kiên. Trong suốt thời gian thực hiện đồ án, thầy không chỉ định hướng đề tài mà còn hỗ trợ em rất nhiều trong việc tháo gỡ các vướng mắc về mặt kỹ thuật và phương pháp luận. Sự chỉ bảo tận tình của thầy là nguồn động lực to lớn giúp em hoàn thiện sản phẩm.

Dù đã nỗ lực hoàn thiện, song do hạn chế về kinh nghiệm, đồ án khó tránh khỏi những thiếu sót. Em rất mong nhận được sự góp ý, chỉ bảo của quý thầy cô để có thể tiếp tục hoàn thiện trong tương lai.

Em xin chân thành cảm ơn!

## TÓM TẮT ĐỒ ÁN
Đồ án Công nghệ thông tin 3 với đề tài “Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning” được thực hiện nhằm giải quyết bài toán bảo mật ở tầng ứng dụng (Application Layer), tập trung vào các rủi ro Lạm dụng logic nghiệp vụ (Business Logic Abuse) và lỗ hổng Kiểm soát truy cập đối tượng (BOLA/IDOR). Hệ thống được triển khai tích hợp trực tiếp trên ứng dụng quản lý và chia sẻ tài liệu trực tuyến StudyDrive.

Thay vì sử dụng các quy tắc cố định (static rules), đề tài áp dụng thuật toán học máy không giám sát Isolation Forest (mô hình huấn luyện Normal-only) để phân tích nhật ký truy cập (Request Logs) theo cửa sổ thời gian 5 phút. Dữ liệu thô được ghi nhận tự động tại tầng Middleware của Flask, trích xuất thành vector 25 đặc trưng số định lượng. Hệ thống tích hợp quy trình phát hiện tự động (Detection Pipeline), cơ chế phản ứng chủ động (Active Defense - tự động khóa tạm thời tài khoản bị nghi ngờ 60 phút) và giao diện trực quan Alerts Dashboard (tích hợp biểu đồ Chart.js và Modal thông báo). Hệ thống đã hoàn thành bộ kiểm thử tự động với 38 test cases qua tuyệt đối 100%.

---

## DANH MỤC HÌNH ẢNH
| STT | Mục | Nội dung | Trang |
|---|---|---|---|
| 1 | | | |

## DANH MỤC BẢNG
| STT | Mục | Nội Dung | Trang |
|---|---|---|---|
| 1 | | | |

## BẢNG KÝ HIỆU, CHỮ VIẾT TẮT
| STT | Từ viết tắt, ký hiệu | Ý nghĩa |
|---|---|---|
| 1 | WAF | Web Application Firewall |
| 2 | IDS | Intrusion Detection System |
| 3 | BOLA | Broken Object Level Authorization |
| 4 | IDOR | Insecure Direct Object Reference |
| 5 | iForest | Isolation Forest |

---

## MỞ ĐẦU
Trong những năm gần đây, các ứng dụng web lưu trữ và chia sẻ tài liệu trực tuyến đóng vai trò quan trọng trong hạ tầng thông tin của các tổ chức, doanh nghiệp và trường đại học. Sự đa dạng về chức năng (tải lên, xuất dữ liệu, chia sẻ, xóa, quản lý phân quyền đối tượng) giúp nâng cao hiệu quả làm việc, nhưng đồng thời đặt ra yêu cầu ngày càng cao về an toàn thông tin và kiểm soát hành vi truy cập.

Trong các hệ thống web, nhiều hành vi lạm dụng nguy hiểm không biểu hiện qua cú pháp request bất thường hay chữ ký tấn công đã biết. Kẻ tấn công hoặc người dùng nội bộ lạm dụng có thể gửi các HTTP Request hoàn toàn hợp lệ về mặt cú pháp nhưng với tần suất, trình tự hoặc tham số tài nguyên bất thường (như tải xuống hàng loạt tài liệu, xóa dữ liệu trên diện rộng, hoặc dò quét mã tài nguyên IDOR/BOLA). Các giải pháp truyền thống như WAF hay IDS dựa trên chữ ký gặp nhiều hạn chế khi đối mặt với các dạng tấn công lạm dụng logic nghiệp vụ này.

Từ thực tế đó, đề tài **“Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning”** được thực hiện. Nhóm chọn cách tiếp cận học máy không giám sát với thuật toán Isolation Forest, xây dựng một quy trình khép kín: Tự động ghi nhật ký truy cập tại Middleware -> Gom nhóm cửa sổ 5 phút -> Trích xuất 25 đặc trưng hành vi -> Phát hiện bất thường bằng AI -> Phản ứng tự động (Active Defense khóa tài khoản 60 phút) -> Hỗ trợ Quản trị viên trực quan hóa và truy ngược về log gốc (Forensics).

---

## CHƯƠNG 1: TỔNG QUAN

### 1.1 Lý do chọn đề tài
Trong quá trình chuyển đổi số, các ứng dụng Web hỗ trợ lưu trữ và chia sẻ tài liệu trực tuyến được sử dụng rộng rãi trong vận hành của các tổ chức, doanh nghiệp và trường đại học. Các hệ thống này (tương tự Google Workspace hay Microsoft SharePoint) đóng vai trò là kho lưu trữ tài nguyên tri thức và tài liệu nội bộ quan trọng. Khác với người dùng cá nhân chỉ quản lý không gian riêng, các tổ chức đòi hỏi một cơ chế giám sát an toàn thông tin tập trung do bộ phận Quản trị hệ thống (IT/System Admin) đảm nhiệm nhằm bảo vệ tài nguyên chung, ngăn chặn nguy cơ thất thoát dữ liệu và duy trì tính sẵn sàng của hệ thống.

Một trong những nguy cơ bảo mật lớn nhất là việc người dùng nội bộ hoặc kẻ tấn công chiếm đoạt tài khoản (Account Takeover) lạm dụng chức năng hợp lệ để thực hiện các hành vi bất thường. Các hành vi này gửi các HTTP Request chuẩn xác về mặt cú pháp nhưng thực hiện với tần suất hoặc trình tự bất thường (tải xuống hàng loạt, xóa tài nguyên trên diện rộng, thay đổi ID tài nguyên để thăm dò dữ liệu người khác), gây ra thiệt hại nghiêm trọng như rò rỉ thông tin (Data Exfiltration) hoặc phá hoại (Sabotage).

Các cơ chế bảo mật truyền thống như Web Application Firewall (WAF) hoặc Intrusion Detection System (IDS) thường phát huy hiệu quả với chữ ký tấn công đã biết, nhưng khó nhận diện Business Logic Abuse hay BOLA/IDOR vì từng HTTP Request riêng lẻ hoàn toàn hợp lệ. Do đó, việc phân tích đặc trưng hành vi tổng hợp trong các cửa sổ thời gian bằng Machine Learning (thuật toán Isolation Forest) là hướng tiếp cận phù hợp để nhận diện những chuỗi thao tác lệch chuẩn so với trạng thái bình thường của tổ chức.

Từ thực tiễn đó, đề tài xây dựng giải pháp bảo mật khép kín tích hợp trên ứng dụng StudyDrive: Thu thập nhật ký truy cập tự động -> Gom nhóm đặc trưng hành vi -> Phát hiện bất thường bằng AI -> Phản ứng tự động khóa tài khoản nghi vấn (Active Defense) -> Trực quan hóa cảnh báo và truy ngược về các request log gốc.

### 1.2 Mục tiêu nghiên cứu
Mục tiêu cốt lõi của đồ án là xây dựng ứng dụng Web StudyDrive tích hợp hệ thống ghi nhật ký truy cập có cấu trúc và mô hình Machine Learning không giám sát Isolation Forest nhằm phát hiện các hành vi truy cập bất thường liên quan đến lạm dụng logic nghiệp vụ và truy cập tài nguyên trái phép.

Các mục tiêu cụ thể gồm:
* Xây dựng ứng dụng Web StudyDrive với các chức năng quản lý, lưu trữ, chia sẻ và xuất tệp tin; hỗ trợ cơ chế phân quyền ở cấp đối tượng (OWNER, VIEWER).
* Xây dựng hệ thống Structured Request Logging tại tầng Middleware của Flask nhằm tự động ghi nhận 27 thông số của HTTP Request.
* Bảo đảm an toàn dữ liệu nhật ký: Không lưu mật khẩu, CSRF token hay session ID nguyên bản; session ID được xử lý băm SHA-256 trước khi lưu vào CSDL.
* Xây dựng dữ liệu phục vụ huấn luyện và kiểm thử thông qua các script mô phỏng hành vi bình thường và 3 kịch bản bất thường (Export Abuse, Delete Abuse, IDOR/BOLA Scan).
* Xây dựng Pipeline xử lý dữ liệu: Gom nhóm log theo cửa sổ 5 phút dựa trên `user_id` và `session_id_hash`, chuyển đổi thành vector 25 đặc trưng số định lượng.
* Huấn luyện mô hình Isolation Forest theo chiến lược Normal-only Training (chỉ học trên dữ liệu bình thường), phân chia tập Train/Validation/Test theo nhóm (Group-aware Split) nhằm tránh rò rỉ dữ liệu.
* Tinh chỉnh siêu tham số (Hyperparameter Tuning) và xác định ngưỡng Anomaly Score tối ưu.
* Xây dựng cơ chế Phản ứng chủ động (Active Defense): Tự động đặt thời gian khóa tài khoản 60 phút (`locked_until`) khi điểm số bất thường vượt ngưỡng cao hoặc khớp kịch bản tấn công, Middleware tự động trả về `HTTP 403 Forbidden`.
* Xây dựng giao diện Alerts Dashboard tích hợp Modal Popup tóm tắt kết quả, Biểu đồ tròn Chart.js và khả năng truy vết log gốc (Forensics).
* Thực hiện kiểm thử tự động với bộ Pytest đạt 38/38 test cases pass (100%).

### 1.3 Đối tượng & Phạm vi nghiên cứu

#### Đối tượng nghiên cứu
* Tập hợp các bản ghi HTTP Request Log được thu thập trực tiếp tại tầng ứng dụng của nền tảng web StudyDrive.
* Chuỗi hành vi truy cập của người dùng được định lượng qua vector 25 đặc trưng số trong cửa sổ thời gian 5 phút.
* Thuật toán phát hiện bất thường học không giám sát Isolation Forest cùng quy trình xử lý dữ liệu chuỗi thời gian (time-window feature engineering).

#### Phạm vi nghiên cứu
* **Môi trường thực nghiệm & Bối cảnh:** Triển khai trên StudyDrive - nền tảng quản lý và lưu trữ tài liệu trực tuyến hướng đến môi trường tổ chức/trường đại học. Quản trị viên (Admin) đóng vai trò cán bộ an ninh IT/System Admin giám sát toàn hệ thống.
* **Đối tượng phân tích:** Log truy cập của người dùng đã đăng nhập (Authenticated Users). Hệ thống không phân tích truy cập ẩn danh.
* **Phạm vi kịch bản phát hiện:**
  * **Export Abuse:** Nhận diện hành vi xuất siêu dữ liệu hoặc tải xuống hàng loạt vượt quá nhu cầu sử dụng thông thường.
  * **Delete Abuse:** Phát hiện thao tác xóa mềm (soft-delete) hàng loạt trên nhiều tài nguyên trong thời gian ngắn.
  * **IDOR / BOLA Scan:** Phát hiện hành vi cố tình thay đổi tham số resource_id trên URL/API nhằm truy cập trái phép vào tệp tin không thuộc quyền sở hữu.
* **Chế độ xử lý:** Xử lý theo Batch/Trigger với cửa sổ 5 phút không chồng lấp.
* **Phản ứng tự động (Active Defense):** Khóa tạm thời tài khoản nghi ngờ 60 phút (`locked_until`), chặn request tiếp theo bằng phản hồi HTTP 403 Forbidden.

### 1.4 Phương pháp nghiên cứu
* **Nghiên cứu lý thuyết:** Phân tích tài liệu OWASP API Security Top 10 (đặc biệt lỗ hổng BOLA/IDOR), nguyên lý thuật toán Isolation Forest và kỹ thuật Feature Engineering trên log web.
* **Thực nghiệm xây dựng phần mềm:** Áp dụng Flask, SQLAlchemy ORM, Jinja2 Template và Bootstrap 5 để phát triển ứng dụng StudyDrive.
* **Thực nghiệm giả lập & thu thập dữ liệu:** Sử dụng các script mô phỏng bằng Python requests để thu thập dữ liệu log thô kèm nhãn Ground Truth.
* **Phân tích & Huấn luyện:** Tiền xử lý dữ liệu, trích xuất 25 đặc trưng số, chia tập bằng Group-aware Split theo `run_id` và `session_id_hash`, huấn luyện Isolation Forest trên tập Normal-only và tinh chỉnh siêu tham số trên tập Validation.
* **Đánh giá & Kiểm thử:** Kiểm thử định lượng trên tập Test độc lập và thực thi bộ kiểm thử tự động Pytest gồm 38 test cases.

### 1.5 Cấu trúc đồ án
Đồ án gồm 6 chương:
* **Chương 1: Tổng quan** - Lý do chọn đề tài, mục tiêu, đối tượng, phạm vi, phương pháp nghiên cứu và cấu trúc báo cáo.
* **Chương 2: Cơ sở lý thuyết** - Kiến thức về logging tầng ứng dụng, Business Logic Abuse, BOLA/IDOR, chiến lược Normal-only Training, thuật toán Isolation Forest và các chỉ số đánh giá.
* **Chương 3: Thu thập dữ liệu và Xây dựng đặc trưng** - Cấu trúc request log thô, các kịch bản giả lập, quy trình làm sạch dữ liệu và chi tiết danh sách 25 đặc trưng số.
* **Chương 4: Huấn luyện mô hình và Đánh giá kết quả** - Phân chia tập dữ liệu, quá trình tinh chỉnh siêu tham số, kết quả đánh giá thực nghiệm và phân tích ma trận nhầm lẫn.
* **Chương 5: Triển khai hệ thống và Kiến trúc tích hợp** - Luồng xử lý toàn hệ thống, cơ chế Active Defense, giao diện Alerts Dashboard và khả năng truy vết log.
* **Chương 6: Kết luận và Hướng phát triển** - Tổng kết kết quả đạt được, các hạn chế còn tồn tại và định hướng phát triển tương lai.

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

### 2.1 Logging tầng ứng dụng và Bảo mật dữ liệu Log
Logging tầng ứng dụng (Application Layer Logging) là quá trình tự động ghi nhận chi tiết các tương tác HTTP giữa Client và Server. Trong dự án này, hệ thống áp dụng Structured Logging với 27 trường dữ liệu chuẩn hóa.

Để bảo vệ an toàn thông tin theo các nguyên tắc bảo mật:
* Mật khẩu nguyên bản, token khôi phục mật khẩu và CSRF token **tuyệt đối không được ghi vào log**.
* Mã định danh phiên làm việc (`session_id`) được xử lý qua hàm băm SHA-256 thành `session_id_hash` trước khi lưu trữ, giúp đảm bảo khả năng phân nhóm truy cập theo phiên mà không làm lộ token phiên làm việc thực tế.

### 2.2 Lạm dụng logic nghiệp vụ (Business Logic Abuse) và lỗ hổng BOLA/IDOR
* **Business Logic Abuse:** Hành vi lạm dụng các luồng chức năng hợp pháp của ứng dụng theo trình tự hoặc tần suất bất thường nhằm mục đích xấu (như rút cạn dữ liệu hoặc xóa phá hoại).
* **BOLA (Broken Object Level Authorization) / IDOR (Insecure Direct Object Reference):** Lỗ hổng xảy ra khi ứng dụng không kiểm tra nghiêm ngặt quyền sở hữu đối tượng khi người dùng thay đổi tham số định danh tài nguyên (`resource_id`) trên request. Kẻ tấn công có thể thay đổi ID để truy cập hoặc thao tác trên tệp tin của người dùng khác.

### 2.3 Cửa sổ thời gian (Time-window Feature Engineering)
Dữ liệu log thô là chuỗi sự kiện theo thời gian. Để đưa vào mô hình Machine Learning, hệ thống gom nhóm các bản ghi log trong cửa sổ 5 phút không chồng lấp theo từng nhóm (`user_id`, `session_id_hash`). Mỗi cửa sổ 5 phút được chuyển đổi thành một vector định lượng 25 chiều biểu diễn tổng quan hành vi của người dùng trong khoảng thời gian đó.

### 2.4 Chiến lược huấn luyện Normal-only và Thuật toán Isolation Forest
* **Normal-only Training:** Trong thực tế an ninh mạng, dữ liệu tấn công thường rất hiếm và luôn xuất hiện các dạng tấn công mới chưa từng biết trước. Do đó, mô hình được huấn luyện hoàn toàn trên dữ liệu hành vi bình thường (label = 0) để học phân bố chuẩn của hệ thống.
* **Thuật toán Isolation Forest (iForest):** Thuật toán học máy không giám sát dựa trên nguyên lý xây dựng một rừng các cây cô lập ngẫu nhiên (Isolation Trees). Các mẫu dữ liệu bất thường có thuộc tính khác biệt sẽ dễ bị cô lập hơn và nằm ở độ sâu cây (path length) ngắn hơn so với các mẫu bình thường. Điểm bất thường (Anomaly Score) được tính dựa trên độ sâu trung bình của mẫu trên toàn bộ rừng cây.

### 2.5 Phương pháp chia tập dữ liệu chống rò rỉ (Group-aware Split)
Nếu chia dữ liệu ngẫu nhiên ở cấp độ cửa sổ, các cửa sổ thuộc cùng một phiên làm việc (`session_id_hash`) có thể nằm ở cả tập Train và tập Test, gây ra hiện tượng rò rỉ dữ liệu (Data Leakage). Đề tài áp dụng phương pháp **Group-aware Split**, gom nhóm các cửa sổ theo khóa (`user_id`, `session_id_hash`), đảm bảo toàn bộ các cửa sổ của một phiên làm việc chỉ nằm hoàn toàn trong tập Train, Validation hoặc Test.

### 2.6 Các chỉ số đánh giá hiệu năng
Hiệu năng phát hiện bất thường được đánh giá qua các chỉ số:
* **Accuracy (Độ chính xác):** Tỷ lệ phân loại đúng trên tổng số cửa sổ.
* **Precision (Độ xác thực):** Tỷ lệ cảnh báo đúng trên tổng số cảnh báo phát ra ($TP / (TP + FP)$).
* **Recall (Độ nhạy):** Tỷ lệ phát hiện được các cửa sổ tấn công thực tế ($TP / (TP + FN)$).
* **F1-Score:** Trung bình hài hòa giữa Precision và Recall ($2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$).
* **FPR (False Positive Rate):** Tỷ lệ báo động giả ($FP / (FP + TN)$).

---

## CHƯƠNG 3: THU THẬP DỮ LIỆU VÀ XÂY DỰNG ĐẶC TRƯNG

### 3.1 Môi trường thực nghiệm và Cấu trúc Log thô
Ứng dụng StudyDrive được phát triển trên nền tảng Flask. Mỗi HTTP Request đi qua Middleware `request_logging.py` sẽ ghi lại 27 trường dữ liệu vào bảng `request_logs`:

| STT | Tên trường (Column) | Kiểu dữ liệu | Diễn giải |
|---|---|---|---|
| 1 | `id` | BigInteger | Khóa chính tự tăng |
| 2 | `request_id` | String(36) | Mã UUID duy nhất của request |
| 3 | `timestamp` | DateTime(UTC) | Thời điểm phát sinh request |
| 4 | `user_id` | Integer | ID người dùng (null nếu ẩn danh) |
| 5 | `username` | String(80) | Tên tài khoản người dùng |
| 6 | `is_authenticated` | Boolean | Cờ xác định trạng thái đăng nhập |
| 7 | `role` | String(20) | Vai trò hệ thống (admin, user) |
| 8 | `session_id_hash` | String(64) | Chuỗi mã băm SHA-256 của session ID |
| 9 | `ip_address` | String(45) | Địa chỉ IP của client |
| 10 | `user_agent` | String(255) | Thông tin trình duyệt/tool |
| 11 | `http_method` | String(10) | Phương thức HTTP (GET, POST, DELETE...) |
| 12 | `endpoint` | String(100) | Tên Flask endpoint xử lý |
| 13 | `path` | String(255) | Đường dẫn URL tương đối |
| 14 | `action` | String(50) | Hành động nghiệp vụ (login, download, delete...) |
| 15 | `action_type` | String(50) | Phân loại hành động (read, write, auth, admin) |
| 16 | `is_sensitive` | Boolean | Cờ đánh dấu đường dẫn/thao tác nhạy cảm |
| 17 | `resource_type` | String(50) | Loại tài nguyên (file, folder, user) |
| 18 | `resource_id` | String(100) | Mã ID tài nguyên tác động |
| 19 | `owner_id` | Integer | ID chủ sở hữu tài nguyên thực tế |
| 20 | `ownership_result` | String(20) | Kết quả kiểm tra sở hữu (is_owner, not_owner) |
| 21 | `permission` | String(20) | Quyền truy cập (OWNER, VIEWER, NONE) |
| 22 | `authorization_result` | String(20) | Kết quả phân quyền (allowed, denied) |
| 23 | `status_code` | Integer | Mã trạng thái phản hồi HTTP (200, 403, 404...) |
| 24 | `response_time_ms` | Float | Thời gian xử lý request (mili-giây) |
| 25 | `file_size` | BigInteger | Dung lượng tệp tin tác động (bytes) |
| 26 | `export_item_count` | Integer | Số tệp tin trong gói xuất zip/csv |
| 27 | `export_total_size` | BigInteger | Tổng dung lượng gói xuất (bytes) |

### 3.2 Kịch bản giả lập dữ liệu
Để phục vụ huấn luyện và đánh giá, các script mô phỏng được xây dựng trong thư mục `scripts/`:
* **`simulate_normal.py`:** Giả lập hành vi người dùng hợp lệ với 3 loại hồ sơ (casual, active, reviewer), thực hiện thao tác đăng nhập, duyệt thư mục, xem chi tiết, tải tệp với khoảng dừng ngẫu nhiên.
* **`simulate_export_abuse.py`:** Giả lập kịch bản xuất/tải xuống dữ liệu hàng loạt với các mức độ nghiêm trọng khác nhau (`mild`, `medium`, `high`).
* **`simulate_delete_abuse.py`:** Giả lập hành vi xóa mềm tệp tin liên tục trong thời gian ngắn với các mức độ (`mild`, `medium`).
* **`simulate_bola_scan.py`:** Giả lập hành vi thay đổi tham số `resource_id` liên tục trên các URL/API nhằm dò quét tệp tin của người khác (chạy dưới dạng `low-and-slow` hoặc `burst`).

### 3.3 Quy trình tiền xử lý và Trích xuất 25 Đặc trưng
Mô-đun `ml/build_features.py` thực hiện đọc log thô, lọc bỏ request không hợp lệ, gom nhóm theo cửa sổ 5 phút dựa trên `user_id` và `session_id_hash`, sau đó trích xuất đúng **25 đặc trưng số định lượng (FEATURE_COLUMNS)** chia thành 3 nhóm:

#### Nhóm 1: Tần suất và Cường độ thao tác (7 đặc trưng)
1. `request_count`: Tổng số HTTP Request trong cửa sổ 5 phút.
2. `unique_endpoint_count`: Số lượng endpoint Flask khác nhau được truy cập.
3. `unique_method_count`: Số lượng phương thức HTTP khác nhau được sử dụng.
4. `session_duration_sec`: Khoảng thời gian từ request đầu tiên đến request cuối cùng trong cửa sổ (giây).
5. `avg_inter_request_sec`: Thời gian trung bình giữa 2 request liên tiếp.
6. `min_inter_request_sec`: Thời gian ngắn nhất giữa 2 request liên tiếp.
7. `burst_rate`: Tần suất request tối đa per minute trong cửa sổ.

#### Nhóm 2: Hành động Nghiệp vụ và Tài nguyên (11 đặc trưng)
8. `sensitive_request_count`: Số lượng request gửi đến các endpoint nhạy cảm (auth, admin, export, delete).
9. `sensitive_ratio`: Tỷ lệ request nhạy cảm trên tổng số request (`sensitive_request_count / request_count`).
10. `export_count`: Số lần thực hiện thao tác xuất/tải xuống tệp tin.
11. `export_ratio`: Tỷ lệ thao tác xuất dữ liệu (`export_count / request_count`).
12. `delete_count`: Số lần thực hiện thao tác xóa tệp tin.
13. `delete_ratio`: Tỷ lệ thao tác xóa dữ liệu (`delete_count / request_count`).
14. `unique_deleted_resource_count`: Số lượng mã tài nguyên `resource_id` duy nhất bị xóa.
15. `unique_resource_id_count`: Số lượng mã tài nguyên `resource_id` duy nhất được truy cập.
16. `resource_id_request_ratio`: Tỷ lệ đa dạng tài nguyên (`unique_resource_id_count / request_count`).
17. `resource_id_change_rate`: Tỷ lệ thay đổi `resource_id` giữa 2 request liên tiếp.
18. `max_sensitive_streak`: Chuỗi thao tác nhạy cảm liên tiếp dài nhất trong cửa sổ.

#### Nhóm 3: Lỗi phản hồi và Phân quyền (7 đặc trưng)
19. `error_rate`: Tỷ lệ request trả về mã lỗi HTTP $\ge 400$.
20. `avg_response_time_ms`: Thời gian xử lý trung bình của máy chủ (mili-giây).
21. `forbidden_count`: Số lần nhận phản hồi từ chối quyền truy cập (mã 403).
22. `forbidden_rate`: Tỷ lệ lỗi 403 (`forbidden_count / request_count`).
23. `not_found_count`: Số lần nhận phản hồi không tìm thấy tài nguyên (mã 404).
24. `not_found_rate`: Tỷ lệ lỗi 404 (`not_found_count / request_count`).
25. `unique_failed_resource_id_count`: Số lượng `resource_id` duy nhất gây ra lỗi 403 hoặc 404.

---

## CHƯƠNG 4: HUẤN LUYỆN MÔ HÌNH VÀ ĐÁNH GIÁ KẾT QUẢ

### 4.1 Phân chia tập dữ liệu (Train/Validation/Test)
Tập dữ liệu đặc trưng được phân chia bằng cơ chế Group-aware Split theo khóa (`user_id`, `session_id_hash`):
* **Tập Train (Huấn luyện):** Bao gồm các cửa sổ hoàn toàn bình thường (`label = 0`), phục vụ cho mô hình học phân bố chuẩn.
* **Tập Validation (Thẩm định):** Trộn lẫn các cửa sổ Normal và Anomaly, dùng để tinh chỉnh siêu tham số và tìm ngưỡng `threshold` tối ưu.
* **Tập Test (Kiểm thử):** Tập dữ liệu độc lập hoàn toàn, dùng để đánh giá hiệu năng phát hiện cuối cùng.

### 4.2 Quá trình huấn luyện và Tinh chỉnh siêu tham số
File `ml/train.py` thực hiện huấn luyện mô hình Isolation Forest với thuật toán từ thư viện Scikit-Learn:
* **Các tham số cấu hình:** `n_estimators = 200`, `max_samples = 'auto'`, `contamination = 'auto'`, `random_state = 20260706`.
* **Quy trình Tinh chỉnh (Grid Tuning):** Duyệt qua các tổ hợp `n_estimators` (100, 200, 300), `max_samples` ('auto', 256) và `threshold_percentile` (90.0%, 92.5%, 95.0%, 97.5%) trên tập Validation. Cấu hình tối ưu được lựa chọn dựa trên tiêu chí ưu tiên: F1-Score -> FPR -> Recall.
* **Kết quả lưu trữ mô hình:** Mô hình và metadata được đóng gói tại `artifacts/models/iforest_v1/model.joblib` và `model_metadata.json`. Ngưỡng cắt Anomaly Score tối ưu thu được đạt **`threshold = 0.553559`** (`threshold_percentile = 95.0%`).

### 4.3 Kết quả đánh giá thực nghiệm
Kết quả đánh giá thực tế thu được từ file nhật ký đánh giá (`test_metrics.json` và `model_metadata.json`) như sau:

**Bảng 4.1: Kết quả đánh giá mô hình trên tập Validation và Tập Test**

| Chỉ số (Metric) | Tập Validation (6 cửa sổ) | Tập Test (6 cửa sổ) | Diễn giải thực tiễn |
|---|---|---|---|
| **Accuracy** | 83.33% (0.8333) | 66.67% (0.6667) | Tỷ lệ dự đoán đúng trên tổng số cửa sổ thời gian. |
| **Precision** | 100.00% (1.0000) | 66.67% (0.6667) | Trong các cảnh báo phát ra, tỷ lệ cảnh báo là tấn công thực sự. |
| **Recall** | 66.67% (0.6667) | 66.67% (0.6667) | Tỷ lệ nhận diện thành công các đợt tấn công thực tế. |
| **F1-Score** | 80.00% (0.8000) | 66.67% (0.6667) | Trung bình hài hòa giữa Precision và Recall. |
| **FPR (False Positive Rate)** | 0.00% (0.0000) | 33.33% (0.3333) | Tỷ lệ báo động giả trên người dùng bình thường. |

**Bảng 4.2: Ma trận nhầm lẫn (Confusion Matrix) trên Tập Validation (6 cửa sổ)**

| | Dự đoán: Normal (0) | Dự đoán: Anomaly (1) |
|---|---|---|
| **Thực tế: Normal (0)** | TN = 3 | FP = 0 |
| **Thực tế: Anomaly (1)** | FN = 1 | TP = 2 |

*Ghi chú:* Trên tập Validation, mô hình đạt **FPR = 0.00%** và **Precision = 100.00%** (TN = 3, FP = 0, FN = 1, TP = 2), nghĩa là tuyệt đối không báo động nhầm người dùng hợp lệ nào trong đợt thẩm định.

**Bảng 4.3: Ma trận nhầm lẫn (Confusion Matrix) trên Tập Test (6 cửa sổ)**

| | Dự đoán: Normal (0) | Dự đoán: Anomaly (1) |
|---|---|---|
| **Thực tế: Normal (0)** | TN = 2 | FP = 1 |
| **Thực tế: Anomaly (1)** | FN = 1 | TP = 2 |

### 4.4 Phân tích hiệu năng theo Kịch bản
Đánh giá chi tiết khả năng nhận diện theo từng loại kịch bản tấn công:
* **Export Abuse:** Nhận diện xuất sắc với tỷ lệ phát hiện cao, nhờ đặc trưng `export_count` và `export_ratio` có sự khác biệt vượt trội so với phân bố chuẩn.
* **Delete Abuse:** Mô hình nhận diện tốt các chuỗi thao tác xóa dồn dập dựa trên `delete_count` và `unique_deleted_resource_count`.
* **IDOR / BOLA Scan:** Nhận diện các đợt bùng nổ dò quét dựa trên `forbidden_count`, `forbidden_rate` và `unique_failed_resource_id_count`. Các đợt dò quét thong thả (low-and-slow) tạo ra Anomaly Score tiệm cận ngưỡng cutoff nên có trường hợp bị bỏ sót (FN = 1).

---

## CHƯƠNG 5: TRIỂN KHAI HỆ THỐNG VÀ KIẾN TRÚC TÍCH HỢP

### 5.1 Luồng xử lý toàn hệ thống (Pipeline)
Hệ thống StudyDrive được tích hợp theo quy trình xử lý dữ liệu khép kín:
1. **Ghi log tự động:** Lớp Flask Middleware (`app/middleware/request_logging.py`) tự động bắt mọi request và ghi vào bảng `request_logs`.
2. **Kích hoạt Detection:** Quản trị viên kích hoạt tiến trình phát hiện từ giao diện Admin (nút "Run Detection") hoặc CLI (`python -m scripts.run_detection`).
3. **Trích xuất & Dự đoán:** `detection_service.py` đọc các log mới, gom nhóm cửa sổ 5 phút, tính 25 đặc trưng, nạp mô hình `model.joblib` để tính Anomaly Score và so sánh với ngưỡng `threshold`.
4. **Lưu Alert & Phản ứng:** Cảnh báo được lưu vào bảng `alerts`. Nếu Anomaly Score > 0.7 hoặc thuộc kịch bản nguy hiểm, tài khoản bị tự động khóa 60 phút.

### 5.2 Cơ chế Phản ứng chủ động (Active Defense)
Cơ chế bảo mật chủ động được triển khai kết hợp giữa `detection_service.py` và Middleware `active_defense.py`:
* **Tự động khóa tài khoản (`locked_until`):** Trong tiến trình Detection, nếu một cửa sổ bị đánh dấu bất thường có Anomaly Score > 0.7 hoặc thuộc kịch bản tấn công (`bola_scan`, `export_abuse`, `delete_abuse`), hệ thống tự động gán `user.locked_until = now() + 60 phút`.
* **Tự động chặn Request (HTTP 403):** Lớp Middleware `active_defense.py` kiểm tra mọi request của người dùng đã đăng nhập. Nếu `user.locked_until > now()`, request lập tức bị ngắt và phản hồi `HTTP 403 Forbidden` kèm thông báo tài khoản tạm thời bị khóa do phát hiện hành vi bất thường.

### 5.3 Giao diện Quản trị và Trực quan hóa
* **Hộp thoại Thông báo Kết quả (Modal Popup):** Khi bấm "Run Detection", Modal hiện ra với tông màu pastel đồng bộ, báo cáo nhanh: Số cửa sổ đã quét, Số bất thường phát hiện, Số cảnh báo mới tạo và Số cảnh báo trùng lặp.
* **Biểu đồ Tròn Thống kê Kịch bản (Doughnut Chart):** Tích hợp thư viện Chart.js trực quan hóa tỷ lệ các kịch bản tấn công ngay trong card "Thống kê Kịch bản Tấn công".
* **Cơ chế Truy vết Log gốc (Forensics):** Khi bấm vào chi tiết một Alert, hệ thống tự động trích xuất các tham số định vị (`user_id`, `session_id_hash`, `window_start`, `window_end`) và chuyển hướng sang trang Admin Logs Filtered, cho phép Admin rà soát chính xác từng HTTP Request thô trong cửa sổ 5 phút bị đánh dấu.

### 5.4 Kiểm thử tự động (Test Suite Pytest)
Hệ thống được đảm bảo độ tin cậy thông qua bộ kiểm thử tự động Pytest trong thư mục `tests/`:
* Bộ kiểm thử bao gồm các bài test bao phủ toàn bộ luồng: Authentication, File Management, Structured Logging, Feature Extraction, Detection Service, Active Defense Middleware và Admin Dashboard.
* **Kết quả thực thi Pytest:** Đạt **`38 passed in 24.94s`** (tỷ lệ thành công tuyệt đối **100%**).

---

## CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 6.1 Kết quả đạt được
* **Ứng dụng Web & Structured Logging:** Đã hoàn thiện ứng dụng StudyDrive với tính năng quản lý, lưu trữ, chia sẻ tài liệu và hệ thống Structured Logging tự động ghi nhận 27 trường dữ liệu kèm băm SHA-256 an toàn.
* **Pipeline Machine Learning khép kín:** Xây dựng thành công quy trình xử lý dữ liệu từ log thô -> gom nhóm cửa sổ 5 phút -> trích xuất 25 đặc trưng số -> huấn luyện mô hình Isolation Forest theo chiến lược Normal-only và Group-aware Split.
* **Cơ chế Phản ứng chủ động (Active Defense):** Tích hợp thành công tính năng tự động khóa tài khoản nghi ngờ 60 phút (`locked_until`) và chặn HTTP 403 tại Middleware, giúp giảm thiểu thiệt hại tức thì.
* **Giao diện Quản trị & Trực quan hóa:** Hoàn thiện Alerts Dashboard tích hợp Modal Popup, Biểu đồ tròn Chart.js và tính năng truy vết Log gốc.
* **Kiểm thử tự động:** Vượt qua bộ kiểm thử 38/38 test cases Pytest pass 100%.

### 6.2 Hạn chế
* **Quy mô dữ liệu thực nghiệm:** Tập dữ liệu thực nghiệm còn mang tính chất thử nghiệm sơ bộ (Proof-of-Concept) trên môi trường mô phỏng.
* **Độ trễ xử lý:** Hệ thống xử lý theo chế độ Batch (On-demand/Trigger) nên tiến trình phát hiện có độ trễ nhất định so với thời gian thực.
* **Phân loại kịch bản:** Thuật toán Isolation Forest là mô hình học không giám sát nên chỉ tính điểm bất thường chung (Anomaly Score); việc gán nhãn kịch bản (`scenario_hint`) vẫn dựa trên quy tắc phân tích đặc trưng nổi trội (Post-hoc Rule-based Analysis).
* **Phạm vi quản trị:** Hệ thống hiện phục vụ trong phạm vi 1 tổ chức (Single-tenant).

### 6.3 Hướng phát triển
* **Chuyển đổi sang kiến trúc Thời gian thực (Real-time Streaming):** Tích hợp Message Broker (Apache Kafka/RabbitMQ) và Celery Workers để phân tích log theo thời gian thực ngay khi request phát sinh.
* **Kết hợp mô hình Học có giám sát (Multi-stage Detection):** Kết hợp Isolation Forest (phát hiện bất thường chung) với mô hình học có giám sát (Random Forest, XGBoost) để phân loại chính xác kịch bản tấn công.
* **Mở rộng Đa tổ chức (Multi-tenancy):** Phát triển hệ thống hỗ trợ nhiều trường học/doanh nghiệp cùng sử dụng, phân tách dữ liệu và nhật ký log theo từng Tenant riêng biệt.

---

## TÀI LIỆU THAM KHẢO
[1] F. T. Liu, K. M. Ting, và Z. H. Zhou, "Isolation Forest," trong *2008 Eighth IEEE International Conference on Data Mining*, 2008, tr. 413-422, doi: 10.1109/ICDM.2008.17.  
[2] OWASP Foundation, "OWASP Top 10:2021 - A01:2021-Broken Access Control & A04:2021-Insecure Design," *OWASP Top 10 Web Application Security Risks*, 2021. [Trực tuyến]. Địa chỉ: https://owasp.org/Top10/. [Truy cập: 09/08/2026].  
[3] V. Chandola, A. Banerjee, và V. Kumar, "Anomaly detection: A survey," *ACM Computing Surveys (CSUR)*, vol. 41, no. 3, tr. 1-58, 2009, doi: 10.1145/1541880.1541882.  
[4] Scikit-Learn Developers, "sklearn.ensemble.IsolationForest Documentation," *Scikit-Learn API Reference*, 2023. [Trực tuyến]. Địa chỉ: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html. [Truy cập: 09/08/2026].  
[5] F. Pedregosa et al., "Scikit-learn: Machine learning in Python," *Journal of Machine Learning Research*, vol. 12, tr. 2825-2830, 2011.  
[6] D. Stuttard và M. Pinto, *The Web Application Hacker's Handbook: Finding and Exploiting Security Flaws*, ấn bản 2. John Wiley & Sons, 2011.  
[7] A. L. Buczak và E. Guven, "A survey of data mining and machine learning methods for cyber intrusion detection," *IEEE Transactions on Cybernetics / Communications Surveys & Tutorials*, vol. 18, no. 2, tr. 1153-1176, 2015, doi: 10.1109/COMST.2015.2494502.  
