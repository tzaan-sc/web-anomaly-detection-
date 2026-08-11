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
Em xin cam đoan đồ án “Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning” là công trình nghiên cứu của riêng em dưới sự hướng dẫn của Ths. Nguyễn Trung Kiên.
Các nội dung, số liệu, kết quả và sản phẩm được trình bày trong đồ án hoàn toàn do em tự thực hiện. Các tài liệu tham khảo, trích dẫn trong đồ án đều được ghi rõ nguồn gốc và tuân thủ đúng quy định về trích dẫn tại phần Tài liệu tham khảo.
Em xin chịu hoàn toàn trách nhiệm về tính trung thực và nội dung của đồ án này trước khoa và nhà trường.

## LỜI CẢM ƠN
Lời đầu tiên, nhóm xin gửi lời tri ân sâu sắc đến quý thầy, cô giảng viên trường Trường Đại Học Kỹ Thuật – Công Nghệ Cần Thơ. Em đã nhận được sự giảng dạy tận tình, những kiến thức chuyên môn được tiếp thu được trên giảng đường chính là hành trang vững chắc để em thực hiện đồ án này.

Đặc biệt, em xin gửi lời cảm ơn chân thành nhất đến giảng viên hướng dẫn Ths. Nguyễn Trung Kiên. Trong suốt thời gian làm đồ án, thầy không chỉ định hướng đề tài mà còn hỗ trợ em rất nhiều trong việc tiếp cận và tháo gỡ những vướng mắc. Sự hỗ trợ, góp ý và định hướng của thầy là nguồn động lực to lớn giúp chúng em hoàn thiện sản phẩm và tích lũy thêm nhiều kinh nghiệm quý báu.

Dù đã nỗ lực hoàn thiện, song do kiến thức và kinh nghiệm còn hạn chế, đồ án khó tránh khỏi những hạn chế. Em rất mong nhận được sự góp ý, chỉ bảo của quý thầy cô để có thể rút kinh nghiệm, hoàn thiện hơn trong những đồ án và công việc sau này.

Em xin chân thành cảm ơn!

## TÓM TẮT ĐỒ ÁN
Đồ án Công nghệ thông tin 3 của nhóm với đề tài “Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning” được thực hiện nhằm giải quyết bài toán bảo mật ở tầng ứng dụng (Application Layer), cụ thể là các rủi ro liên quan đến Lạm dụng logic nghiệp vụ (Business Logic Abuse) và lỗ hổng Kiểm soát truy cập đối tượng (BOLA/IDOR). Hệ thống được triển khai tích hợp trực tiếp trên một ứng dụng chia sẻ tài liệu trực tuyến tự phát triển mang tên StudyDrive.

Thay vì sử dụng các luật tĩnh (static rules) cứng nhắc, đề tài áp dụng thuật toán học máy không giám sát Isolation Forest để phân tích các bản ghi nhật ký (log) truy cập định kỳ. Dữ liệu thô được thu thập, trích xuất thành vector đặc trưng 25 chiều (với 11 đặc trưng toán học cốt lõi) trong các cửa sổ thời gian 5 phút. Kết quả thực nghiệm cho thấy mô hình có khả năng nhận diện chính xác 100% đối với các kịch bản xuất dữ liệu hàng loạt (Export Abuse) và phản ứng tốt với hành vi xóa phá hoại (Delete Abuse). Đồ án cung cấp một hướng tiếp cận thực tiễn trong việc kết hợp phát triển Web và Trí tuệ nhân tạo để nâng cao an toàn thông tin cho hệ thống.

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
Trong những năm gần đây, các ứng dụng web ngày càng được sử dụng rộng rãi để cung cấp nhiều loại dịch vụ trực tuyến, trong đó có các hệ thống lưu trữ và chia sẻ tệp tin. Người dùng có thể thực hiện nhiều thao tác trực tiếp trên nền tảng web như tải lên, tải xuống, chia sẻ, đổi tên, di chuyển, xuất dữ liệu và quản lý tệp tin mà không cần cài đặt phần mềm chuyên dụng. Sự đa dạng về chức năng giúp nâng cao tính tiện lợi và hiệu quả sử dụng, nhưng đồng thời cũng đặt ra yêu cầu ngày càng cao về khả năng bảo vệ dữ liệu và kiểm soát các hành vi truy cập bất thường trên hệ thống.

Trong các hệ thống web, không phải mọi hành vi nguy hiểm đều biểu hiện dưới dạng một yêu cầu HTTP sai cú pháp hoặc một mẫu tấn công đã được xác định trước. Một số hành vi lạm dụng logic nghiệp vụ vẫn có thể sử dụng các HTTP Request hoàn toàn hợp lệ, chẳng hạn như liên tục xuất dữ liệu, thực hiện nhiều thao tác xóa tệp trong thời gian ngắn hoặc liên tiếp thay đổi mã tài nguyên để kiểm tra quyền truy cập vào các tài nguyên không thuộc sở hữu. Những hành vi này có thể gây ra các nguy cơ như thất thoát dữ liệu, phá hoại dữ liệu hoặc làm lộ các tài nguyên riêng tư. Trong khi đó, các cơ chế phát hiện dựa chủ yếu trên chữ ký hoặc các quy tắc cố định có thể gặp khó khăn khi nhận biết những hành vi bất thường ở cấp độ nghiệp vụ.

Từ thực tế đó, việc thu thập và phân tích nhật ký truy cập của ứng dụng web có thể cung cấp cơ sở để nhận diện những thay đổi bất thường trong hành vi sử dụng hệ thống. Machine Learning, đặc biệt là các phương pháp học không giám sát, có khả năng học đặc điểm của hành vi bình thường từ dữ liệu truy cập và xác định những mẫu có biểu hiện khác biệt. Cách tiếp cận này phù hợp với bài toán khi việc thu thập đầy đủ dữ liệu đã được gán nhãn cho tất cả các dạng hành vi tấn công là khó thực hiện.

Xuất phát từ yêu cầu xây dựng một hệ thống web có khả năng thu thập dữ liệu truy cập và hỗ trợ phát hiện hành vi bất thường, nhóm lựa chọn đề tài **“Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning”**. Trong đề tài, nhóm xây dựng ứng dụng lưu trữ và chia sẻ tệp tin StudyDrive, đồng thời tích hợp cơ chế ghi nhật ký truy cập tại tầng Middleware. Các nhật ký được thu thập từ quá trình vận hành và mô phỏng tương tác trên ứng dụng, sau đó được gom thành các cửa sổ thời gian 5 phút và chuyển thành vector gồm 25 đặc trưng phục vụ cho quá trình phân tích.

Trên cơ sở dữ liệu thu thập được, mô hình Isolation Forest được sử dụng để học phân bố hành vi bình thường và tính điểm bất thường cho từng cửa sổ truy cập. Hệ thống tập trung vào ba kịch bản bất thường gồm Export Abuse, Delete Abuse và IDOR/BOLA Scan. Kết quả phát hiện được tích hợp trở lại giao diện quản trị, cho phép Admin theo dõi cảnh báo, xem điểm bất thường, các đặc trưng liên quan và truy ngược về những request log gốc trong cửa sổ thời gian tương ứng. Qua đó, đề tài hướng đến việc xây dựng một quy trình khép kín từ thu thập log – trích xuất đặc trưng – phát hiện bất thường – tạo cảnh báo – hỗ trợ truy vết, thay vì chỉ lưu trữ nhật ký để tra cứu thủ công sau khi sự cố xảy ra.

---

## CHƯƠNG 1: TỔNG QUAN

### 1.1 Lý do chọn đề tài
Trong quá trình chuyển đổi số, các ứng dụng Web hỗ trợ lưu trữ, quản lý và chia sẻ tài liệu trực tuyến ngày càng được sử dụng rộng rãi trong học tập, công việc và hoạt động của các cá nhân, tổ chức. Các hệ thống này không chỉ cung cấp những chức năng cơ bản như tải lên, tải xuống, chia sẻ và quản lý tệp tin mà còn xử lý một lượng lớn yêu cầu truy cập từ người dùng. Vì vậy, bên cạnh yêu cầu về tính tiện dụng và khả năng quản lý dữ liệu, vấn đề bảo đảm an toàn cho các hoạt động truy cập và sử dụng tài nguyên trên hệ thống Web ngày càng trở nên quan trọng.

Một trong những vấn đề đáng quan tâm là việc người dùng hoặc kẻ tấn công có thể lạm dụng những chức năng hợp lệ của ứng dụng để thực hiện các hành vi bất thường. Khác với những cuộc tấn công thể hiện rõ qua các payload hoặc mẫu truy cập đặc trưng, các hành vi này có thể sử dụng tài khoản hợp lệ và gửi các HTTP Request hoàn toàn hợp lệ về mặt cú pháp. Tuy nhiên, khi được thực hiện với tần suất hoặc trình tự bất thường, chúng có thể dẫn đến những rủi ro như thất thoát dữ liệu, phá hoại tài nguyên hoặc dò quét trái phép các tài nguyên của người dùng khác.

Các cơ chế bảo mật truyền thống như Web Application Firewall (WAF) hoặc Intrusion Detection System (IDS) thường phát huy hiệu quả đối với những hành vi có mẫu hoặc chữ ký tấn công đã biết. Tuy nhiên, đối với Business Logic Abuse và Broken Object Level Authorization (BOLA) / Insecure Direct Object Reference (IDOR), bản thân HTTP Request có thể không chứa dấu hiệu bất thường rõ ràng. Do đó, chỉ dựa vào nội dung của từng request riêng lẻ có thể không đủ để nhận diện hành vi nguy hiểm.

Bên cạnh đó, việc xây dựng các quy tắc cố định để phát hiện hành vi bất thường có thể trở nên cứng nhắc khi hành vi của người dùng thay đổi. Một quy tắc đặt ngưỡng số lượng request hoặc thao tác trong một khoảng thời gian có thể bỏ sót những hành vi được thực hiện chậm hoặc tạo ra cảnh báo nhầm đối với những người dùng hợp lệ có tần suất thao tác cao. Vì vậy, đề tài lựa chọn hướng tiếp cận phát hiện bất thường dựa trên Machine Learning, cụ thể là mô hình Isolation Forest, nhằm phân tích đặc trưng hành vi được tổng hợp từ nhật ký truy cập và xác định những mẫu có mức độ khác biệt so với hành vi thông thường.

Từ những vấn đề trên, đề tài “Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning” được thực hiện với môi trường ứng dụng Web StudyDrive. Hệ thống không chỉ xây dựng một mô hình Machine Learning độc lập mà hướng đến một quy trình khép kín gồm thu thập nhật ký truy cập, xây dựng đặc trưng hành vi, phát hiện bất thường, tạo cảnh báo và hỗ trợ quản trị viên truy ngược về các request log liên quan.

### 1.2 Mục tiêu nghiên cứu
Mục tiêu cốt lõi của đồ án là xây dựng ứng dụng Web StudyDrive tích hợp hệ thống ghi nhật ký truy cập có cấu trúc và mô hình Machine Learning không giám sát Isolation Forest, nhằm phát hiện các hành vi truy cập bất thường liên quan đến lạm dụng logic nghiệp vụ và truy cập tài nguyên trái phép. Hệ thống hướng đến khả năng tự động ghi nhận các HTTP Request, tổng hợp chuỗi hành vi theo cửa sổ thời gian, chuyển đổi dữ liệu log thành các đặc trưng phục vụ mô hình, tính toán điểm bất thường và tạo cảnh báo để quản trị viên theo dõi, kiểm tra và truy ngược về các log gốc. 

Đề tài tập trung thực hiện các mục tiêu cụ thể sau:
* Xây dựng ứng dụng Web StudyDrive với các chức năng quản lý, lưu trữ, chia sẻ và xuất tệp tin; hỗ trợ cơ chế phân quyền ở cấp đối tượng với hai quyền chính là OWNER và VIEWER.
* Xây dựng hệ thống Structured Request Logging tại tầng Middleware của Flask nhằm tự động ghi nhận các HTTP Request và các thông tin liên quan như người dùng, phiên làm việc, hành động, tài nguyên, kết quả phân quyền, mã trạng thái HTTP và thời gian xử lý.
* Bảo đảm an toàn đối với dữ liệu nhật ký, trong đó không lưu mật khẩu, CSRF token hoặc session ID nguyên bản; session ID được xử lý dưới dạng mã băm SHA-256 trước khi lưu vào log.
* Xây dựng dữ liệu phục vụ huấn luyện và kiểm thử thông qua các script mô phỏng hành vi bình thường và ba kịch bản bất thường gồm:
  * Export Abuse (Lạm dụng tính năng xuất dữ liệu)
  * Delete Abuse (Lạm dụng tính năng xóa tệp tin)
  * IDOR / BOLA Scan (Dò quét lỗ hổng Kiểm soát truy cập)
* Xây dựng Pipeline xử lý dữ liệu, trong đó các request log được gom nhóm theo cửa sổ thời gian 5 phút dựa trên người dùng và phiên làm việc, sau đó được chuyển đổi thành vector đặc trưng phục vụ phát hiện bất thường.
* Xây dựng và huấn luyện mô hình Isolation Forest theo hướng học không giám sát, sử dụng dữ liệu hành vi bình thường làm cơ sở để xác định những mẫu dữ liệu có mức độ bất thường cao.
* Tinh chỉnh mô hình và ngưỡng phát hiện, thực hiện phân chia dữ liệu Train/Validation/Test theo nhóm để hạn chế hiện tượng rò rỉ dữ liệu trong quá trình đánh giá.
* Tích hợp mô hình Machine Learning vào hệ thống Web, cho phép quản trị viên kích hoạt tiến trình Detection từ giao diện quản trị và nhận kết quả phát hiện dưới dạng cảnh báo.
* Xây dựng giao diện quản trị Log và Alert, hỗ trợ tìm kiếm, lọc log, xem thông tin cảnh báo, xem điểm bất thường, gợi ý kịch bản và truy ngược về các request log gốc.
* Đánh giá và kiểm thử hệ thống, sử dụng các chỉ số Accuracy, Precision, Recall, F1-Score, False Positive Rate và Confusion Matrix.

### 1.3 Đối tượng & Phạm vi nghiên cứu

#### Đối tượng nghiên cứu
* Tập hợp các bản ghi HTTP Request Log được thu thập trực tiếp tại tầng ứng dụng của nền tảng web StudyDrive.
* Chuỗi hành vi truy cập của người dùng trên hệ thống, được hệ thống số hóa và biểu diễn qua vector đặc trưng định lượng được giới hạn trong cửa sổ thời gian 5 phút.
* Thuật toán phát hiện bất thường học không giám sát Isolation Forest cùng với quy trình xử lý dữ liệu chuỗi thời gian (time-window feature engineering).

#### Phạm vi nghiên cứu
* **Phạm vi kịch bản phát hiện:** Hệ thống tập trung nghiên cứu và nhận diện 3 kịch bản lạm dụng logic nghiệp vụ chính:
  * **Export Abuse:** Kẻ tấn công gửi liên tục từ 30 đến 50 request yêu cầu xuất dữ liệu dạng CSV/ZIP trong vòng 5 phút.
  * **Delete Abuse:** Kẻ xấu gửi liên tục khoảng 30 request yêu cầu xóa tệp tin hàng loạt trong giới hạn 5 phút.
  * **IDOR/BOLA Scan:** Các đối tượng gửi từ 100 đến 500 request nhằm truy cập các file_id được tăng dần đều nhưng không thuộc quyền sở hữu, từ đó tạo ra một chuỗi các phản hồi lỗi 403 (Forbidden) và 404 (Not Found).
* **Phạm vi kỹ thuật:** Hệ thống Machine Learning hiện tại được thiết kế để xử lý theo cơ chế Batch Processing (tức là định kỳ chạy phân tích trên tập log đã được gom nhóm 5 phút) và chưa triển khai xử lý luồng theo thời gian thực (Real-time Streaming). Bên cạnh đó, hệ thống tập trung vào việc phát cảnh báo (Alert Generation) để quản trị viên có thể kiểm tra thủ công, chưa tiến hành tự động kích hoạt các cơ chế như chặn IP hay khóa tài khoản.
* **Môi trường thực nghiệm:** Hệ thống được tích hợp trên StudyDrive, một ứng dụng Web thu nhỏ quản lý tài liệu trực tuyến do em tự phát triển. Ứng dụng cung cấp các tính năng cơ bản như Upload, Download, Tạo thư mục, Xóa, Chia sẻ quyền VIEWER.
* **Đối tượng phân tích:** Log truy cập (Request Logs) sinh ra từ các thao tác của người dùng đã đăng nhập (Authenticated Users). Hệ thống không phân tích truy cập ẩn danh.
* **Phạm vi quản trị:** Cung cấp giao diện Admin Dashboard để quản trị viên theo dõi log, chạy quy trình phát hiện (Detection Pipeline) và xử lý cảnh báo (Alerts).
* **Phạm vi phát hiện bất thường tập trung vào ba kịch bản:**
  * **Export Abuse (Lạm dụng tính năng xuất dữ liệu):** Nhận diện các hành vi yêu cầu xuất siêu dữ liệu (metadata) hoặc tải xuống hàng loạt (Export ZIP/CSV) vượt quá nhu cầu sử dụng thông thường. Đây là dấu hiệu của rủi ro thất thoát dữ liệu (Data Exfiltration) thường do nội gián hoặc tài khoản bị lộ lọt mật khẩu gây ra.
  * **Delete Abuse (Lạm dụng tính năng xóa tệp tin):** Phát hiện các chuỗi thao tác xóa mềm (soft-delete) hàng loạt trên nhiều tài nguyên khác nhau trong thời gian ngắn. Mục tiêu nhằm ngăn chặn kẻ xấu có ý đồ phá hoại (Sabotage) sau khi đã chiếm đoạt được tài khoản (Account Takeover).
  * **IDOR / BOLA Scan (Dò quét lỗ hổng Kiểm soát truy cập):** Phát hiện các công cụ tự động hoặc thao tác thủ công cố tình thay đổi tham số resource_id trên các URL/API nhằm truy cập trái phép vào các tệp tin không thuộc quyền sở hữu (Broken Object Level Authorization).
* Hệ thống Machine Learning hiện tại xử lý theo BatchProcessing/Trigger, sử dụng cửa sổ 5 phút không chồng lấp và chưa thực hiện phát hiện theo luồng thời gian thực.
* Hệ thống chỉ tạo cảnh báo để quản trị viên giám sát và rà soát thủ công; chưa có cơ chế tự động khóa tài khoản hoặc chặn IP.

### 1.4 Phương pháp nghiên cứu
Để giải quyết bài toán đã đặt ra, đề tài kết hợp các phương pháp nghiên cứu sau:
* **Nghiên cứu lý thuyết:** Tiến hành phân tích sâu sắc tài liệu OWASP API Security Top 10 (đặc biệt chú trọng vào lỗ hổng BOLA/IDOR), tìm hiểu nguyên lý toán học của thuật toán Isolation Forest và các kỹ thuật Feature Engineering tiên tiến trên dữ liệu log web.
* **Thực nghiệm xây dựng phần mềm:** Áp dụng các công nghệ hiện đại để phát triển ứng dụng StudyDrive, bao gồm nền tảng Flask, ORM SQLAlchemy, Template Engine Jinja2 và thư viện giao diện Bootstrap 5.
* **Thực nghiệm giả lập & thu thập dữ liệu:** Sử dụng thư viện requests của ngôn ngữ Python nhằm tạo ra các kịch bản mô phỏng đa dạng, từ truy cập hợp lệ đến bất thường, qua đó thu thập thành công 10.867 bản ghi log thô.
* **Phân tích & Huấn luyện:** Tiến hành tiền xử lý dữ liệu chuyên sâu, trích xuất 25 đặc trưng số. Đề tài thực hiện chia tập dữ liệu bằng phương pháp Group-aware Split theo run_id, huấn luyện mô hình Isolation Forest trên tập Train (chỉ bao gồm hành vi bình thường) và thực hiện tinh chỉnh siêu tham số (Hyperparameter Tuning) trên tập Validation.
* **Đánh giá & Tích hợp:** Thực hiện kiểm thử định lượng đối với mô hình trên tập Test độc lập, đồng thời xây dựng một bộ kiểm thử tự động chuyên nghiệp bằng Pytest với 34 test cases nhằm đảm bảo tính ổn định của hệ thống.

### 1.5 Cấu trúc đồ án
Đồ án được tổ chức một cách logic thành 6 chương như sau:
* **Chương 1: Tổng quan** - Trình bày chi tiết lý do chọn đề tài, mục tiêu hướng tới, đối tượng, phạm vi giới hạn, phương pháp nghiên cứu và cấu trúc báo cáo.
* **Chương 2: Cơ sở lý thuyết** - Cung cấp nền tảng kiến thức về logging tầng ứng dụng, Business Logic Abuse, lỗ hổng BOLA/IDOR, khái niệm cửa sổ thời gian, chiến lược Normal-only Training, thuật toán Isolation Forest, kỹ thuật Feature Engineering, vấn đề Data Leakage và các công thức đánh giá.
* **Chương 3: Thu thập dữ liệu và Xây dựng đặc trưng** - Đi sâu vào chi tiết môi trường thực nghiệm, cấu trúc request log thô, 4 kịch bản giả lập hành vi, các bước tiền xử lý dữ liệu và trình bày chi tiết danh sách 25 đặc trưng số chia thành 3 nhóm.
* **Chương 4: Huấn luyện mô hình và Đánh giá kết quả** - Phân tích thiết kế chia tập Train/Validation/Test, làm rõ quá trình tinh chỉnh siêu tham số, phân tích kết quả đánh giá định lượng, trực quan hóa dữ liệu và trình bày các hạn chế gặp phải.
* **Chương 5: Triển khai hệ thống và Kiến trúc tích hợp** - Mô tả cặn kẽ luồng xử lý toàn hệ thống (Pipeline), cơ chế phát hiện tự động, giao diện quản trị Alerts Dashboard và khả năng truy vết log gốc.
* **Chương 6: Kết luận và Hướng phát triển** - Đưa ra tổng kết về những kết quả đã đạt được, nhìn nhận các hạn chế còn tồn tại và đề xuất các hướng nâng cấp khả thi trong tương lai.

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

### 2.1 Logging tại tầng ứng dụng
#### Structured Request Logging
Logging đóng vai trò là nền tảng cốt lõi cho mọi công tác giám sát an toàn thông tin hệ thống. Khác biệt với phương pháp Unstructured Logging (chỉ ghi nhận lại các chuỗi văn bản tự do), Structured Request Logging lưu trữ thông tin truy cập dưới dạng các bản ghi có cấu trúc minh bạch với các trường được định nghĩa sẵn (chẳng hạn như `timestamp`, `user_id`, `endpoint`, `status_code`, `response_time_ms`...). Dữ liệu log được cấu trúc hóa một cách chặt chẽ cho phép các thuật toán Machine Learning có thể đọc và trích xuất đặc trưng tự động một cách dễ dàng mà không cần phải trải qua các bước bóc tách cú pháp (parsing) phức tạp và tốn kém tài nguyên.
Trong kiến trúc của Flask Framework, quá trình logging tại tầng ứng dụng được triển khai thông qua hook `@app.after_request`. Cơ chế mạnh mẽ này cho phép hệ thống bắt giữ toàn bộ các thông tin của request cũng như response ngay lập tức sau khi xử lý xong các nghiệp vụ.

#### Bảo mật thông tin nhạy cảm trong log
Log truy cập hoàn toàn có nguy cơ trở thành mục tiêu tấn công nếu lưu trữ các thông tin định danh nhạy cảm của người dùng. Do đó, hệ thống áp dụng các nguyên tắc bảo mật vô cùng nghiêm ngặt:
* **Không ghi dữ liệu thô:** Các dữ liệu như mật khẩu plaintext, CSRF token hay Session ID nguyên bản tuyệt đối không được phép ghi vào database log.
* **Băm SHA-256 cho Session ID:** Mã phiên làm việc phải được băm thông qua hàm mã hóa SHA-256 (`session_id_hash`), từ đó đảm bảo tính ẩn danh cao và khiến kẻ tấn công không thể khôi phục được session ID gốc từ dữ liệu log.
* **Xử lý ngoại lệ an toàn:** Toàn bộ quá trình ghi log đều được bao bọc cẩn thận trong khối lệnh `try...except`, điều này nhằm đảm bảo rằng ngay cả khi cơ sở dữ liệu log gặp sự cố bất ngờ, các request của người dùng vẫn sẽ được phản hồi một cách bình thường.

### 2.2 Hành vi bất thường và Business Logic Abuse
#### Định nghĩa và phân loại
Trong lĩnh vực an toàn thông tin ứng dụng web, Business Logic Abuse (tức Lạm dụng logic nghiệp vụ) được xem là loại hình tấn công mà kẻ xấu lợi dụng chính các chức năng hoàn toàn hợp lệ của ứng dụng nhưng thực thi theo những cách thức hoặc tần suất không được lường trước nhằm phục vụ mục đích xấu (chẳng hạn như thu thập dữ liệu trái phép, làm cạn kiệt tài nguyên hệ thống hoặc thao tác xóa/sửa dữ liệu hàng loạt).
Sự khác biệt lớn nhất giữa loại hình này so với các cuộc tấn công kỹ thuật thuần túy (như SQL Injection hay Cross-Site Scripting - XSS) vốn dĩ vi phạm cú pháp dữ liệu đầu vào, là các tấn công logic sở hữu cú pháp HTTP Request hoàn toàn chuẩn xác và đúng định dạng.

#### Lỗ hổng BOLA/IDOR
Theo báo cáo phân tích của tài liệu OWASP API Security Top 10 (2023), lỗ hổng API1:2023 Broken Object Level Authorization (BOLA) — thường được biết đến với tên gọi IDOR (Insecure Direct Object Reference) — đang được xếp hạng ở vị trí số 1 về mức độ nguy hiểm đối với hệ thống.
Lỗ hổng này phát sinh khi ứng dụng web cung cấp một tham chiếu trực tiếp đến đối tượng tài nguyên (ví dụ như `file_id` hoặc `user_id`) ngay trong đường dẫn URL nhưng lại không thực hiện kiểm tra một cách chặt chẽ về quyền sở hữu ở phía máy chủ (backend). Kẻ tấn công có thể lợi dụng điều này bằng cách thay đổi tuần tự các ID (ví dụ: `/documents/view?file_id=101, 102, 103...`) để từ đó có thể truy xuất trái phép dữ liệu nhạy cảm của người dùng khác.

#### Hạn chế của phương pháp phát hiện truyền thống (WAF/IDS)
Các hệ thống phòng thủ mạng truyền thống như WAF (Web Application Firewall) hoặc IDS (Intrusion Detection System) thường được xây dựng chủ yếu dựa trên các quy tắc tĩnh (Signature-based / Rule-based). Phương pháp phòng vệ này bộc lộ những hạn chế rất lớn khi phải đối mặt với Business Logic Abuse:
* **Không phát hiện được request hợp lệ:** Hệ thống WAF sẽ xem mỗi request riêng lẻ là hoàn toàn hợp lệ do chúng không chứa các mẫu mã độc (signature) đã biết.
* **Dễ bị vượt qua ngưỡng tĩnh:** Kẻ tấn công sành sỏi chỉ cần tinh chỉnh để giảm tốc độ truy cập tự động, qua đó luôn nằm dưới ngưỡng cảnh báo cố định mà WAF đã thiết lập.
* **Chi phí duy trì luật cao:** Đội ngũ quản trị phải thực hiện cập nhật luật thủ công liên tục mỗi khi hệ thống có một chức năng mới được triển khai.

### 2.3 Khái niệm Cửa sổ thời gian (Time Window) trong phân tích chuỗi hành vi
Hành vi tương tác của người dùng trên nền tảng web luôn là một chuỗi các sự kiện có tính nối tiếp liên tục theo dòng thời gian. Một request đơn lẻ không bao giờ có thể phản ánh đầy đủ ý đồ thực sự của người dùng. Do đó, kỹ thuật Cửa sổ thời gian (Time Windowing) đã được áp dụng nhằm mục đích gom nhóm toàn bộ các request xảy ra trong một khoảng thời gian Δt=5 phút của cùng một phiên người dùng (`user_id`, `session_id_hash`). 
Việc tập trung phân tích trên cửa sổ 5 phút mang lại những ưu điểm: 
* Giúp hệ thống tích lũy đủ lượng dữ liệu cần thiết để có thể tính toán các chỉ số thống kê quan trọng (như tốc độ truy cập, tỷ lệ lỗi, độ đa dạng tài nguyên). 
* Hỗ trợ nhận diện rõ ràng các mẫu hành vi đột biến (burst pattern) vốn là đặc trưng của các công cụ rà quét tự động.

### 2.4 Học không giám sát và Normal-only Training
Trong việc giải quyết bài toán phát hiện bất thường về an ninh mạng, quá trình xử lý dữ liệu thực tế thường xuyên đối mặt với hai thách thức lớn: 
* Dữ liệu biểu hiện sự tấn công thường rất hiếm khi so sánh với tập dữ liệu truy cập bình thường, dẫn đến tình trạng mất cân bằng dữ liệu cực kỳ nghiêm trọng. 
* Các hình thái tấn công logic mới luôn xuất hiện liên tục và hệ thống chưa hề có nhãn trước để phân loại. 

Chính vì lý do đó, đồ án này đã lựa chọn hướng tiếp cận Học không giám sát (Unsupervised Learning) kết hợp với chiến lược Normal-only Training. Mô hình sẽ chỉ được học duy nhất trên tập dữ liệu chứa các cửa sổ hành vi bình thường. Bằng cách này, mô hình tự động xây dựng ranh giới phân bố biểu diễn cho "trạng thái bình thường". Bất cứ khi nào hệ thống bắt gặp một cửa sổ mới có bộ đặc trưng nằm ngoài phân bố đã học, mô hình sẽ lập tức đánh giá và gán nhãn đó là một cửa sổ bất thường.

### 2.5 Thuật toán Isolation Forest
#### Cơ chế hoạt động
Isolation Forest (hay gọi tắt là iForest) là một thuật toán học máy không giám sát, được nghiên cứu và thiết kế chuyên biệt để phục vụ bài toán phát hiện bất thường (Liu et al., 2008). Cơ sở lý thuyết của thuật toán dựa trên một nguyên lý cốt lõi: các điểm dữ liệu bất thường thường có số lượng rất ít và mang những giá trị đặc trưng khác biệt đáng kể, do đó chúng có xu hướng dễ bị cô lập (isolate) hơn rất nhiều so với các điểm dữ liệu bình thường.

Quá trình vận hành của Isolation Forest dựa trên việc xây dựng một tập hợp các cây quyết định ngẫu nhiên, được gọi là Isolation Trees. Tại mỗi nút trên cây, thuật toán tiến hành chọn ngẫu nhiên một đặc trưng $x_j$ và đồng thời chọn một giá trị cắt ngẫu nhiên $p$ nằm trong khoảng dao động $[min(x_j), max(x_j)]$. 
Các điểm dữ liệu bình thường, do nằm tập trung trong vùng có mật độ cao, sẽ đòi hỏi hệ thống phải trải qua rất nhiều lần chia (dẫn đến chiều sâu cây lớn) thì mới bị cô lập hoàn toàn. Ngược lại, những điểm dữ liệu bất thường phân bố ở các vùng thưa thớt sẽ nhanh chóng bị cô lập chỉ sau một vài lần chia (chiều sâu cây rất nhỏ).

#### Công thức tính Anomaly Score
Điểm bất thường Anomaly score $s(x,n)$ đối với mẫu dữ liệu $x$ trong một tập hợp gồm $n$ mẫu được toán học hóa theo công thức sau:
$$s(x,n) = 2^{-rac{E(h(x))}{c(n)}}$$

Trong đó:
* $h(x)$ đại diện cho chiều dài đường đi (path length) đo từ vị trí gốc đến nút lá của mẫu $x$ trên một cây riêng lẻ.
* $E(h(x))$ là giá trị chiều dài đường đi trung bình của mẫu $x$ được tính trên toàn bộ tập hợp cây trong rừng.
* $c(n)$ biểu diễn chiều dài đường đi trung bình mang tính lý thuyết của một cây tìm kiếm nhị phân không thành công được tạo từ $n$ mẫu, tính bằng công thức:
$$c(n) = 2 \ln(n-1) + 0.5772156649 - rac{2(n-1)}{n}$$

Các trường hợp đánh giá:
* Nếu $E(h(x)) 	o 0 \implies s 	o 1$ : Điều này chỉ ra mẫu $x$ có chiều dài đường đi rất ngắn. Nên rất có khả năng đây là một điểm dữ liệu bất thường.
* Nếu $E(h(x)) 	o c(n) \implies s 	o 0.5$ : Nghĩa là mẫu $x$ chia sẻ các đặc điểm phổ biến của dữ liệu bình thường.

Trong quá trình triển khai mã thực tế bằng thư viện scikit-learn, điểm số này được biến đổi toán học thành một biến `Score = -score_samples(X)`, đảm bảo nguyên tắc giá trị điểm càng cao thì mức độ bất thường của dữ liệu càng lớn.

### 2.6 Feature Engineering
Feature Engineering (hay Kỹ thuật trích xuất đặc trưng) là một quá trình phân tích tinh vi nhằm chuyển đổi dữ liệu thô (các HTTP request log) thành những biến số định lượng, từ đó biểu diễn toàn diện các khía cạnh hành vi của người dùng. Trong phạm vi của đồ án này, tập hợp 25 đặc trưng số được thiết kế bài bản nhằm phản ánh 3 trụ cột hành vi quan trọng:
* Cường độ và tốc độ phát ra các yêu cầu từ phía client (Frequency / Burst).
* Mức độ tác động qua lại đối với hệ thống tài nguyên (Resource Variety / Sensitive Actions).
* Tần suất phản hồi lỗi và các tín hiệu phân quyền từ phía máy chủ (Error / Authorization Signals).

### 2.7 Chống rò rỉ dữ liệu (Data Leakage)
Data Leakage (Rò rỉ dữ liệu) là một hiện tượng nguy hiểm trong Machine Learning, xảy ra khi các thông tin thuộc tập kiểm thử (Test Set) bị vô tình đưa vào quá trình huấn luyện mô hình, dẫn đến việc mô hình cho ra kết quả đánh giá cao một cách ảo tưởng nhưng lại thất bại trong thực tế. Đối với tập dữ liệu log được nhóm theo phiên làm việc, nếu sử dụng phương pháp chia dữ liệu ngẫu nhiên (Random Split) ở cấp độ cửa sổ thời gian, một rủi ro lớn là các cửa sổ thuộc về cùng một đợt thử nghiệm hay cùng một phiên làm việc có thể xuất hiện đồng thời ở cả hai tập Train và Test.

Để khắc phục triệt để lỗ hổng này, đồ án đã triển khai kỹ thuật Group-aware Split: Tất cả các cửa sổ có cùng một mã `run_id` (mã đợt giả lập) sẽ bị bắt buộc phải nằm trọn vẹn trong cùng một phân tập dữ liệu duy nhất (hoặc là Train, hoặc Validation, hoặc Test).

### 2.8 Các chỉ số đánh giá
Hiệu năng mô hình được đo lường bằng ma trận nhầm lẫn (Confusion Matrix):

**Table 1: Ma trận nhầm lẫn**

| | Dự đoán: Normal (0) | Dự đoán: Anomaly (1) |
|---|---|---|
| **Thực tế: Normal (0)** | True Negative (TN) | False Positive (FP) |
| **Thực tế: Anomaly (1)** | False Negative (FN) | True Positive (TP) |

Từ ma trận với các tham số này, các chỉ số đánh giá chuyên sâu được tính toán như sau:

* **Accuracy (Độ chính xác toàn cục):** Là tỷ lệ giữa số lượng dự đoán đúng trên tổng số dự đoán. 
  $$Accuracy = rac{TP + TN}{TP + TN + FP + FN}$$
* **Precision (Độ chính xác của cảnh báo):** Là tỷ lệ giữa số lượng mẫu dương được dự đoán đúng trên tổng số mẫu được dự đoán là dương. 
  $$Precision = rac{TP}{TP + FP}$$
* **Recall (Độ nhạy / Tỷ lệ phát hiện):** Là tỷ lệ giữa số lượng mẫu dương được dự đoán đúng trên tổng số mẫu dương thực tế. 
  $$Recall = rac{TP}{TP + FN}$$
* **F1-Score:** Là chỉ số kết hợp giữa Precision và Recall, đặc biệt hữu ích khi có sự mất cân đối giữa các lớp. 
  $$F1	ext{-}Score = rac{2 	imes Precision 	imes Recall}{Precision + Recall}$$
* **False Positive Rate (Tỷ lệ báo động giả - FPR):** là tỷ lệ của tất cả các trường hợp âm tính thực tế được dự đoán thành dương tính. 
  $$FPR = rac{FP}{FP + TN}$$

---

## CHƯƠNG 3: THU THẬP DỮ LIỆU VÀ XÂY DỰNG ĐẶC TRƯNG

### 3.1 Môi trường thực nghiệm và Chiến lược thu thập dữ liệu
Môi trường tiến hành thực nghiệm bao gồm một ứng dụng StudyDrive được xây dựng và chạy trên nền tảng Flask phiên bản 3.x, kết nối linh hoạt với cơ sở dữ liệu SQLite/MySQL. Tất cả các HTTP Request được gửi đến ứng dụng đều phải di chuyển qua một lớp Flask Middleware đặc biệt tại `app/middleware/request_logging.py`. Mỗi khi một request hoàn tất chu trình xử lý, hệ thống sử dụng hook `@app.after_request` để trích xuất ngay lập tức các thông tin ngữ cảnh và tự động chèn một bản ghi mới hoàn chỉnh vào bảng `request_logs`.

### 3.2 Cấu trúc dữ liệu log thô (Raw Features)
Mỗi một bản ghi được lưu trong bảng `request_logs` chứa đựng 18 trường thông tin cốt lõi, qua đó mô tả toàn vẹn vòng đời của một HTTP request:
* `request_id`: Chuỗi UUID4 đóng vai trò nhận dạng duy nhất cho từng request.
* `timestamp`: Ghi nhận thời điểm phát sinh request theo chuẩn UTC.
* `user_id`: Mã định danh người dùng (-1 trong trường hợp truy cập chưa đăng nhập).
* `is_authenticated`: Cho biết trạng thái xác thực bằng True/False.
* `role`: Xác định vai trò của người dùng trên hệ thống (USER / ADMIN / ANONYMOUS).
* `session_id_hash`: Chứa chuỗi băm bảo mật SHA-256 của Session Token.
* `http_method`: Xác định phương thức HTTP được sử dụng (GET, POST, DELETE...).
* `endpoint`: Tên của endpoint Flask chịu trách nhiệm xử lý request.
* `path`: Chi tiết đường dẫn URL mà client truy cập.
* `action`: Định nghĩa tên hành động nghiệp vụ (chẳng hạn như `view_file`, `export`...).
* `action_type`: Phân loại hành động (read, export, delete, auth...).
* `is_sensitive`: Cờ (True/False) nhằm đánh dấu xem thao tác đó có tính chất nhạy cảm hay không.
* `resource_type`: Phân loại tài nguyên bị tác động (file, folder, system).
* `resource_id`: Mã ID của đối tượng tài nguyên đang bị request tác động.
* `ownership_result`: Lưu trữ kết quả kiểm tra quyền sở hữu (OWNER, VIEWER, NONE).
* `authorization_result`: Lưu kết quả của quá trình phân quyền (ALLOWED, DENIED).
* `status_code`: Mã trạng thái phản hồi HTTP do máy chủ trả về (200, 403, 404, 500...).
* `response_time_ms`: Quãng thời gian xử lý thực tế của máy chủ, được đo lường bằng milliseconds.

### 3.3 Giả lập kịch bản hành vi (Simulation)
Để có thể tạo ra một tập dữ liệu tiêu chuẩn phục vụ cho công tác huấn luyện và đánh giá, đồ án đã tiến hành xây dựng các script giả lập thao tác tự động bằng thư viện `requests` của Python, đặt trong thư mục `scripts/`:
* **Hành vi người dùng hợp lệ (`simulate_normal.py`):** Script này mô phỏng lại một chuỗi tương tác tự nhiên thường thấy của người dùng bình thường: Bắt đầu bằng Đăng nhập → Duyệt qua danh sách thư mục → Xem chi tiết 2–3 tệp tin → Tải xuống 1 tệp → Kết thúc bằng Đăng xuất. Các request phát sinh trong kịch bản này đều đặn với những khoảng cách thời gian ngẫu nhiên kéo dài từ 3 đến 15 giây.
* **Kịch bản Export Abuse (`simulate_export_abuse.py`):** Tập trung mô phỏng hành vi lạm dụng chức năng xuất dữ liệu (một dạng Business Logic Abuse). Script liên tục gửi đi từ 30 đến 50 request yêu cầu xuất báo cáo định dạng CSV/ZIP trong cùng một vòng 5 phút, khoảng thời gian ngắt quãng giữa các request là cực kỳ ngắn (dưới 1 giây).
* **Kịch bản Delete Abuse (`simulate_delete_abuse.py`):** Nhắm tới việc mô phỏng hành vi phá hoại tài nguyên thông qua các lệnh xóa mềm (soft delete). Script thực hiện liên tục khoảng 30 lệnh xóa trên các tệp tin hoàn toàn khác nhau trong giới hạn một cửa sổ 5 phút.
* **Kịch bản IDOR/BOLA Scan (`simulate_bola_scan.py`):** Mô phỏng hành vi rà quét để thăm dò quyền truy cập đối tượng của hệ thống. Kẻ tấn công tự động thay đổi tham số `file_id` theo thứ tự tăng dần từ 100 đến 500, cố gắng truy cập các tệp tin trái quyền sở hữu, tạo ra liên tiếp các phản hồi lỗi 403 (Forbidden) và 404 (Not Found).

Nhờ quá trình giả lập này, đồ án đã thu thập được thành công 10.867 bản ghi log thô, từ đó gom lại thành 17 cửa sổ thời gian 5 phút phục vụ phân tích.

### 3.4 Tiền xử lý dữ liệu và Chống rò rỉ dữ liệu (Data Leakage)
Quy trình tiền xử lý dữ liệu chuyên sâu được thực thi qua các bước trong tệp `ml/build_features.py`:
* **Lọc dữ liệu rác:** Hệ thống loại bỏ các request hướng tới tài nguyên tĩnh (`/static/...`) cũng như các request dùng để kiểm tra trạng thái máy chủ (`/health`).
* **Chuẩn hóa dtypes:** Các biến được ép kiểu chính xác (đưa timestamp về hệ UTC, ép biến boolean và chuẩn hóa chuỗi `resource_id`).
* **Gán nhãn Ground Truth:** Tiến hành kết hợp dữ liệu log thô với tệp `ground_truth.csv` dựa trên sự đối chiếu khoảng thời gian (`started_at`, `ended_at`) và `user_id` để tiến hành gán nhãn `label = 1` đối với cửa sổ Anomaly hoặc `label = 0` đối với cửa sổ Normal.
* **Chia tập dữ liệu chống rò rỉ:** Sử dụng hàm chuyên biệt `split_features()` nhằm nhóm các cửa sổ theo mã `run_id`, đảm bảo rằng Tập Train chỉ giữ lại các đợt chạy được xác định là Normal.

### 3.5 Trích xuất đặc trưng (Feature Engineering)
Dựa trên nền tảng các bản ghi log trong từng cửa sổ 5 phút tương ứng với (`user_id`, `session_id_hash`), pipeline của hệ thống thực hiện tính toán ra 25 đặc trưng số, được phân tách vào 3 nhóm chuyên biệt:

**Đặc trưng dựa trên tần suất (Frequency Features): Phản ánh cường độ hoạt động**
* `request_count`: Đo tổng số request hiện diện trong cửa sổ.
* `session_duration_sec`: Đo độ dài thời gian phiên làm việc (tính bằng giây) = $max(ts) - min(ts)$.
* `avg_inter_request_sec`: Tính toán khoảng cách thời gian trung bình giữa 2 request nối tiếp.
* `min_inter_request_sec`: Tìm ra khoảng cách thời gian nhỏ nhất giữa 2 request.
* `burst_rate`: Đánh giá tỷ lệ các request sở hữu khoảng cách liên tiếp ≤ 1.0 giây.
* `export_count` và `export_ratio`: Đếm số lượng và tính tỷ lệ request yêu cầu export.
* `delete_count` và `delete_ratio`: Đếm số lượng và tính tỷ lệ request yêu cầu thao tác xóa.
* `sensitive_request_count` và `sensitive_ratio`: Thống kê các thao tác mang tính nhạy cảm.
* `max_sensitive_streak`: Tìm kiếm độ dài của chuỗi các request nhạy cảm xảy ra liên tiếp dài nhất.

**Đặc trưng dựa trên tính đa dạng tài nguyên (Resource Variety Features): Khảo sát phạm vi tác động**
* `unique_endpoint_count`: Đếm số lượng endpoint Flask khác biệt đã được client truy cập.
* `unique_method_count`: Thống kê các phương thức HTTP khác nhau (GET, POST...).
* `unique_deleted_resource_count`: Thống kê số lượng `resource_id` duy nhất đã bị người dùng xóa.
* `unique_resource_id_count` và `resource_id_request_ratio`: Phân tích sự đa dạng thông qua số lượng `resource_id` duy nhất được yêu cầu trên tổng số request.
* `resource_id_change_rate`: Đo lường tỷ lệ thay đổi đối tượng `resource_id` giữa các request gửi liên tiếp.

**Đặc trưng dựa trên tỷ lệ lỗi và phân quyền (Error/Auth Features): Cảnh báo dấu hiệu xâm phạm hệ thống**
* `error_rate`: Tính tỷ lệ các request trả về status code ≥ 400.
* `avg_response_time_ms`: Xác định thời gian máy chủ mất để phản hồi trung bình.
* `forbidden_count` và `forbidden_rate`: Số lượng và tỷ lệ request gặp lỗi từ chối quyền truy cập (mã 403).
* `not_found_count` và `not_found_rate`: Số lượng và tỷ lệ request thất bại vì không tìm thấy tài nguyên (mã 404).
* `unique_failed_resource_id_count`: Thống kê lượng `resource_id` duy nhất gây ra lỗi 403 hoặc 404.

---

## CHƯƠNG 4: HUẤN LUYỆN MÔ HÌNH VÀ ĐÁNH GIÁ KẾT QUẢ

### 4.1 Thiết kế thực nghiệm và Phân chia tập dữ liệu (Train/Validation/Test)
Toàn bộ tập dữ liệu gồm 17 cửa sổ 5 phút (được trích xuất từ 10.867 bản ghi log) đã được phân chia theo Group Key định dạng (`run_id`, `session_id_hash`) thành các tập:
* **Tập Train (Huấn luyện):** Bao gồm 6 cửa sổ mang đặc tính hoàn toàn bình thường (label = 0), dùng để cho mô hình có thể học được thế nào là phân bố chuẩn của hệ thống.
* **Tập Validation (Thẩm định):** Bao gồm 6 cửa sổ (trộn lẫn cả Normal và Anomaly), được sử dụng riêng biệt cho quá trình tinh chỉnh siêu tham số và xác định ngưỡng đánh giá (threshold).
* **Tập Test (Kiểm thử):** Bao gồm 5 cửa sổ độc lập hoàn toàn, được ứng dụng ở bước cuối cùng nhằm đánh giá hiệu năng thực tế.

### 4.2 Quá trình huấn luyện và Tinh chỉnh siêu tham số (Hyperparameter Tuning)
Quá trình khởi tạo baseline model trong file `ml/train.py` được thiết lập với cấu hình ban đầu: `n_estimators = 200`, `max_samples = 'auto'` (min(256, n)), `contamination = 'auto'`, và `random_state = 20260706`.

Sau đó, hệ thống tiến hành Grid Tuning trên tập Validation, tìm kiếm qua 24 tổ hợp siêu tham số kết hợp giữa `n_estimators` (100, 200, 300), `max_samples` ('auto', 256) và `threshold_percentile` (90.0%, 92.5%, 95.0%, 97.5%). Cấu hình tối ưu nhất được lựa chọn dựa trên mức độ ưu tiên: F1-Score -> FPR -> Recall.

Kết quả mang lại cấu hình tối ưu bao gồm: `n_estimators = 200`, `max_samples = 'auto'`, `threshold_percentile = 95.0%` với Ngưỡng Anomaly Score thu được đạt mức xấp xỉ 0.4866.

### 4.3 Kết quả đánh giá
Để đánh giá tính hiệu quả, mô hình được chạy thử nghiệm trên một tập dữ liệu Test độc lập (không nằm trong tập huấn luyện). Các chỉ số hiệu năng (Evaluation Metrics) thu được như sau:

**Table 2: Kết quả đánh giá mô hình**

| Chỉ số (Metric) | Giá trị Thực tế | Diễn giải thực tiễn |
|---|---|---|
| Accuracy (Độ chính xác) | 83.33% (0.8333) | Tỷ lệ dự đoán đúng đắn trên tổng thể tất cả các cửa sổ thời gian. |
| Precision (Độ xác thực) | 75.00% (0.7500) | Trong số các cảnh báo hệ thống phát ra, có 75% cảnh báo là tấn công thực sự. |
| Recall (Độ nhạy) | 100.00% (1.0000) | Trong tổng số tất cả các đợt tấn công thực tế, mô hình nhận diện được tuyệt đối 100%. |
| F1-Score | 85.71% (0.8571) | Giá trị trung bình hài hòa, phản ánh độ tin cậy và cân bằng rất tốt của mô hình. |
| FPR (False Positive Rate) | 33.33% (0.3333) | Tỷ lệ báo động giả: 33.33% người dùng bình thường bị nhận diện nhầm thành kẻ tấn công. |

Phân tích qua Ma trận nhầm lẫn (Confusion Matrix):

**Table 3: Confusion Matrix**

| | Dự đoán: Normal (0) | Dự đoán: Anomaly (1) |
|---|---|---|
| **Thực tế: Normal (0)** | TN = 2 | FP = 1 |
| **Thực tế: Anomaly (1)** | FN = 0 | TP = 3 |

Cho thấy: Có 2 mẫu Normal được dự đoán đúng (TN), 1 mẫu Normal dự đoán nhầm thành Anomaly (FP), 0 mẫu Anomaly bị bỏ sót (FN), và toàn bộ 3 mẫu Anomaly được phát hiện chính xác (TP).

### 4.4 Phân tích trực quan
Khi đi sâu phân tích hiệu suất theo từng kịch bản hành vi, hệ thống ghi nhận:
* **Khả năng phát hiện (Thành công tuyệt đối):** Đạt thành công tuyệt đối khi mô hình phát hiện chính xác 100% các cửa sổ tấn công (TP=3, FN=0). Nhóm đặc trưng `export_count`, `burst_rate` và `forbidden_rate` đã thể hiện sự vượt trội rõ rệt so với phân bố bình thường, giúp kích hoạt cảnh báo kịp thời.
* **Hành vi người dùng hợp lệ cường độ cao:** Tạo ra False Positive khi 1 cửa sổ Normal bị cảnh báo nhầm (FP=1). Hiện tượng này xảy ra do người dùng thực hiện thao tác duyệt tệp và xuất báo cáo với cường độ liên tục, tạo ra một độ vọt `burst_rate` tiệm cận với mẫu của các kịch bản tấn công.

### 4.5 Những hạn chế trong quá trình thực nghiệm mô hình
* Kích thước tập dữ liệu khá khiêm tốn (chỉ với 17 cửa sổ tổng thể và 5 cửa sổ trên tập Test), do đó chỉ số F1 85.71% mới chỉ mang tính chất phản ánh sơ bộ mức độ khả thi của thuật toán trên tập dữ liệu hiện tại.
* Tỷ lệ báo động giả (FPR = 33.33%) cho thấy mô hình vẫn còn xu hướng nhạy cảm với những người dùng thao tác quá nhanh.
* Việc cố định kích thước cửa sổ 5 phút có thể tạo kẽ hở cho các đợt tấn công cố tình có mật độ request thưa thớt, khiến chúng có khả năng không bị phát hiện.

---

## CHƯƠNG 5: TRIỂN KHAI HỆ THỐNG VÀ KIẾN TRÚC TÍCH HỢP

### 5.1 Luồng xử lý hệ thống (Pipeline)
Toàn bộ hệ thống StudyDrive đã được tích hợp thành công theo một quy trình dữ liệu khép kín (pipeline). Các HTTP Requests đi qua lớp Flask Middleware (`request_logging.py`), sử dụng hook `after_request` để truyền dữ liệu vào cơ sở dữ liệu `request_logs`. Từ phía Admin Dashboard, quản trị viên có thể kích hoạt file `detection_service.py` để hệ thống tiến hành: 
1. Gom nhóm các cửa sổ 5 phút; 
2. Trích xuất đủ 25 đặc trưng; 
3. Tải mô hình Isolation Forest (`model.joblib`); 
4. Tính toán Anomaly Score. 
Các cảnh báo nếu vượt ngưỡng sẽ được lưu xuống CSDL và báo cáo lên giao diện Alerts Dashboard, hỗ trợ quy trình truy vết log.

### 5.2 Cơ chế phát hiện tự động
Toàn bộ dịch vụ phát hiện được đóng gói chuyên nghiệp tại thư mục `app/services/detection_service.py`. Khối mã thực thi sẽ nạp dữ liệu log chưa được xử lý, làm sạch chúng, tổng hợp đặc trưng, sau đó load file mô hình huấn luyện `model.joblib` để tính điểm bất thường thông qua lệnh `-model.score_samples(X)`. Quản trị viên có hai cách để kích hoạt tiến trình này: nhấn nút "Run Detection" trực tiếp trên giao diện Admin, hoặc chạy tự động thông qua dòng lệnh CLI `python -m scripts.run_detection`.

### 5.3 Giao diện quản trị
#### Alerts Dashboard
Trang quản trị Cảnh báo (truy cập qua `/admin/alerts`) đem đến một giao diện trực quan. Tại đây, Admin có thể theo dõi danh sách cảnh báo minh bạch bao gồm thời gian phát hiện, User ID, Session ID hash, điểm Anomaly Score và cả gợi ý kịch bản (`scenario_hint`). Trạng thái của từng cảnh báo được phân loại rõ ràng thành: Pending (Mới), Investigating (Đang rà soát), Resolved (Đã xử lý), và Ignored (Bỏ qua).

#### Cơ chế truy vết Log gốc (Forensics)
Điểm mạnh của hệ thống là khi quản trị viên nhấn vào chi tiết của một Alert, hệ thống sẽ tự động trích xuất các thông tin định vị (`user_id`, `session_id_hash`, `window_start`, `window_end`) và điều hướng trực tiếp sang trang Admin Logs Filtered. Tại đó, quản trị viên có thể giám sát chính xác từng thao tác HTTP Request trong cửa sổ 5 phút bị đánh dấu, từ URL, status code cho đến tham số nhằm đưa ra các quyết định chính xác.

Hệ thống được chứng minh độ tin cậy khi đã vượt qua 34 test cases tự động (sử dụng Pytest và Pytest-Flask) với tỷ lệ qua bài (pass rate) đạt mức tuyệt đối 100% trong thời gian 17.87s.

---

## CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 6.1 Kết quả đạt được
Đồ án tự hào khẳng định đã ứng dụng thành công kỹ thuật Machine Learning trong bài toán nhận diện và phát hiện các hành vi truy cập bất thường trên môi trường web StudyDrive:
* Triển khai phần mềm vững chắc với cơ chế Structured Logging tự động và áp dụng quy chuẩn băm SHA-256 an toàn.
* Xây dựng trọn vẹn một Pipeline Machine Learning khép kín từ khâu thu thập log thô cho đến việc đưa qua mô hình Isolation Forest với chiến lược Normal-only Training và Group-aware Split.
* Tích hợp hệ thống quản trị chuyên sâu với giao diện Alerts Dashboard hỗ trợ truy vết xuất sắc về bản ghi log gốc.
* Đánh giá thực nghiệm khách quan bằng tập Test chuyên dụng đạt mức F1-Score 66.67% cùng bộ kiểm thử 34 test cases ổn định.

### 6.2 Hạn chế
Bên cạnh kết quả, hệ thống vẫn mang một số giới hạn thực tiễn, cụ thể như quy mô của tập dữ liệu thực nghiệm (24 cửa sổ 5 phút) vẫn còn khá nhỏ, đòi hỏi phải được mở rộng trong một môi trường thực tế. Hơn nữa, việc chỉ áp dụng phương thức xử lý Batch khiến hệ thống chưa thể đạt được độ trễ thời gian thực (Real-time Streaming). Cuối cùng, phản ứng của hệ thống vẫn mang tính chất thụ động khi chỉ phát ra cảnh báo thay vì tự động khóa tài khoản hay chặn IP kẻ xấu.

### 6.3 Hướng phát triển
Trong tương lai, đồ án định hướng nâng cấp kiến trúc phát hiện bằng việc tích hợp các Message Broker (Apache Kafka, RabbitMQ) cùng Celery Workers nhằm đẩy mạnh tiến trình xử lý thời gian thực. Bên cạnh đó, hệ thống sẽ thử nghiệm kết hợp thuật toán Isolation Forest với các mô hình tiên tiến như Autoencoder hay One-Class SVM để đa dạng hóa việc phòng thủ trước các kịch bản rắc rối như Credential Stuffing hay Brute-force Login. Mục tiêu cuối cùng là hoàn thiện cơ chế phản ứng tự động (Active Response) nhằm chủ động yêu cầu xác thực OTP hoặc chặn IP ngay khi điểm số bất thường (Anomaly Score) vượt mức nguy hiểm.

---

## TÀI LIỆU THAM KHẢO
[1] F. T. Liu, K. M. Ting, và Z. H. Zhou, "Isolation Forest," trong 2008 Eighth IEEE International Conference on Data Mining, 2008, tr. 413-422, doi: 10.1109/ICDM.2008.17.
[2] OWASP Foundation, "OWASP Top 10:2021 - A01:2021-Broken Access Control & A04:2021-Insecure Design," OWASP Top 10 Web Application Security Risks, 2021. [Trực tuyến]. Địa chỉ: https://owasp.org/Top10/. [Truy cập: 09/08/2026].
[3] V. Chandola, A. Banerjee, và V. Kumar, "Anomaly detection: A survey," ACM Computing Surveys (CSUR), vol. 41, no. 3, tr. 1-58, 2009, doi: 10.1145/1541880.1541882.
[4] Scikit-Learn Developers, "sklearn.ensemble.IsolationForest Documentation," Scikit-Learn API Reference, 2023. [Trực tuyến]. Địa chỉ: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html. [Truy cập: 09/08/2026].
[5] F. Pedregosa et al., "Scikit-learn: Machine learning in Python," Journal of Machine Learning Research, vol. 12, tr. 2825-2830, 2011.
[6] D. Stuttard và M. Pinto, The Web Application Hacker's Handbook: Finding and Exploiting Security Flaws, ấn bản 2. John Wiley & Sons, 2011.
[7] A. L. Buczak và E. Guven, "A survey of data mining and machine learning methods for cyber intrusion detection," IEEE Communications Surveys & Tutorials, vol. 18, no. 2, tr. 1153-1176, 2015, doi: 10.1109/COMST.2015.2494502.
