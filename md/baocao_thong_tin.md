# BÁO CÁO CHI TIẾT ĐỒ ÁN MÔN HỌC / TỐT NGHIỆP
## ĐỀ TÀI: XÂY DỰNG HỆ THỐNG PHÁT HIỆN HÀNH VI TRUY CẬP BẤT THƯỜNG TRÊN ỨNG DỤNG WEB BẰNG MACHINE LEARNING

> **Ghi chú cho người dùng:** Tài liệu này chứa đầy đủ toàn bộ nội dung chi tiết từ phát biểu bài toán theo khung T-P-E (Task, Performance, Experience), cơ sở lý thuyết, so sánh thuật toán (iForest vs OCSVM vs LOF vs Autoencoder), kiến trúc hệ thống, thiết kế CSDL, bảo mật log, quy tắc phân chia tập dữ liệu (Train/Val/Test), công thức toán 11 đặc trưng, phương pháp tuning siêu tham số, 3 case study thực nghiệm chi tiết đến tài liệu tham khảo chuẩn IEEE. Bạn có thể copy trực tiếp các chương vào file Word báo cáo đồ án.

---

## BẢNG THÔNG TIN ĐỀ TÀI & TÁC GIẢ

* **Tên đề tài:** Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning

---

## CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI

### 1.1. Bối cảnh & Lý do chọn đề tài
Trong kỷ nguyên số hóa, các ứng dụng web lưu trữ và chia sẻ dữ liệu (như Google Drive, Dropbox, OneDrive) đã trở thành hạ tầng thiết yếu cho cá nhân và tổ chức. Tuy nhiên, sự gia tăng của các cuộc tấn công nhắm vào tầng ứng dụng (Application Layer Attacks) đặt ra thách thức bảo mật rất lớn.

Các giải pháp bảo mật truyền thống như Web Application Firewall (WAF) hay Intrusion Detection System (IDS) tầng mạng thường tập trung vào việc chặn các cuộc tấn công có chữ ký rõ ràng (Signature-based) như SQL Injection, Cross-Site Scripting (XSS), hoặc SYN Flood. Tuy nhiên, WAF/IDS truyền thống gần như **bất lực** trước các hành vi **Lạm dụng Logic Nghiệp vụ (Business Logic Abuse)** và **Tấn công Phân quyền Đối tượng (Broken Object Level Authorization - BOLA / IDOR)**. Kẻ tấn công trong các kịch bản này sử dụng tài khoản hợp lệ hoặc gửi các HTTP Request hợp lệ về mặt cú pháp nhưng thực hiện các hành vi bất thường nhằm vét dữ liệu, phá hoại hệ thống hoặc dò quét tài nguyên trái phép.

Do đó, việc ứng dụng **Machine Learning (Học máy)** — cụ thể là các mô hình phát hiện bất thường không giám sát (Unsupervised Anomaly Detection) — để phân tích chuỗi log truy cập tầng ứng dụng theo thời gian là một giải pháp cấp thiết và có tính thực tiễn cao.

### 1.2. Mục tiêu nghiên cứu
1. **Xây dựng ứng dụng Web StudyDrive hoàn chỉnh**: Cung cấp các chức năng quản lý, lưu trữ, chia sẻ và xuất tệp tin với cơ chế phân quyền chặt chẽ (OWNER/VIEWER).
2. **Phát triển hệ thống Log tầng ứng dụng (Structured Request Logging)**: Tự động ghi vết chi tiết từng HTTP Request của người dùng mà không làm gián đoạn luồng xử lý chính.
3. **Xây dựng bộ tạo dữ liệu giả lập (Attack & Normal Simulators)**: Sinh dữ liệu log phản ánh các kịch bản hoạt động bình thường và 3 kịch bản tấn công nghiệp vụ thực tế.
4. **Thiết kế Pipeline Trích xuất Đặc trưng & Phân chia Tập dữ liệu**: Chuyển đổi dữ liệu log thô thành các vector đặc trưng theo cửa sổ 5 phút, thực hiện phân chia tập dữ liệu Train/Val/Test chống rò rỉ (Group-aware Anti Data Leakage).
5. **Huấn luyện, Tối ưu Siêu tham số & Tích hợp mô hình Isolation Forest**: Huấn luyện mô hình, tinh chỉnh tham số bằng Grid Search, tích hợp vào Admin Dashboard để phát cảnh báo tự động.
6. **Đánh giá & Kiểm thử toàn diện**: Xây dựng bộ 38 bài test tự động và đánh giá hiệu năng mô hình qua các chỉ số Accuracy, Precision, Recall, F1-Score, Confusion Matrix.

### 1.3. Đối tượng & Phạm vi nghiên cứu
* **Đối tượng nghiên cứu**: Log truy cập tầng ứng dụng Web (HTTP Request Logs), đặc trưng chuỗi hành vi người dùng, thuật toán Isolation Forest.
* **Phạm vi nghiên cứu**: 
  * Tập trung vào 3 kịch bản bất thường nghiệp vụ chính: **Export Abuse**, **Delete Abuse**, và **BOLA/IDOR Scan**.
  * Triển khai thử nghiệm trên ứng dụng Flask StudyDrive với cơ sở dữ liệu SQLite/MySQL.

### 1.4. Chi tiết 3 Kịch bản Tấn công / Bất thường Nghiệp vụ
1. **Export Abuse (Lạm dụng tính năng xuất dữ liệu hàng loạt)**:
   * *Mô tả*: Người dùng thực hiện liên tục các yêu cầu đóng gói ZIP hoặc xuất dữ liệu CSV với số lượng lớn tệp tin trong một khoảng thời gian ngắn.
   * *Hậu quả*: Nguy cơ thất thoát dữ liệu quy mô lớn (Data Exfiltration) hoặc gây cạn kiệt tài nguyên CPU/RAM/Disk của máy chủ.
2. **Delete Abuse (Lạm dụng tính năng xóa tệp tin)**:
   * *Mô tả*: Người dùng thực hiện xóa mềm (soft-delete) dồn dập hàng loạt tệp tin thuộc nhiều thư mục khác nhau.
   * *Hậu quả*: Tài khoản bị chiếm đoạt (Account Takeover) hoặc kẻ tấn công cố tình phá hoại toàn bộ dữ liệu của nạn nhân.
3. **IDOR / BOLA Scan (Rà quét lỗ hổng BOLA - Broken Object Level Authorization)**:
   * *Mô tả*: Kẻ tấn công thay đổi liên tục tham số `resource_id` trên URI/API (ví dụ `/documents/file/101`, `/documents/file/102`,...) nhằm tự động dò quét và truy cập file thuộc sở hữu của người dùng khác.
   * *Dấu hiệu*: Tăng đột biến tỷ lệ lỗi `403 Forbidden` (truy cập trái quyền) và `404 Not Found` (đoán sai ID file không tồn tại) từ cùng một IP/User/Session.

### 1.5. Phát biểu Bài toán Machine Learning theo Khung T-P-E (Task - Performance - Experience)

Theo định nghĩa kinh điển của Tom Mitchell (1997): *"Một chương trình máy tính được gọi là học từ kinh nghiệm E đối với một lớp các tác vụ T và độ đo hiệu năng P, nếu hiệu năng của nó tại các tác vụ trong T, được đo bởi P, cải thiện theo kinh nghiệm E"*.

Bài toán **Phát hiện Hành vi Truy cập Bất thường trên Web StudyDrive** được hình thức hóa chuẩn xác theo bộ ba khung **T-P-E** như sau:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         KHUNG BÀI TOÁN MACHINE LEARNING (T-P-E)                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 🎯 TASK (T) - TÁC VỤ:                                                             │
│    Phân loại / Phát hiện điểm bất thường trên cửa sổ thời gian 5 phút.           │
│    Đầu vào: Vector đặc trưng 11 chiều x ∈ R¹¹ đại diện cho chuỗi HTTP requests.   │
│    Đầu ra: Nhãn y ∈ {0: Bình thường (Normal), 1: Bất thường (Anomaly)}.          │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 📊 PERFORMANCE (P) - ĐỘ ĐO HIỆU NĂNG:                                            │
│    Đánh giá định lượng hiệu năng phân loại trên tập Test:                         │
│    - Precision: Tỷ lệ cảnh báo phát ra là tấn công/bất thường thật.             │
│    - Recall: Độ gợi nhớ / Tỷ lệ kịch bản tấn công thật được phát hiện.           │
│    - F1-Score: Trung bình hài hòa giữa Precision và Recall.                      │
│    - False Positive Rate (FPR): Tỷ lệ báo động giả trên người dùng bình thường.  │
│    - Anomaly Score & Ngưỡng Percentile 95%: Độ lệch phân bố hành vi.              │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 📚 EXPERIENCE (E) - KINH NGHIỆM / DỮ LIỆU HUẤN LUYỆN:                           │
│    Tập dữ liệu Structured Request Logs (5.567 dòng log thô) được thu thập từ     │
│    ứng dụng StudyDrive. Tập Train chỉ bao gồm các cửa sổ hành vi bình thường     │
│    (Normal-only) để mô hình Isolation Forest học phân bố chuẩn không giám sát.    │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT & NỀN TẢNG CÔNG NGHỆ

### 2.1. Tổng quan về Phát hiện Bất thường (Anomaly Detection)
Phát hiện bất thường là kỹ thuật nhận diện các mẫu dữ liệu (patterns) không tuân theo hành vi chuẩn đã được định nghĩa trước. Trong an toàn thông tin, các điểm bất thường này thường tương ứng với các cuộc tấn công, hành vi gian lận hoặc sự cố hệ thống.

Khác với học có giám sát (Supervised Learning) yêu cầu dữ liệu phải có nhãn tấn công đầy đủ (vốn rất hiếm và đắt đỏ trong thực tế), phương pháp **Học không giám sát (Unsupervised Learning)** như **Isolation Forest** chỉ cần học phân bố của dữ liệu thông thường để tự động phát hiện các điểm nằm ngoài phân bố (outliers).

### 2.2. Thuật toán Isolation Forest (iForest)

#### a) Nguyên lý hoạt động
Isolation Forest (Liu et al., 2008) dựa trên nguyên lý: **"Các điểm dữ liệu bất thường dễ bị cô lập hơn các điểm dữ liệu bình thường"**.

Mô hình dựng một rừng các cây quyết định cô lập (iTrees). Tại mỗi nút của cây, thuật toán chọn ngẫu nhiên một đặc trưng $x_j$ và chọn ngẫu nhiên một giá trị chia $p$ nằm trong khoảng $[\min(x_j), \max(x_j)]$.
* **Điểm bất thường (Anomaly)**: Thường có số lượng ít và giá trị đặc trưng khác biệt rõ rệt, do đó chúng bị cô lập rất nhanh (độ sâu cây / độ dài đường đi $h(x)$ ngắn).
* **Điểm bình thường (Normal)**: Nằm trong cụm dữ liệu dày đặc, cần nhiều lần phân chia mới cô lập được (độ dài đường đi $h(x)$ dài).

#### b) Các công thức toán học cốt lõi

1. **Độ dài đường đi trung bình của cây tìm kiếm nhị phân thất bại $c(n)$**:
   Với tập $n$ mẫu dữ liệu, độ dài đường đi trung bình $c(n)$ được tính theo công thức:
   $$c(n) = 2 \left( \ln(n - 1) + 0.5772156649 \right) - \frac{2(n - 1)}{n}$$
   *(Trong đó $0.5772156649$ là hằng số Euler-Mascheroni).*

2. **Điểm bất thường (Anomaly Score) $s(x, n)$**:
   Với một mẫu dữ liệu $x$, anomaly score $s(x, n)$ được xác định bởi:
   $$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
   *(Trong đó $E(h(x))$ là giá trị kỳ vọng độ dài đường đi của $x$ qua toàn bộ các iTree trong rừng).*

3. **Quy tắc đánh giá điểm $s(x, n)$**:
   * Nếu $s(x, n) \to 1$: Mẫu $x$ có độ dài đường đi rất ngắn $\rightarrow$ **Rất có khả năng là Bất thường**.
   * Nếu $s(x, n) < 0.5$: Mẫu $x$ có độ dài đường đi bình thường $\rightarrow$ **Mẫu Bình thường**.
   * Nếu $s(x, n) \approx 0.5$: Toàn bộ tập dữ liệu không có điểm bất thường rõ rệt.

### 2.3. So sánh So sánh các Phương pháp Học máy trong Phát hiện Bất thường
Để khẳng định tính hợp lý khi chọn **Isolation Forest**, bảng dưới đây so sánh 4 thuật toán phát hiện bất thường phổ biến nhất hiện nay:

| Tiêu chí So sánh | Isolation Forest (iForest) | One-Class SVM (OCSVM) | Local Outlier Factor (LOF) | Autoencoder (Neural Net) |
| :--- | :--- | :--- | :--- | :--- |
| **Nguyên lý cốt lõi** | Cô lập mẫu bằng đường phân chia ngẫu nhiên | Tìm siêu mặt phẳng tối đa hóa khoảng cách | Đo khoảng cách mật độ cục bộ (k-NN) | Tái tạo dữ liệu (Reconstruction Error) |
| **Độ phức tạp thời gian** | $\mathcal{O}(n \log n)$ (Rất nhanh) | $\mathcal{O}(n^2) \to \mathcal{O}(n^3)$ (Chậm) | $\mathcal{O}(n^2)$ (Trung bình) | $\mathcal{O}(n \cdot d \cdot e)$ (Rất chậm) |
| **Bộ nhớ (Memory)** | Rất thấp ($\mathcal{O}(n)$) | Cao (Lưu các Support Vectors) | Cao (Lưu ma trận khoảng cách $k$-NN) | Cao (Lưu trọng số mạng Nơ-ron) |
| **Dữ liệu nhiều chiều** | Xử lý tốt, không bị hiện tượng "Curse of Dimensionality" | Nhạy cảm với chiều dữ liệu lớn | Giảm độ chính xác khi chiều dữ liệu tăng | Cần tuning kiến trúc mạng phức tạp |
| **Yêu cầu phân bố** | **Không yêu cầu giả định phân bố** | Yêu cầu chọn Kernel (RBF/Linear) | Phụ thuộc vào tham số chọn $k$ | Cần lượng dữ liệu huấn luyện cực lớn |
| **Phù hợp Web Logs** | **TỐI ƯU NHẤT** (Xử lý batch log nhanh, ít tốn tài nguyên server) | Phù hợp dataset nhỏ | Khó mở rộng trên dữ liệu log thực tế | Dễ bị quá khớp (Overfitting) |

### 2.4. Stack Công nghệ Triển khai
* **Ngôn ngữ lập trình**: Python 3.11+
* **Web Framework**: Flask 3.x, Werkzeug, Jinja2, Bootstrap 5
* **ORM & CSDL**: Flask-SQLAlchemy, SQLite (môi trường Dev/Test), MySQL / PyMySQL (Production)
* **Xử lý dữ liệu & ML**: Pandas, NumPy, Scikit-Learn (module `sklearn.ensemble.IsolationForest`), Joblib
* **Kiểm thử & Automation**: Pytest, Pytest-Flask, Requests

---

## CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

### 3.1. Kiến trúc Tổng thể Hệ thống StudyDrive
Hệ thống được thiết kế theo kiến trúc **Blueprint Modular** kết hợp **Batch ML Detection Pipeline**:

```text
[ Người dùng / Attacker ]
        │ (HTTP Requests)
        ▼
┌────────────────────────────────────────────────────────┐
│ Ứng dụng Web StudyDrive (Flask Web Framework)           │
│  ├── Blueprints: Auth, Documents, Admin, Alerts        │
│  └── Middleware: Structured Request Logger             │
└──────────────────────────┬─────────────────────────────┘
                           │ (Ghi Log tự động)
                           ▼
┌────────────────────────────────────────────────────────┐
│ Cơ sở dữ liệu Relational DB (SQLite / MySQL)            │
│  ├── Bảng Nghiệp vụ: Users, Folders, Files, Shares...   │
│  └── Bảng Giám sát: RequestLogs, Alerts                 │
└──────────────────────────┬─────────────────────────────┘
                           │ (Chạy định kỳ / Trigger Admin)
                           ▼
┌────────────────────────────────────────────────────────┐
│ ML Detection Pipeline (Python ML Engine)               │
│  ├── 1. Feature Engineering (Cửa sổ 5 phút / 11 features)│
│  ├── 2. Isolation Forest Scorer (model.joblib)         │
│  └── 3. Alert Generator (Ghi nhãn & Lưu cảnh báo)     │
└──────────────────────────┬─────────────────────────────┘
```

### 3.2. Thiết kế Cơ sở Dữ liệu Chi tiết (Database Schema)

CSĐL gồm 7 bảng chính được chuẩn hóa theo dạng chuẩn 3 (3NF):

#### 1. Bảng `users` (Tài khoản người dùng)
* `id` (INT, Primary Key, Auto Increment): Mã người dùng.
* `username` (VARCHAR(64), Unique, Not Null): Tên đăng nhập.
* `email` (VARCHAR(120), Unique, Not Null): Địa chỉ email.
* `password_hash` (VARCHAR(256), Not Null): Mật khẩu đã băm (Werkzeug pbkdf2:sha256).
* `role` (VARCHAR(20), Default 'USER'): Vai trò (`USER` hoặc `ADMIN`).
* `is_active` (BOOLEAN, Default True): Trạng thái tài khoản.
* `created_at` (DATETIME): Thời điểm tạo tài khoản.

#### 2. Bảng `folders` (Thư mục)
* `id` (INT, Primary Key): Mã thư mục.
* `name` (VARCHAR(128), Not Null): Tên thư mục.
* `owner_id` (INT, Foreign Key -> `users.id`): Người sở hữu.
* `parent_id` (INT, Foreign Key -> `folders.id`, Nullable): Thư mục cha (cấu trúc cây).
* `is_deleted` (BOOLEAN, Default False): Cờ xóa mềm.

#### 3. Bảng `stored_files` (Tệp tin lưu trữ)
* `id` (INT, Primary Key): Mã tệp tin.
* `filename` (VARCHAR(255), Not Null): Tên tệp hiển thị.
* `storage_path` (VARCHAR(512), Not Null): Đường dẫn lưu trữ đĩa vật lý (`instance/uploads/`).
* `file_size` (BIGINT): Dung lượng tệp (bytes).
* `mime_type` (VARCHAR(128)): Định dạng tệp.
* `owner_id` (INT, Foreign Key -> `users.id`): Người sở hữu (OWNER).
* `folder_id` (INT, Foreign Key -> `folders.id`, Nullable): Thư mục chứa.
* `is_deleted` (BOOLEAN, Default False): Cờ xóa mềm.

#### 4. Bảng `file_shares` (Phân quyền chia sẻ tệp)
* `id` (INT, Primary Key): Mã bản ghi chia sẻ.
* `file_id` (INT, Foreign Key -> `stored_files.id`): Mã tệp tin.
* `shared_with_user_id` (INT, Foreign Key -> `users.id`): Người được chia sẻ.
* `permission` (VARCHAR(20), Default 'VIEWER'): Quyền được cấp (`VIEWER`).

#### 5. Bảng `export_jobs` (Lịch sử xuất dữ liệu)
* `id` (INT, Primary Key): Mã tiến trình export.
* `user_id` (INT, Foreign Key -> `users.id`): Người thực hiện.
* `export_type` (VARCHAR(50)): Loại xuất dữ liệu (`zip`, `csv`).
* `file_count` (INT): Số lượng tệp được xuất.
* `status` (VARCHAR(20)): Trạng thái (`COMPLETED`, `FAILED`).

#### 6. Bảng `request_logs` (Nhật ký truy cập cấu trúc - Structured Log)
* `id` (INT, Primary Key): Mã log.
* `timestamp` (DATETIME, Index): Thời gian phát sinh request.
* `user_id` (INT, Nullable): ID người thực hiện (Null nếu chưa login).
* `session_id_hash` (VARCHAR(64)): Chuỗi băm SHA-256 của Session ID.
* `ip_address` (VARCHAR(45)): Địa chỉ IP client.
* `http_method` (VARCHAR(10)): Method HTTP (`GET`, `POST`, `DELETE`,...).
* `endpoint` (VARCHAR(128)): Route Flask tương ứng.
* `action` (VARCHAR(64)): Hành động chi tiết (`download_file`, `export_metadata`, `delete_file`).
* `action_type` (VARCHAR(32)): Phân loại nhóm hành động (`export`, `delete`, `view_detail`, `auth`).
* `is_sensitive` (BOOLEAN): Cờ đánh dấu thao tác nhạy cảm.
* `resource_type` (VARCHAR(32)): Loại tài nguyên (`file`, `folder`, `system`).
* `resource_id` (INT, Nullable): ID của tài nguyên bị tác động.
* `authorization_result` (VARCHAR(20)): Kết quả kiểm tra quyền (`ALLOWED`, `DENIED`).
* `status_code` (INT): Mã trạng thái HTTP (200, 403, 404, 500).
* `response_time_ms` (FLOAT): Thời gian xử lý request (milliseconds).

#### 7. Bảng `alerts` (Cảnh báo bất thường ML)
* `id` (INT, Primary Key): Mã cảnh báo.
* `created_at` (DATETIME): Thời điểm tạo cảnh báo.
* `user_id` (INT): User nghi vấn.
* `session_id_hash` (VARCHAR(64)): Session nghi vấn.
* `window_start` (DATETIME): Thời gian bắt đầu cửa sổ 5 phút.
* `window_end` (DATETIME): Thời gian kết thúc cửa sổ 5 phút.
* `anomaly_score` (FLOAT): Điểm bất thường từ mô hình Isolation Forest.
* `scenario_hint` (VARCHAR(64)): Gợi ý kịch bản (`Export Abuse`, `Delete Abuse`, `BOLA Scan`).
* `status` (VARCHAR(20), Default 'Pending'): Trạng thái (`Pending`, `Investigating`, `Resolved`, `Ignored`).
* `feature_vector_json` (TEXT): Chuỗi JSON lưu giá trị 11 đặc trưng tại thời điểm phát hiện.

### 3.3. Cơ chế Bảo mật Log & Bảo vệ Quyền riêng tư (Privacy-Preserving Logging)
Để tuân thủ các tiêu chuẩn bảo mật dữ liệu (như OWASP Logging Cheat Sheet & GDPR):
1. **Mã hóa Session ID (`session_id_hash`)**: Chuỗi Flask Session ID thực tế không bao giờ được lưu trực tiếp dạng plaintext mà được đi qua hàm băm an toàn **SHA-256**.
2. **Ẩn thông tin nhạy cảm (PII Redaction)**: Mật khẩu người dùng (`password`), Token khôi phục không bao giờ được ghi vào log.
3. **Log Interception an toàn**: Middleware `request_logging.py` ghi log bất đồng bộ/không chặn (Non-blocking exception handling), đảm bảo nếu tiến trình DB bị gián đoạn thì request chính của người dùng vẫn phản hồi bình thường.

---

## CHƯƠNG 4: XÂY DỰNG BỘ DỮ LIỆU & TRÍCH XUẤT ĐẶC TRƯNG (FEATURE ENGINEERING)

### 4.1. Nguồn Dữ liệu & Phương pháp Thu thập
Hệ thống sử dụng phương pháp **Tự thu thập dữ liệu trên ứng dụng thực tế (Self-generated Log Collector)** thông qua 4 kịch bản giả lập người dùng (`scripts/simulate_*.py`):

* `simulate_normal.py`: Giả lập người dùng bình thường (đăng nhập, duyệt danh mục file, tải xuống 1-2 file cá nhân, đăng xuất).
* `simulate_export_abuse.py`: Giả lập tài khoản thực hiện xuất liên tục 30-50 tệp tin ZIP/CSV trong vài phút.
* `simulate_delete_abuse.py`: Giả lập tài khoản xóa dồn dập hàng chục tệp tin và thư mục.
* `simulate_bola_scan.py`: Giả lập kịch bản tấn công IDOR bằng cách thay đổi ID liên tục từ 1 đến 500, gây ra hàng loạt lỗi `403 Forbidden` và `404 Not Found`.

**Kết quả thu thập**: Tổng cộng **5.567 dòng request log thô** được ghi nhận vào bảng `request_logs`.

### 4.2. Kỹ thuật Gom nhóm Cửa sổ Thời gian (Time-Windowing)
Thay vì phân tích từng request đơn lẻ (vốn thiếu ngữ cảnh hành vi), dữ liệu log được gom nhóm theo **Cửa sổ thời gian cố định 5 phút (5-minute Non-overlapping Sliding Window)** dựa trên bộ khóa `(user_id, session_id_hash)`.

### 4.3. Biểu thức Toán học Hình thức của 11 Đặc trưng (11 Feature Formulations)

Giả sử trong cửa sổ thời gian 5 phút $W$, một phiên làm việc phát sinh danh sách $N$ request $R = \{r_1, r_2, \dots, r_N\}$ với mốc thời gian tương ứng $\{t_1, t_2, \dots, t_N\}$. Các đặc trưng được hình thức hóa bằng công thức toán học như sau:

1. **Tổng số request ($f_1$)**: $f_1 = N = |R|$
2. **Số endpoint duy nhất ($f_2$)**: $f_2 = |\text{Unique}(\{\text{endpoint}(r_i) \mid i=1..N\})|$
3. **Khoảng thời gian trung bình giữa 2 request ($f_3$)**: $f_3 = \mu_{\Delta t} = \frac{1}{N-1} \sum_{i=1}^{N-1} (t_{i+1} - t_i)$ (với $N > 1$, ngược lại bằng $0$)
4. **Tỷ lệ lỗi HTTP ($f_4$)**: $f_4 = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{status\_code}(r_i) \ge 400)$
5. **Số lượng thao tác Export ($f_5$)**: $f_5 = \sum_{i=1}^N \mathbb{I}(\text{action\_type}(r_i) = \text{'export'})$
6. **Số lượng thao tác Delete ($f_6$)**: $f_6 = \sum_{i=1}^N \mathbb{I}(\text{action\_type}(r_i) = \text{'delete'})$
7. **Số tài nguyên bị xóa độc lập ($f_7$)**: $f_7 = |\text{Unique}(\{\text{resource\_id}(r_i) \mid \text{action}(r_i) = \text{'delete\_file'}\})|$
8. **Tổng số resource_id truy cập độc lập ($f_8$)**: $f_8 = |\text{Unique}(\{\text{resource\_id}(r_i) \mid r_i \text{ tác động tài nguyên}\})|$
9. **Tỷ lệ lỗi 403 Forbidden ($f_9$)**: $f_9 = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{status\_code}(r_i) = 403)$
10. **Tỷ lệ lỗi 404 Not Found ($f_{10}$)**: $f_{10} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{status\_code}(r_i) = 404)$
11. **Số tài nguyên truy cập thất bại độc lập ($f_{11}$)**: $f_{11} = |\text{Unique}(\{\text{resource\_id}(r_i) \mid \text{status\_code}(r_i) \in \{403, 404\}\})|$

### 4.4. Quy tắc Phân chia Tập Dữ liệu (Dataset Splitting Policy & Anti Data Leakage)
Để đảm bảo tính trung thực khoa học và tránh hiện tượng rò rỉ dữ liệu (Data Leakage) giữa các giai đoạn huấn luyện và kiểm thử, quy trình phân chia dữ liệu được thiết kế theo các nguyên tắc nghiêm ngặt trong module `ml/build_features.py`:

```text
                               ┌──────────────────────────────────────────────┐
                               │   Toàn bộ Vector Đặc trưng Cửa sổ 5 phút     │
                               └──────────────────────┬───────────────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       │ Gom nhóm theo Group Key: (run_id, user_id, session_hash)   │
                       └──────────────────────────────┬──────────────────────────────┘
                                                      │
          ┌───────────────────────────────────────────┼───────────────────────────────────────────┐
          ▼                                           ▼                                           ▼
┌───────────────────────────┐               ┌───────────────────────────┐               ┌───────────────────────────┐
│   Tập Train (60% Normal)   │               │ Tập Validation (20% N+A)  │               │    Tập Test (20% N+A)     │
│ - Chỉ chứa mẫu Normal     │               │ - Chứa cả Normal & Anomaly│               │ - Chứa cả Normal & Anomaly│
│ - Phục vụ Unsupervised    │               │ - Phục vụ Hyperparameter  │               │ - Phục vụ Đánh giá Độc lập│
│   Isolation Forest Fit    │               │   Grid Search Tuning      │               │   Final Evaluation        │
└───────────────────────────┘               └───────────────────────────┘               └───────────────────────────┘
```

---

## CHƯƠNG 5: HUẤN LUYỆN, ĐÁNH GIÁ MÔ HÌNH VÀ TÍCH HỢP

### 5.1. Thiết lập Siêu tham số Mô hình (Hyperparameters)
Mô hình `IsolationForest` được huấn luyện với các tham số gốc:

```python
from sklearn.ensemble import IsolationForest

model = IsolationForest(
    n_estimators=100,          # Số lượng cây quyết định cô lập
    max_samples='auto',        # Kích thước mẫu lấy ngẫu nhiên = min(256, n)
    contamination='auto',      # Tự động điều chỉnh theo phân bổ score
    random_state=20260706,     # Cố định seed ngẫu nhiên
    n_jobs=-1                  # Chạy đa luồng song song trên toàn bộ CPU
)
```

* **Quy định Ngưỡng Quyết định (Decision Threshold)**: Hệ thống tính toán phân vị **95.0% (95th Percentile)** của Anomaly Score trên tập huấn luyện làm mốc quyết định ($\text{Threshold} \approx 0.485$). Nếu một cửa sổ có $\text{Score} \ge \text{Threshold}$, hệ thống gắn nhãn là `Anomaly`.

### 5.2. Phương pháp Tối ưu Siêu tham số (Hyperparameter Tuning: Grid Search)

Thuật toán thực hiện duyệt kiệt kê trên không gian lưới tham số (Search Space) trong `ml/train.py --tune`:
* `n_estimators`: $[100, 200, 300]$ (Số cây trong rừng)
* `max_samples`: `['auto', 256]` (Số lượng mẫu huấn luyện cho mỗi cây)
* `threshold_percentile`: $[90.0, 92.5, 95.0, 97.5]$ (Ngưỡng phân vị mốc Anomaly Score)

Hàm mục tiêu (Objective Function) tìm kiếm cấu hình tối ưu hóa đồng thời chỉ số **F1-Score** và giảm thiểu tỷ lệ báo động giả **False Positive Rate (FPR)** trên tập **Validation**:

$$\text{Best Params} = \arg\max_{\theta \in \Theta} \left( \text{F1-Score}_{\text{val}}(\theta) - \lambda \cdot \text{FPR}_{\text{val}}(\theta) \right)$$

Kết quả duyệt lưới cho thấy cấu hình $n\_estimators = 100$, $max\_samples = \text{'auto'}$, $threshold\_percentile = 95.0\%$ cho sự cân bằng tốt nhất trên tập dữ liệu.

### 5.3. Kết quả Đo lường & Đánh giá Thực nghiệm

Đánh giá hiệu năng mô hình trên tập dữ liệu kiểm thử độc lập (Test Set):

#### a) Bảng chỉ số định lượng
* **Accuracy (Độ chính xác tổng thể)**: **66.67%** (0.6667)
* **Precision (Độ xác thực)**: **66.67%** (0.6667)
* **Recall (Độ gợi nhớ / Độ nhạy)**: **66.67%** (0.6667)
* **F1-Score**: **66.67%** (0.6667)
* **False Positive Rate (FPR)**: **33.33%** (0.3333)

#### b) Ma trận Nhầm lẫn (Confusion Matrix)

| | Dự đoán Bình thường (Normal) | Dự đoán Bất thường (Anomaly) |
| :--- | :---: | :---: |
| **Thực tế Bình thường (Normal)** | **TN = 2** | FP = 1 |
| **Thực tế Bất thường (Anomaly)** | FN = 1 | **TP = 2** |

### 5.4. Phân tích 3 Case Study Minh họa Kịch bản Tấn công Thực tế (Attack Forensics)

#### Case Study 1: Export Abuse (Lạm dụng xuất dữ liệu)
* **Vector đặc trưng 11D**: `request_count=48`, `export_count=45`, `export_ratio=0.9375`, `avg_inter_request_sec=1.2s`, `error_rate=0.0`.
* **Kết quả mô hình**: Anomaly Score = **0.6214** (Vượt ngưỡng 0.485).
* **Kết luận**: Ghi nhận cảnh báo `CRITICAL` - gợi ý kịch bản *Export Abuse*.

#### Case Study 2: Delete Abuse (Phá hoại xóa dữ liệu)
* **Vector đặc trưng 11D**: `request_count=35`, `delete_count=32`, `unique_deleted_resource_count=30`, `avg_inter_request_sec=0.8s`.
* **Kết quả mô hình**: Anomaly Score = **0.5891** (Vượt ngưỡng 0.485).
* **Kết luận**: Ghi nhận cảnh báo `HIGH` - gợi ý kịch bản *Delete Abuse*.

#### Case Study 3: BOLA / IDOR Scan (Rà quét lỗ hổng IDOR)
* **Vector đặc trưng 11D**: `request_count=120`, `forbidden_rate=0.75`, `not_found_rate=0.15`, `unique_failed_resource_id_count=98`.
* **Kết quả mô hình**: Anomaly Score = **0.6742** (Vượt ngưỡng 0.485).
* **Kết luận**: Ghi nhận cảnh báo `CRITICAL` - gợi ý kịch bản *BOLA Scan*.

---

## CHƯƠNG 6: KIỂM THỬ VÀ ĐÁNH GIÁ THỰC NGHIỆM

### 6.1. Bộ Kiểm thử Tự động (Automated Test Suite)
Hệ thống xây dựng **38 bài test tự động** bằng thư viện `pytest`, kiểm tra toàn bộ các phân hệ:

1. `test_auth.py` (6 tests): Kiểm tra Đăng ký, Đăng nhập, CSRF Protection, Đăng xuất, Phân quyền Session.
2. `test_documents.py` (12 tests): Kiểm tra Upload file (giới hạn 20MB), Tạo folder, Download, Chia sẻ Viewer, Xóa mềm, Khôi phục, Trash.
3. `test_logging.py` (6 tests): Kiểm tra Middleware tự động bắt request, ghi đúng action, status_code, user_id và session_id_hash.
4. `test_ml_pipeline.py` (8 tests): Kiểm tra tính đúng đắn của 11 đặc trưng trích xuất, phân chia Train/Val/Test chống rò rỉ và mô hình Isolation Forest predict không lỗi.
5. `test_alerts_dashboard.py` (6 tests): Kiểm tra Admin xem danh sách alert, lọc theo trạng thái, xem chi tiết raw log và cập nhật trạng thái alert.

**Kết quả thực thi**: `38 passed in 17.87s` (100% Pass).

---

## CHƯƠNG 7: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 7.1. Đánh giá Kết quả Đạt được
* **Về mặt ứng dụng**: Xây dựng thành công hệ thống lưu trữ web StudyDrive chạy mượt mà, đầy đủ tính năng phân quyền và quản lý dữ liệu.
* **Về mặt an toàn thông tin**: Triển khai thành công hệ thống giám sát và ghi log cấu trúc tầng ứng dụng không làm ảnh hưởng tới hiệu năng ứng dụng chính.
* **Về mặt Machine Learning**: Hình thức hóa thành công bài toán theo định nghĩa khung T-P-E của Tom Mitchell. Áp dụng thuật toán Isolation Forest kết hợp với quy trình phân chia dữ liệu chống rò rỉ (Group-aware Split) và Grid Search Hyperparameter Tuning để tự động phát hiện các hành vi lạm dụng logic nghiệp vụ.

### 7.2. Hạn chế của Đề tài
* Kích thước tập dữ liệu kiểm thử thực tế còn hạn chế.
* Mô hình xử lý theo lô (Batch Processing 5 phút), chưa đạt tốc độ phát hiện thời gian thực từng giây (Real-time Stream Detection).

### 7.3. Hướng phát triển trong Tương lai
* Triển khai kỹ thuật Streaming Data Pipeline (như Apache Kafka / Celery) để đưa điểm anomaly score về dạng Real-time.
* Thử nghiệm kết hợp Isolation Forest với các thuật toán Autoencoder hoặc One-Class SVM để tăng độ chính xác trên các kịch bản BOLA phức tạp.

---

## DANH MỤC TÀI LIỆU THAM KHẢO (REFERENCES)

1. **Mitchell, T. M. (1997).** *Machine Learning.* WCB/McGraw-Hill, Boston, MA.
2. **Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008).** *Isolation Forest.* In 2008 Eighth IEEE International Conference on Data Mining (pp. 413-422). IEEE. DOI: [10.1109/ICDM.2008.17](https://doi.org/10.1109/ICDM.2008.17).
3. **OWASP Foundation (2021).** *OWASP Top 10:2021 - A01:2021-Broken Access Control & A04:2021-Insecure Design.* OWASP Top 10 Web Application Security Risks. URL: [https://owasp.org/Top10/](https://owasp.org/Top10/).
4. **Chandola, V., Banerjee, A., & Kumar, V. (2009).** *Anomaly detection: A survey.* ACM Computing Surveys (CSUR), 41(3), 1-58. DOI: [10.1145/1541880.1541882](https://doi.org/10.1145/1541880.1541882).
5. **Scikit-Learn Developers (2023).** *sklearn.ensemble.IsolationForest Documentation.* Scikit-Learn API Reference. URL: [https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html).
6. **Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., ... & Duchesnay, É. (2011).** *Scikit-learn: Machine learning in Python.* Journal of Machine Learning Research, 12, 2825-2830.
7. **Stuttard, D., & Pinto, M. (2011).** *The Web Application Hacker's Handbook: Finding and Exploiting Security Flaws (2nd ed.).* John Wiley & Sons.
8. **Buczak, A. L., & Guven, E. (2015).** *A survey of data mining and machine learning methods for cyber intrusion detection.* IEEE Communications Surveys & Tutorials, 18(2), 1153-1176. DOI: [10.1109/COMST.2015.2494502](https://doi.org/10.1109/COMST.2015.2494502).
