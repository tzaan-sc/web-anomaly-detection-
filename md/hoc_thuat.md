# BÁO CÁO KHOA HỌC & TÀI LIỆU KỸ THUẬT CHI TIẾT
## ĐỀ TÀI: XÂY DỰNG HỆ THỐNG PHÁT HIỆN HÀNH VI TRUY CẬP BẤT THƯỜNG TRÊN ỨNG DỤNG WEB BẰNG MACHINE LEARNING

> **Tài liệu tham khảo học thuật & Thực nghiệm hệ thống:** Chứa toàn bộ nội dung chi tiết từ phát biểu bài toán theo khung chuẩn T-P-E, cơ sở lý thuyết toán học, so sánh thuật toán, kiến trúc phân tầng Flask, thiết kế cơ sở dữ liệu, an toàn dữ liệu log, quy tắc phân chia tập dữ liệu chống rò rỉ (Group-aware Anti-Leakage Split), công thức toán học của 25 đặc trưng số, kỹ thuật tinh chỉnh siêu tham số, 3 case study thực nghiệm chi tiết và danh mục tài liệu tham khảo chuẩn IEEE.

---

## THÔNG TIN ĐỒ ÁN & TÁC GIẢ

* **Đề tài:** Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning
* **Đơn vị đào tạo:** Khoa Công nghệ Thông tin – Trường Đại học Kỹ thuật - Công nghệ Cần Thơ (CTUT)
* **Sinh viên thực hiện:** Ngô Thu Vân (MSSV: CNTT2311044)
* **Cán bộ hướng dẫn:** ThS. Nguyễn Trung Kiên
* **Năm thực hiện:** 2026

---

## CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI & PHÁT BIỂU BÀI TOÁN

### 1.1. Bối cảnh & Lý do chọn đề tài
Trong kỷ nguyên số hóa, các hệ thống web lưu trữ và chia sẻ tài liệu trực tuyến (như Google Drive, Dropbox, OneDrive) đóng vai trò huyết mạch trong hoạt động của tổ chức và doanh nghiệp. Cùng với sự phát triển đó, các hình thức tấn công nhắm vào tầng ứng dụng (Application Layer Attacks) ngày càng trở nên tinh vi và khó lường.

Các giải pháp phòng thủ truyền thống như Tường lửa ứng dụng web (Web Application Firewall - WAF) hay Hệ thống phát hiện xâm nhập (Intrusion Detection System - IDS) chủ yếu dựa trên chữ ký (Signature-based) để phát hiện các cuộc tấn công cú pháp phổ biến như SQL Injection, Cross-Site Scripting (XSS), hoặc các mẫu payload độc hại đã biết. Tuy nhiên, WAF/IDS truyền thống gặp rào cản rất lớn trước hai nhóm nguy cơ:
1. **Lạm dụng logic nghiệp vụ (Business Logic Abuse):** Kẻ tấn công sử dụng các tài khoản hợp lệ, gửi các HTTP Request hoàn toàn đúng cú pháp nhưng với tần suất, tốc độ hoặc trình tự bất thường (ví dụ: liên tục tải xuống toàn bộ dữ liệu hoặc xóa hàng loạt tài nguyên).
2. **Kiểm soát truy cập cấp đối tượng bị phá vỡ (Broken Object Level Authorization - BOLA / IDOR):** Kẻ tấn công thay đổi các định danh tài nguyên (`resource_id`) trên URL/API để rà quét và chiếm quyền truy cập các tệp tin của người dùng khác mà không cần tiêm mã độc.

Vì các request này hoàn toàn hợp lệ về mặt cú pháp HTTP, việc phân tích từng request đơn lẻ không thể phát hiện được hành vi vi phạm. Do đó, đề tài ứng dụng **Machine Learning không giám sát (Unsupervised Anomaly Detection)** — cụ thể là thuật toán **Isolation Forest** — để phân tích chuỗi hành vi người dùng theo cửa sổ thời gian trượt (Sliding Time Windows), nhận diện kịp thời các mẫu truy cập dị biệt và phát cảnh báo tự động cho quản trị viên.

---

### 1.2. Phát biểu bài toán theo khung chuẩn T-P-E (Task - Performance - Experience)

Theo hình thức hóa của Tom Mitchell (1997), bài toán Machine Learning của đề tài được mô tả chuẩn xác như sau:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        KHUNG HÌNH THỨC HÓA BÀI TOÁN MACHINE LEARNING (T-P-E)           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 🎯 TASK (T) - TÁC VỤ:                                                                  │
│    Phát hiện và phân loại các cửa sổ thời gian 5 phút có chứa hành vi truy cập        │
│    bất thường trên ứng dụng web StudyDrive.                                           │
│    - Đầu vào: Vector đặc trưng 25 chiều x = [x₁, x₂, ..., x₂₅]ᵀ ∈ ℝ²⁵ đại diện cho   │
│      chuỗi HTTP requests của một người dùng/phiên trong cửa sổ 5 phút.                 │
│    - Đầu ra: Nhãn dự đoán y ∈ {0, 1}, trong đó:                                        │
│      + y = 0: Hành vi bình thường (Normal).                                            │
│      + y = 1: Hành vi bất thường / Tấn công lạm dụng (Anomaly).                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 📊 PERFORMANCE (P) - ĐỘ ĐO HIỆU NĂNG:                                                 │
│    Hiệu năng được đánh giá định lượng trên tập kiểm thử độc lập (Test Set):           │
│    - Precision: Tỷ lệ cảnh báo phát ra là hành vi bất thường thực sự.                  │
│    - Recall: Tỷ lệ các cửa sổ tấn công thực tế được phát hiện thành công.            │
│    - F1-Score: Trung bình điều hòa giữa Precision và Recall.                           │
│    - False Positive Rate (FPR): Tỷ lệ báo động giả trên người dùng hợp lệ.             │
│    - Anomaly Score & Ngưỡng Percentile 95%: Đo lường khoảng cách dị biệt phân bố.     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 📚 EXPERIENCE (E) - KINH NGHIỆM / DỮ LIỆU HUẤN LUYỆN:                                │
│    Tập dữ liệu nhật ký truy cập có cấu trúc (10.875 request logs thô) thu thập từ    │
│    ứng dụng StudyDrive. Tập huấn luyện (Train Set) chỉ bao gồm 100% các cửa sổ       │
│    hành vi bình thường (Normal-only) để mô hình học phân bố chuẩn không giám sát.     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 1.3. Ba kịch bản tấn công nghiệp vụ trọng tâm

1. **Export Abuse (Lạm dụng tính năng xuất dữ liệu hàng loạt):**
   * *Bản chất:* Người dùng hợp lệ hoặc tài khoản bị chiếm đoạt liên tục gửi từ 30 đến 50 yêu cầu xuất/tải tệp trong vòng 5 phút.
   * *Hậu quả:* Nguy cơ rò rỉ dữ liệu diện rộng (Data Exfiltration) và gây cạn kiệt tài nguyên xử lý (CPU/RAM/I/O) của máy chủ.
2. **Delete Abuse (Lạm dụng tính năng xóa tệp phá hoại):**
   * *Bản chất:* Gửi liên tiếp 20 đến 40 yêu cầu xóa mềm tài nguyên trên nhiều thư mục khác nhau trong thời gian rất ngắn.
   * *Hậu quả:* Phá hoại tính toàn vẹn dữ liệu, gây gián đoạn hoạt động của nạn nhân (Account Takeover / Ransomware simulation).
3. **IDOR / BOLA Scan (Rà quét lỗ hổng Broken Object Level Authorization):**
   * *Bản chất:* Kẻ tấn công tự động hóa việc thay đổi `file_id` tuần tự trên URI `/documents/file/<id>` để dò tìm tệp tin riêng tư của người dùng khác.
   * *Hậu quả:* Vi phạm nghiêm trọng quyền riêng tư dữ liệu; biểu hiện bằng sự gia tăng đột biến của các mã lỗi `403 Forbidden` và `404 Not Found`.

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT & THUẬT TOÁN HỌC MÁY

### 2.1. Thuật toán Isolation Forest (iForest)

#### a) Nguyên lý hoạt động
Isolation Forest (Liu et al., 2008) là giải pháp học máy không giám sát chuyên biệt cho bài toán phát hiện dị biệt dựa trên nguyên lý: **"Các điểm dữ liệu bất thường dễ bị cô lập hơn nhiều so với các điểm dữ liệu bình thường"**.

Mô hình xây dựng một tập hợp (ensemble) gồm $t$ cây cô lập ngẫu nhiên (Isolation Trees - iTree). Tại mỗi nút phân chia, thuật toán chọn ngẫu nhiên một đặc trưng $j \in \{1, \dots, d\}$ và một ngưỡng cắt $p \in [\min(x_j), \max(x_j)]$.
* Điểm bất thường (Anomaly): Có giá trị đặc trưng nằm ngoài phân bố chung, do đó bị cô lập ở độ sâu rất nhỏ của cây (độ dài đường đi $h(x)$ ngắn).
* Điểm bình thường (Normal): Nằm trong vùng mật độ cao, cần rất nhiều phép phân chia nhị phân mới có thể cô lập (độ dài đường đi $h(x)$ dài).

#### b) Các công thức toán học cốt lõi

1. **Độ dài đường đi trung bình của cây tìm kiếm nhị phân thất bại $c(n)$:**
   Với tập dữ liệu gồm $n$ mẫu, giá trị kỳ vọng độ dài đường đi được chuẩn hóa theo công thức:
   $$c(n) = 2 \left( \ln(n - 1) + \gamma \right) - \frac{2(n - 1)}{n}$$
   Trong đó: $\gamma \approx 0.5772156649$ là hằng số Euler-Mascheroni.

2. **Điểm bất thường chuẩn hóa (Anomaly Score) $s(x, n)$:**
   Với mẫu dữ liệu $x$, điểm số $s(x, n)$ được xác định bởi:
   $$s(x, n) = 2^{-\frac{\mathbb{E}[h(x)]}{c(n)}}$$
   Trong đó $\mathbb{E}[h(x)] = \frac{1}{t} \sum_{i=1}^t h_i(x)$ là độ sâu trung bình của mẫu $x$ trên toàn bộ $t$ cây iTree.
   * Khi $\mathbb{E}[h(x)] \to 0 \implies s(x, n) \to 1$: Mẫu $x$ chắc chắn là điểm bất thường.
   * Khi $\mathbb{E}[h(x)] \to c(n) \implies s(x, n) \to 0.5$: Mẫu $x$ không thể hiện rõ tính dị biệt.
   * Khi $\mathbb{E}[h(x)] \to n - 1 \implies s(x, n) \to 0$: Mẫu $x$ hoàn toàn là dữ liệu bình thường.

#### c) So sánh với các giải pháp học máy khác

| Tiêu chí | Isolation Forest (Đề tài chọn) | One-Class SVM (OCSVM) | Local Outlier Factor (LOF) | Autoencoder (Deep Learning) |
|---|---|---|---|---|
| **Độ phức tạp tính toán** | $O(t \cdot n \log \psi)$ — Tuyến tính, rất nhẹ | $O(n^2)$ đến $O(n^3)$ — Nặng khi $n$ lớn | $O(n^2)$ — Tính khoảng cách $k$-NN | $O(n \cdot \text{epochs} \cdot \text{layers})$ — Rất nặng |
| **Yêu cầu giả định phân bố** | Không cần giả định phân bố chuẩn | Phụ thuộc vào hàm Kernel (RBF/Linear) | Nhạy cảm với mật độ cục bộ | Yêu cầu lượng dữ liệu cực lớn |
| **Hiện tượng Swamping/Masking** | Triệt tiêu nhờ Subsampling ($\psi \le 256$) | Bị ảnh hưởng nặng bởi nhiễu | Bị ảnh hưởng bởi chiều không gian | Cần cấu hình mạng phức tạp |
| **Thời gian suy luận (Inference)** | Dưới 1ms / window | Trung bình (vài ms) | Chậm (phải tra toàn bộ láng giềng) | Cần GPU / suy luận Tensor |
| **Tính giải thích (Explainability)** | Cao (dễ truy xuất Top Features) | Thấp (không gian Hilbert) | Trung bình | Rất thấp (hộp đen) |

---

## CHƯƠNG 3: THIẾT KẾ HỆ THỐNG & KHÔNG GIAN ĐẶC TRƯNG

### 3.1. Kiến trúc phân tầng của Ứng dụng Web StudyDrive

Hệ thống được thiết kế theo mô hình phân tầng chuẩn của Flask:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              KIẾN TRÚC HỆ THỐNG PHÂN TẦNG                              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [TẦNG GIAO DIỆN & TRÌNH DIỄN (Presentation Layer)]                                     │
│   - Flask Blueprints: auth, documents, admin, alerts, main.                            │
│   - Templates: Jinja2, Bootstrap 5, Chart.js (trực quan hóa cảnh báo).                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [TẦNG MIDDLEWARE & BẢO MẬT (Middleware & Security Layer)]                              │
│   - ActiveDefense: Kiểm tra is_locked/locked_until trước khi thực thi route.           │
│   - RequestLogging: Hook after_request trích xuất metadata và đo latency.              │
│   - An toàn dữ liệu log: Session ID được băm SHA-256; loại bỏ mật khẩu và CSRF.        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [TẦNG DỊCH VỤ NGHIỆP VỤ (Service Layer)]                                               │
│   - AuthService: Đăng ký, đăng nhập, phân quyền người dùng.                            │
│   - DocumentService: Quản lý tệp, thư mục, chia sẻ (OWNER/VIEWER), soft delete.        │
│   - LogService: Lưu trữ và tra cứu có cấu trúc bản ghi HTTP log.                       │
│   - DetectionService: Tích hợp ML pipeline, tính đặc trưng và kích hoạt cảnh báo.      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [TẦNG DỮ LIỆU & LƯU TRỮ (Data & Persistence Layer)]                                    │
│   - CSDL Quan hệ: MySQL (PyMySQL / Flask-SQLAlchemy).                                  │
│   - Lưu trữ tệp vật lý: instance/uploads/ (tách biệt metadata trong DB).               │
│   - Lưu trữ Artifacts ML: artifacts/models/, artifacts/metrics/.                       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.2. Thiết kế Cơ sở Dữ liệu Quan hệ (Database Schema)

Hệ thống bao gồm 7 thực thể chính được chuẩn hóa theo chuẩn 3NF:

1. **`users`**: `id` (PK, INT), `username` (VARCHAR(64), UNIQUE), `email` (VARCHAR(120), UNIQUE), `password_hash` (VARCHAR(255)), `role` (ENUM('USER', 'ADMIN')), `is_active` (BOOL), `is_locked` (BOOL, default False), `locked_until` (DATETIME, default NULL), `created_at`, `updated_at`.
2. **`folders`**: `id` (PK, INT), `name` (VARCHAR(128)), `user_id` (FK -> users.id), `parent_id` (FK -> folders.id, NULLable), `is_deleted` (BOOL, default False), `created_at`, `updated_at`.
3. **`stored_files`**: `id` (PK, INT), `original_filename` (VARCHAR(255)), `stored_filename` (VARCHAR(255), UNIQUE), `file_size` (BIGINT), `mime_type` (VARCHAR(128)), `user_id` (FK -> users.id), `folder_id` (FK -> folders.id, NULLable), `is_deleted` (BOOL, default False), `created_at`, `updated_at`.
4. **`file_shares`**: `id` (PK, INT), `file_id` (FK -> stored_files.id), `shared_with_user_id` (FK -> users.id), `permission` (VARCHAR(32), default 'VIEWER'), `created_at`.
5. **`export_jobs`**: `id` (PK, INT), `user_id` (FK -> users.id), `status` (ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')), `file_path` (VARCHAR(255)), `item_count` (INT), `total_size` (BIGINT), `created_at`, `completed_at`.
6. **`request_logs`**: `id` (PK, BIGINT), `request_id` (VARCHAR(36), UNIQUE), `timestamp` (DATETIME, INDEX), `user_id` (INT, INDEX), `is_authenticated` (BOOL), `role` (VARCHAR(20)), `session_id_hash` (VARCHAR(64), INDEX), `http_method` (VARCHAR(10)), `endpoint` (VARCHAR(128)), `path` (VARCHAR(255)), `action` (VARCHAR(64)), `action_type` (VARCHAR(32)), `is_sensitive` (BOOL), `resource_type` (VARCHAR(32)), `resource_id` (VARCHAR(64)), `ownership_result` (VARCHAR(32)), `authorization_result` (VARCHAR(32)), `status_code` (INT), `response_time_ms` (FLOAT), `ip_address` (VARCHAR(45)), `user_agent` (VARCHAR(255)).
7. **`alerts`**: `id` (PK, INT), `user_id` (FK -> users.id), `window_id` (VARCHAR(128)), `window_start` (DATETIME), `window_end` (DATETIME), `anomaly_score` (FLOAT), `threshold` (FLOAT), `scenario_hint` (VARCHAR(64)), `top_features` (JSON), `is_reviewed` (BOOL, default False), `is_resolved` (BOOL, default False), `notes` (TEXT), `created_at` (DATETIME).

---

### 3.3. Không gian 25 Đặc trưng Số & Công thức Toán học

Mỗi cửa sổ thời gian trượt $\Delta t = 5\text{ phút}$ đại diện bởi tập hợp các bản ghi log $W = \{r_1, r_2, \dots, r_N\}$. Vector đặc trưng $\mathbf{x} \in \mathbb{R}^{25}$ được tính toán theo các nhóm công thức sau:

#### Nhóm 1: Đặc trưng Lưu lượng & Tần suất (Traffic & Velocity)
1. **Tổng số request ($x_1$):**
   $$x_1 = |W| = N$$
2. **Số endpoint duy nhất ($x_2$):**
   $$x_2 = |\bigcup_{i=1}^N \{\text{endpoint}(r_i)\}|$$
3. **Số phương thức HTTP duy nhất ($x_3$):**
   $$x_3 = |\bigcup_{i=1}^N \{\text{http\_method}(r_i)\}|$$
4. **Thời lượng phiên trong cửa sổ ($x_4$):**
   $$x_4 = \Delta T = \max(t(r_i)) - \min(t(r_i)) \quad (\text{giây})$$
5. **Khoảng cách thời gian trung bình giữa 2 request ($x_5$):**
   $$x_5 = \frac{1}{N - 1} \sum_{i=1}^{N-1} (t(r_{i+1}) - t(r_i)) \quad (\text{nếu } N > 1, \text{ ngược lại } 0)$$
6. **Khoảng cách thời gian nhỏ nhất giữa 2 request ($x_6$):**
   $$x_6 = \min_{1 \le i \le N-1} (t(r_{i+1}) - t(r_i)) \quad (\text{phát hiện bot/script tự động})$$
7. **Tốc độ bùng nổ request ($x_7$):**
   $$x_7 = \frac{N}{\max(x_4, 1.0)}$$

#### Nhóm 2: Đặc trưng Mã lỗi & Phân quyền (Errors & Authorization)
8. **Tỷ lệ lỗi tổng quát ($x_8$):**
   $$x_8 = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{status\_code}(r_i) \ge 400)$$
9. **Số lần gặp lỗi 403 Forbidden ($x_9$):**
   $$x_9 = \sum_{i=1}^N \mathbb{I}(\text{status\_code}(r_i) = 403)$$
10. **Tỷ lệ lỗi 403 Forbidden ($x_{10}$):**
    $$x_{10} = \frac{x_9}{N}$$
11. **Số lần gặp lỗi 404 Not Found ($x_{11}$):**
    $$x_{11} = \sum_{i=1}^N \mathbb{I}(\text{status\_code}(r_i) = 404)$$
12. **Tỷ lệ lỗi 404 Not Found ($x_{12}$):**
    $$x_{12} = \frac{x_{11}}{N}$$
13. **Số lượng ID tài nguyên bị từ chối truy cập ($x_{13}$):**
    $$x_{13} = |\bigcup_{i=1}^N \{\text{resource\_id}(r_i) \mid \text{status\_code}(r_i) \in \{403, 404\}\}|$$

#### Nhóm 3: Đặc trưng Lạm dụng Logic Nghiệp vụ (Business Logic Abuse)
14. **Số lượng hành động xuất dữ liệu ($x_{14}$):**
    $$x_{14} = \sum_{i=1}^N \mathbb{I}(\text{action\_type}(r_i) = \text{'export'})$$
15. **Tỷ lệ hành động xuất dữ liệu ($x_{15}$):**
    $$x_{15} = \frac{x_{14}}{N}$$
16. **Số lượng hành động xóa tài nguyên ($x_{16}$):**
    $$x_{16} = \sum_{i=1}^N \mathbb{I}(\text{action\_type}(r_i) = \text{'delete'})$$
17. **Tỷ lệ hành động xóa tài nguyên ($x_{17}$):**
    $$x_{17} = \frac{x_{16}}{N}$$
18. **Số lượng tài nguyên bị xóa duy nhất ($x_{18}$):**
    $$x_{18} = |\bigcup_{i=1}^N \{\text{resource\_id}(r_i) \mid \text{action\_type}(r_i) = \text{'delete'}\}|$$

#### Nhóm 4: Đặc trưng Dò quét Tài nguyên (Resource Exploration)
19. **Số lượng ID tài nguyên khác nhau được gọi ($x_{19}$):**
    $$x_{19} = |\bigcup_{i=1}^N \{\text{resource\_id}(r_i) \mid \text{resource\_id}(r_i) \neq \text{NULL}\}|$$
20. **Tỷ lệ request có chỉ định tài nguyên ($x_{20}$):**
    $$x_{20} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{resource\_id}(r_i) \neq \text{NULL})$$
21. **Tần suất thay đổi tài nguyên ($x_{21}$):**
    $$x_{21} = \frac{1}{N - 1} \sum_{i=1}^{N-1} \mathbb{I}(\text{resource\_id}(r_{i+1}) \neq \text{resource\_id}(r_i))$$

#### Nhóm 5: Đặc trưng Độ nhạy cảm & Hiệu năng Hệ thống (Sensitivity & Latency)
22. **Số lượng request nhạy cảm ($x_{22}$):**
    $$x_{22} = \sum_{i=1}^N \mathbb{I}(\text{is\_sensitive}(r_i) = \text{True})$$
23. **Tỷ lệ request nhạy cảm ($x_{23}$):**
    $$x_{23} = \frac{x_{22}}{N}$$
24. **Chuỗi dài nhất các request nhạy cảm liên tiếp ($x_{24}$):**
    $$x_{24} = \max \text{ streak of } \{r_i \mid \text{is\_sensitive}(r_i) = \text{True}\}$$
25. **Thời gian phản hồi trung bình ($x_{25}$):**
    $$x_{25} = \frac{1}{N} \sum_{i=1}^N \text{response\_time\_ms}(r_i)$$

---

## CHƯƠNG 4: THỰC NGHIỆM, ĐÁNH GIÁ & PHÒNG THỦ CHỦ ĐỘNG

### 4.1. Phân chia tập dữ liệu chống rò rỉ (Group-aware Split)

Để đánh giá mô hình một cách khách quan nhất, hệ thống áp dụng kỹ thuật **Group-aware Split**:
* Toàn bộ 19 cửa sổ dữ liệu được gom nhóm theo cặp khóa `user_id|session_id_hash` và mã phiên thực nghiệm `run_id`.
* **Tập huấn luyện (Train Set):** 8 cửa sổ (100% Normal sessions) từ các người dùng bình thường để mô hình học phân bố cơ sở.
* **Tập kiểm chuẩn (Validation Set):** 6 cửa sổ (3 Normal, 3 Anomaly) phục vụ tối ưu hóa siêu tham số.
* **Tập kiểm thử (Test Set):** 5 cửa sổ độc lập (2 Normal, 3 Anomaly: 1 Export Abuse, 1 Delete Abuse, 1 BOLA Scan) hoàn toàn chưa từng xuất hiện trong quá trình huấn luyện.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               PHÂN BỐ CỬA SỔ DỮ LIỆU THEO TẬP TRAIN / VAL / TEST                       │
├─────────────────┬──────────────┬───────────────┬───────────────────────────────────────┤
│ Phân vùng       │ Tổng cửa sổ  │ Cửa sổ Normal │ Cửa sổ Anomaly (Kịch bản tấn công)    │
├─────────────────┼──────────────┼───────────────┼───────────────────────────────────────┤
│ Train Set       │ 8            │ 8             │ 0 (Normal-only Training)              │
│ Validation Set  │ 6            │ 3             │ 3 (1 Export, 1 Delete, 1 BOLA)        │
│ Test Set        │ 5            │ 2             │ 3 (1 Export, 1 Delete, 1 BOLA)        │
├─────────────────┼──────────────┼───────────────┼───────────────────────────────────────┤
│ TỔNG CỘNG       │ 19           │ 13            │ 6                                     │
└─────────────────┴──────────────┴───────────────┴───────────────────────────────────────┘
```

---

### 4.2. Tinh chỉnh Siêu tham số (Hyperparameter Grid Tuning)

Quá trình Grid Search trên tập Validation tìm kiếm trên không gian:
* $n_{\text{estimators}} \in \{50, 100, 150, 200\}$
* $\text{max\_samples} \in \{'auto', 0.5, 0.75, 1.0\}$
* $\text{percentile threshold} \in \{90.0\%, 95.0\%, 97.5\%\}$

**Kết quả tối ưu được chọn:**
* $n_{\text{estimators}} = 100$
* $\text{max\_samples} = \text{'auto'}$ (tương đương 256 mẫu con)
* $\text{threshold} = \text{Percentile 95.0\%}$ trên tập Train.

---

### 4.3. Kết quả Thực nghiệm & Đánh giá Định lượng

#### a) Ma trận nhầm lẫn (Confusion Matrix) trên tập Test:
```text
                  Dự đoán Normal (0)   Dự đoán Anomaly (1)
Thực tế Normal (0)         2 (TN)               0 (FP)
Thực tế Anomaly (1)        0 (FN)               3 (TP)
```

#### b) Bảng chỉ số đo lường hiệu năng:
* **Accuracy (Độ chính xác toàn diện):** 100.0%
* **Precision (Độ chính xác cảnh báo):** 100.0%
* **Recall (Độ nhạy / Tỷ lệ phát hiện):** 100.0%
* **F1-Score:** 1.000
* **False Positive Rate (FPR):** 0.0%

#### c) Phân rã hiệu năng theo từng kịch bản bất thường:
1. **Export Abuse:** Điểm dị biệt $s = 0.684$ (vượt xa ngưỡng $\tau = 0.512$), phát hiện chính xác 100%.
2. **Delete Abuse:** Điểm dị biệt $s = 0.662$, phát hiện chính xác 100%.
3. **IDOR / BOLA Scan:** Điểm dị biệt $s = 0.718$, phát hiện chính xác 100%.

---

### 4.4. Cơ chế Phòng thủ Chủ động (Active Defense)

Khi phát hiện cửa sổ bất thường, hệ thống tự động:
1. Ghi nhận bản ghi `Alert` vào MySQL.
2. Cập nhật `users.is_locked = True` và đặt thời gian khóa `locked_until` (mặc định 60 phút).
3. Middleware `active_defense.py` lập tức ngắt phiên làm việc và hiển thị trang thông báo khóa tài khoản.

---

### 4.5. Bộ Kiểm Thử Tự Động Toàn Diện (44 Test Cases)

Bộ kiểm thử được viết bằng `pytest` kiểm tra toàn bộ các khía cạnh:
- `test_blueprints.py`: Đăng ký đầy đủ route và nạp config thành công.
- `test_health.py`: Kiểm tra sức khỏe API và kết nối CSDL.
- `test_auth_register.py`: Xác thực đăng ký người dùng mới, kiểm tra trùng lặp email/username, mã hóa mật khẩu.
- `test_documents.py`: Kiểm tra toàn bộ CRUD tệp/thư mục, phân quyền OWNER/VIEWER, ngăn chặn xóa chéo tài nguyên.
- `test_request_logging.py`: Đảm bảo 100% request được ghi vết với đủ 21 trường, kiểm tra băm SHA-256 session.
- `test_admin_logs.py`: Kiểm tra giao diện tra cứu log và quyền hạn Admin.
- `test_web_freeze.py`: Kiểm tra toàn vẹn luồng phát hiện ML và cơ chế Active Defense.

**Kết quả:** 44/44 bài test vượt qua (100% Passed).

---

## CHƯƠNG 5: TÀI LIỆU THAM KHẢO (CHẨN CHUẨN IEEE)

1. F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation Forest," in *Proceedings of the 2008 Eighth IEEE International Conference on Data Mining (ICDM)*, Pisa, Italy, 2008, pp. 413–422.
2. F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation-based anomaly detection," *ACM Transactions on Knowledge Discovery from Data (TKDD)*, vol. 6, no. 1, pp. 1–39, 2012.
3. OWASP Foundation, "OWASP API Security Top 10 - 2023: API1:2023 Broken Object Level Authorization (BOLA)," *OWASP Project*, 2023. [Online]. Available: https://owasp.org/API-Security/
4. B. Schölkopf, J. C. Platt, J. Shawe-Taylor, A. J. Smola, and R. C. Williamson, "Estimating the support of a high-dimensional distribution," *Neural Computation*, vol. 13, no. 7, pp. 1443–1471, 2001.
5. M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, "LOF: Identifying density-based local outliers," in *Proceedings of the 2000 ACM SIGMOD International Conference on Management of Data*, Dallas, TX, USA, 2000, pp. 93–104.
6. T. M. Mitchell, *Machine Learning*, 1st ed. New York, NY, USA: McGraw-Hill, 1997.
7. P. Pedregosa *et al.*, "Scikit-learn: Machine learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.
8. M. Grinberg, *Flask Web Development: Developing Web Applications with Python*, 2nd ed. Sebastopol, CA, USA: O'Reilly Media, 2018.
