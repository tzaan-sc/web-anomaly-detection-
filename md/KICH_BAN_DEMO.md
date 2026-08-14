# KỊCH BẢN DEMO BẢO VỆ ĐỒ ÁN
# HỆ THỐNG PHÁT HIỆN HÀNH VI TRUY CẬP BẤT THƯỜNG TRÊN ỨNG DỤNG WEB (STUDYDRIVE)

> **Tài liệu hướng dẫn thực hành Demo trực tiếp trước Hội đồng chấm:** Trình bày theo từng bước cụ thể, có lệnh chạy dòng lệnh, thao tác trên giao diện web, kết quả mong đợi và lời thoại mẫu cho sinh viên khi thuyết trình.

---

## PHẦN 1: CHECKLIST CHUẨN BỊ TRƯỚC BUỔI BẢO VỆ

### 1.1. Kiểm tra Môi trường & Dịch vụ
1. **Cơ sở dữ liệu MySQL:** Đang chạy tại cổng `3306` (hoặc `3307` theo file `.env`).
2. **Kích hoạt Môi trường ảo Python (.venv):**
   ```powershell
   cd D:\web-anomaly-detection
   .\.venv\Scripts\Activate.ps1
   ```
3. **Khởi động Web Server Flask:** Mở **Terminal 1** và chạy:
   ```powershell
   python run.py
   ```
   *Kiểm tra Web Server hoạt động:* Mở trình duyệt truy cập `http://127.0.0.1:5000/health` $\rightarrow$ Trả về `{"status": "ok"}`.

4. **Chuẩn bị 2 Cửa sổ Trình duyệt:**
   - **Cửa sổ 1 (Chế độ Thường):** Dành cho tài khoản **Admin** (`http://127.0.0.1:5000/admin`).
   - **Cửa sổ 2 (Chế độ Ẩn danh - Incognito):** Dành cho tài khoản **Người dùng / Kẻ tấn công** (`http://127.0.0.1:5000/`).

---

### 1.2. Danh sách Tài khoản Phục vụ Demo

| Loại tài khoản | Tên đăng nhập (Username) | Mật khẩu (Password) | Vai trò & Mục đích sử dụng |
|---|---|---|---|
| **Quản trị viên (Admin)** | `admin` | `StudyDriveAdmin@2026` | Quản trị hệ thống, xem nhật ký log, theo dõi Alerts Dashboard, mở khóa tài khoản. |
| **Người dùng 1 (User 1)** | `user1` | `User1Password@2026` | Người dùng bình thường / Kẻ tấn công lạm dụng xuất dữ liệu (*Export Abuse*). |
| **Người dùng 2 (User 2)** | `user2` | `User2Password@2026` | Kẻ tấn công lạm dụng xóa phá hoại tài nguyên (*Delete Abuse*). |
| **Người dùng 3 (User 3)** | `user3` | `User3Password@2026` | Kẻ tấn công dò quét phân quyền đối tượng (*IDOR/BOLA Scan*). |
| **Người dùng 4 & 5** | `user4`, `user5` | `User4Password@2026`,... | Tài khoản phối hợp phân quyền và chia sẻ tệp tin. |

---

## PHẦN 2: CÁC KỊCH BẢN DEMO CHI TIẾT (TỪNG BƯỚC THỰC HIỆN)

---

### KỊCH BẢN 1: Khởi Tạo Trạng Thái Sạch (Reset Demo State)

* **Mục đích:** Đưa cơ sở dữ liệu và thư mục tệp tin về trạng thái chuẩn ban đầu (5 người dùng mẫu, 1 admin, các thư mục và tệp tin sẵn sàng).
* **Lệnh thực thi (Terminal 2):**
  ```powershell
  python -m scripts.reset_demo
  ```
* **Kết quả hiển thị:**
  ```text
  Reset demo hoàn tất: 6 users, 6 folders, 12 files, 4 shares.
  ```
* **Lời thoại thuyết trình:**  
  > *"Kính thưa Thầy Cô, trước tiên em chạy script `reset_demo` để khởi tạo lại toàn bộ cơ sở dữ liệu MySQL và thư mục lưu trữ `instance/uploads/` về trạng thái ban đầu với các tài khoản và tệp tin mẫu."*

---

### KỊCH BẢN 2: Trình Diễn Chức Năng Web StudyDrive & Cơ Chế Phân Quyền (RBAC)

* **Mục đích:** Chứng minh ứng dụng Web StudyDrive hoạt động trơn tru với đầy đủ các nghiệp vụ quản lý tài liệu và phân quyền cấp đối tượng (`OWNER` / `VIEWER`).

#### Các bước thực hiện trên giao diện Web:
1. **Đăng ký tài khoản mới:**
   - Truy cập `http://127.0.0.1:5000/auth/register`.
   - Đăng ký tài khoản `testuser` / `TestPassword@2026` $\rightarrow$ Đăng ký thành công và tự động đăng nhập.
2. **Tạo thư mục & Tải lên tệp tin (Upload):**
   - Đăng nhập tài khoản `user1` / `User1Password@2026`.
   - Vào menu **Tài liệu** (`/documents/`) $\rightarrow$ Tạo thư mục mới *"Báo cáo Thực tập"*.
   - Nhấn nút **Tải lên tệp** $\rightarrow$ Tải lên một tệp tin PDF/Word mẫu $\rightarrow$ Tệp được lưu vật lý dưới mã UUID tại `instance/uploads/`.
3. **Phân quyền chia sẻ tệp (File Sharing):**
   - Tại tệp tin vừa tải lên của `user1`, nhấn nút **Chia sẻ**.
   - Chọn chia sẻ cho `user2` với quyền **VIEWER**.
4. **Kiểm tra quyền truy cập:**
   - Mở cửa sổ ẩn danh, đăng nhập tài khoản `user2`.
   - `user2` xem được tệp tin được chia sẻ và có thể tải xuống (`Download`), nhưng không có nút **Xóa** hoặc **Chia sẻ tiếp**.
5. **Xóa mềm (Soft Delete) & Khôi phục Thùng rác (Trash):**
   - `user1` thực hiện xóa một tệp tin $\rightarrow$ Tệp chuyển vào **Thùng rác** (`/documents/trash`).
   - Vào Thùng rác nhấn **Khôi phục (Restore)** $\rightarrow$ Tệp tin quay trở lại thư mục gốc.

* **Lời thoại thuyết trình:**  
  > *"Như Thầy Cô thấy, StudyDrive hỗ trợ đầy đủ các tính năng lưu trữ đám mây: tạo cây thư mục, tải tệp an toàn, phân quyền chặt chẽ theo cấp đối tượng OWNER và VIEWER, cơ chế xóa mềm bảo vệ dữ liệu không bị mất vĩnh viễn."*

---

### KỊCH BẢN 3: Trình Diễn Cơ Chế Ghi Nhật Ký Có Cấu Trúc (Structured Request Logging)

* **Mục đích:** Chứng minh Middleware của Flask tự động ghi vết 21 trường dữ liệu và băm bảo mật SHA-256 session ID mà không làm giảm hiệu năng.

#### Các bước thực hiện:
1. Đăng nhập tài khoản **Admin** (`admin` / `StudyDriveAdmin@2026`).
2. Truy cập trang **Quản trị Nhật ký** tại `http://127.0.0.1:5000/admin/logs`.
3. Nhấp vào một bản ghi log bất kỳ để xem chi tiết:
   - `timestamp`, `user_id`, `role` (`USER`).
   - `session_id_hash`: Chuỗi băm SHA-256 (không lưu session ID thô).
   - `action`: `upload_file`, `download_file`, `delete_file`...
   - `authorization_result`: `allowed` hoặc `denied`.
   - `response_time_ms`: Thời gian xử lý (trung bình < 5ms).
   - Các trường bảo mật: Mật khẩu và CSRF token đã được lọc bỏ hoàn toàn.

* **Lời thoại thuyết trình:**  
  > *"Mọi tương tác vừa rồi của người dùng đều được Middleware `request_logging.py` tự động ghi vết tại sự kiện `after_request` với 21 trường có cấu trúc lưu vào bảng `request_logs`. Toàn bộ Session ID đều được băm SHA-256 để đảm bảo tuyệt đối tính riêng tư."*

---

### KỊCH BẢN 4: Mô Phỏng 3 Kịch Bản Tấn Công & Phát Hiện Bất Thường Bằng Machine Learning

---

#### 4.1. Kịch bản Tấn công 1: Lạm Dụng Xuất Dữ Liệu Hàng Loạt (Export Abuse)

* **Hành vi mô phỏng:** Tài khoản `user1` gửi liên tiếp 35 yêu cầu export CSV / ZIP trong vòng vài giây nhằm vét dữ liệu.
* **Thực thi tấn công (Terminal 2):**
  ```powershell
  python -m scripts.simulate_export_abuse --username user1 --severity high --fast
  ```
* **Quét phát hiện bất thường (Terminal 2 hoặc bấm 'Run Detection' trên Web):**
  ```powershell
  python scripts/run_detection.py
  ```
* **Kết quả kiểm tra trên Alerts Dashboard (`http://127.0.0.1:5000/alerts/`):**
  - Xuất hiện Cảnh báo mới: **Export Abuse**.
  - **User bị nghi vấn:** `user1`.
  - **Anomaly Score:** $\approx 0.684$ (Vượt ngưỡng $\tau = 0.512$).
  - **Top Đặc trưng nổi bật:** `export_count = 35`, `export_ratio = 0.85`, `avg_inter_request_sec = 0.35s`.
* **Lời thoại thuyết trình:**  
  > *"Em vừa kích hoạt kịch bản Export Abuse trên tài khoản user1. Mô hình Isolation Forest đã phân tích cửa sổ 5 phút và phát hiện Anomaly Score đạt 0.684, vượt xa ngưỡng cho phép và đưa ra cảnh báo chính xác kịch bản Export Abuse."*

---

#### 4.2. Kịch bản Tấn công 2: Lạm Dụng Xóa Tài Nguyên Phá Hoại (Delete Abuse)

* **Hành vi mô phỏng:** Tài khoản `user2` gửi dồn dập 28 yêu cầu xóa mềm tệp tin trên nhiều thư mục khác nhau trong thời gian ngắn.
* **Thực thi tấn công (Terminal 2):**
  ```powershell
  python -m scripts.simulate_delete_abuse --username user2 --severity high --fast
  ```
* **Quét phát hiện bất thường:**
  ```powershell
  python scripts/run_detection.py
  ```
* **Kết quả trên Alerts Dashboard:**
  - Xuất hiện Cảnh báo: **Delete Abuse**.
  - **User bị nghi vấn:** `user2`.
  - **Anomaly Score:** $\approx 0.662$.
  - **Top Đặc trưng nổi bật:** `delete_count = 28`, `delete_ratio = 0.78`, `unique_deleted_resource_count = 28`.
* **Lời thoại thuyết trình:**  
  > *"Tiếp theo là kịch bản Delete Abuse trên user2. Hệ thống phát hiện tần suất xóa tệp tăng đột biến với 28 tệp khác nhau bị xóa trong cửa sổ 5 phút và tự động phát cảnh báo cho Admin."*

---

#### 4.3. Kịch bản Tấn công 3: Rà Quét Lỗ Hổng Phân Quyền Đối Tượng (IDOR / BOLA Scan)

* **Hành vi mô phỏng:** Tài khoản `user3` sử dụng script tự động thay đổi liên tiếp hàng trăm `file_id` không thuộc sở hữu trên URI `/documents/file/<id>` để dò tìm tệp tin của người khác.
* **Thực thi tấn công (Terminal 2):**
  ```powershell
  python -m scripts.simulate_bola_scan --username user3 --mode burst --fast
  ```
* **Quét phát hiện bất thường:**
  ```powershell
  python scripts/run_detection.py
  ```
* **Kết quả trên Alerts Dashboard:**
  - Xuất hiện Cảnh báo: **BOLA Scan (Broken Object Level Authorization)**.
  - **User bị nghi vấn:** `user3`.
  - **Anomaly Score:** $\approx 0.718$ (Điểm bất thường rất cao).
  - **Top Đặc trưng nổi bật:** `forbidden_count = 150`, `not_found_count = 50`, `unique_failed_resource_id_count = 195`, `resource_id_change_rate = 0.99`.
* **Lời thoại thuyết trình:**  
  > *"Cuối cùng là kịch bản BOLA/IDOR Scan trên user3. Kẻ tấn công dò quét hàng trăm ID tệp khiến tỷ lệ mã lỗi 403 và 404 tăng vọt. Mô hình Isolation Forest đã gán điểm dị biệt 0.718 và chỉ ra dấu hiệu rà quét phân quyền rõ rệt."*

---

### KỊCH BẢN 5: Trình Diễn Cơ Chế Phòng Thủ Chủ Động (Active Defense)

* **Mục đích:** Chứng minh hệ thống không chỉ dừng lại ở việc phát cảnh báo thụ động mà có khả năng **chủ động ngăn chặn tấn công** ngay lập tức.

#### Các bước thực hiện:
1. **Kiểm tra trạng thái khóa tài khoản:**
   - Sau khi phát hiện cảnh báo ở Kịch bản 4, tài khoản `user3` (hoặc `user1`) đã tự động bị hệ thống kích hoạt Active Defense: đặt cờ `is_locked = True` và thời hạn khóa `locked_until = now + 60 phút`.
2. **Thử nghiệm thao tác từ phía Kẻ tấn công:**
   - Mở trình duyệt của `user3`, nhấp vào bất kỳ liên kết nào trên StudyDrive (ví dụ `/documents/`).
   - **Hiện tượng:** Middleware `active_defense.py` lập tức ngắt phiên làm việc, chuyển hướng người dùng đến trang thông báo:  
     **"Tài khoản của bạn đã bị khóa tạm thời 60 phút do phát hiện hành vi truy cập bất thường. Vui lòng liên hệ Quản trị viên."**
3. **Thao tác Quản trị viên can thiệp (Admin Unlock):**
   - Đăng nhập tài khoản Admin $\rightarrow$ Truy cập menu **Quản lý Người dùng** (`http://127.0.0.1:5000/admin/users`).
   - Admin nhìn thấy trạng thái tài khoản `user3` đang hiển thị huy hiệu `Locked (Active Defense)`.
   - Admin nhấn nút **Mở khóa (Unlock)** $\rightarrow$ Tài khoản `user3` trở lại trạng thái hoạt động bình thường.

* **Lời thoại thuyết trình:**  
  > *"Đây là điểm cải tiến quan trọng của đề tài: Cơ chế Phòng thủ chủ động (Active Defense). Ngay khi mô hình ML phát hiện bất thường, Middleware sẽ tự động khóa tạm thời tài khoản trong 60 phút để ngăn chặn kẻ tấn công tiếp tục phá hoại, đồng thời Admin có thể chủ động mở khóa lại sau khi đã xác minh an toàn."*

---

### KỊCH BẢN 6: Trình Diễn Điều Tra & Truy Vết Nhật Ký Gốc (Forensic Log Investigation)

* **Mục đích:** Chứng minh tính khả thi trong thực tế khi Quản trị viên cần bằng chứng số để điều tra sự cố an ninh.

#### Các bước thực hiện:
1. Tại trang **Alerts Dashboard** (`http://127.0.0.1:5000/alerts/`), nhấn vào nút **Chi tiết** của cảnh báo BOLA Scan.
2. Nhấn vào liên kết **"Xem danh sách 200 Request Log gốc trong cửa sổ này"**.
3. Hệ thống lọc và hiển thị chính xác toàn bộ chuỗi request của kẻ tấn công trong đúng khung giờ 5 phút đó:
   - Các dòng request liên tiếp với mã lỗi `403 Forbidden` và `404 Not Found`.
   - Hiển thị rõ các URI mục tiêu bị rà quét (`/documents/file/101`, `/documents/file/102`,...).

* **Lời thoại thuyết trình:**  
  > *"Từ cảnh báo của mô hình ML, Quản trị viên có thể nhấp chuột để truy ngược trực tiếp về toàn bộ các bản ghi log thô nguyên bản trong CSDL để phục vụ công tác điều tra số liệu và báo cáo sự cố."*

---

### KỊCH BẢN 7: Tự Động Hóa Toàn Bộ Quy Trình Bằng 1 Lệnh (One-Click Demo Orchestrator)

* **Mục đích:** Dành cho trường hợp Hội đồng muốn xem chạy toàn bộ từ đầu đến cuối một cách nhanh chóng và tự động.
* **Lệnh thực thi (Terminal 2):**
  ```powershell
  python -m scripts.run_demo_scenario --scenario all --fast
  ```
* **Quy trình script tự động thực hiện tuần tự:**
  1. Reset dữ liệu CSDL và tệp tin sạch.
  2. Sinh log người dùng bình thường (`simulate_normal.py`).
  3. Sinh log 3 kịch bản tấn công (`simulate_export_abuse`, `simulate_delete_abuse`, `simulate_bola_scan`).
  4. Trích xuất đặc trưng 25 chiều (`ml.build_features`).
  5. Huấn luyện mô hình và Grid Tuning (`ml.train`).
  6. Đánh giá kiểm định và xuất biểu đồ (`ml.evaluate`).
  7. Quét phát hiện bất thường và ghi nhận cảnh báo vào CSDL (`scripts.run_detection`).
* **Thời gian thực thi:** Khoảng **30 – 45 giây**.

---

### KỊCH BẢN 8: Trình Diễn Kết Quả Bộ Kiểm Thử Tự Động (44 Test Cases)

* **Mục đích:** Chứng minh mã nguồn đạt chất lượng cao, không có lỗi tiềm ẩn và vượt qua 100% các bài test tự động.
* **Lệnh thực thi (Terminal 2):**
  ```powershell
  pytest
  ```
* **Kết quả hiển thị trên màn hình:**
  ```text
  ============================== 44 passed in 14.80s ==============================
  ```
* **Lời thoại thuyết trình:**  
  > *"Để đảm bảo tính tin cậy tuyệt đối, em đã xây dựng bộ kiểm thử tự động với 44 bài test bao gồm kiểm thử phân quyền tệp, xác thực đăng ký người dùng, cơ chế ghi log tầng middleware và pipeline phát hiện ML. Toàn bộ 44/44 bài test đều vượt qua 100%."*

---

## PHẦN 3: BẢNG TÓM TẮT CÁC LỆNH NHANH KHI DEMO (CHEAT SHEET)

```powershell
# ==============================================================================
# BẢNG TỔNG HỢP LỆNH DÒNG LỆNH PHỤC VỤ BUỔI BẢO VỆ ĐỒ ÁN
# ==============================================================================

# 1. Kích hoạt môi trường ảo:
.\.venv\Scripts\Activate.ps1

# 2. Khởi động Web Server (Mở Terminal riêng):
python run.py

# 3. Reset CSDL về trạng thái sạch ban đầu:
python -m scripts.reset_demo

# 4. Chạy từng kịch bản tấn công:
python -m scripts.simulate_export_abuse --username user1 --severity high --fast
python -m scripts.simulate_delete_abuse --username user2 --severity high --fast
python -m scripts.simulate_bola_scan --username user3 --mode burst --fast

# 5. Kích hoạt quét phát hiện bất thường:
python scripts/run_detection.py

# 6. Chạy tự động toàn bộ quy trình demo (One-Click):
python -m scripts.run_demo_scenario --scenario all --fast

# 7. Chạy bộ kiểm thử tự động 44 test cases:
pytest
```
