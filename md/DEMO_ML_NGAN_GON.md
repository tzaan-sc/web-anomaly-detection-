# KỊCH BẢN DEMO MACHINE LEARNING (BẢN RÚT GỌN 3 PHÚT)
## HỆ THỐNG PHÁT HIỆN BẤT THƯỜNG WEB (STUDYDRIVE)

> **Mục tiêu:** Trình diễn nhanh, trực diện phần **Machine Learning (Isolation Forest)** và **Cảnh báo bất thường** cho Hội đồng chấm đồ án trong vòng 3 phút.

---

## 1. HỆ THỐNG CÓ TỰ ĐỘNG KHÓA TÀI KHOẢN KHÔNG?

👉 **CÓ, HOÀN TOÀN TỰ ĐỘNG! (Cơ chế Active Defense)**

* **Vị trí cài đặt trong mã nguồn:** 
  - File `app/services/detection_service.py` (dòng 212–219).
  - Middleware `app/middleware/active_defense.py`.
* **Cách hoạt động:**
  1. Khi tiến trình quét ML (`run_detection`) phát hiện cửa sổ có điểm dị biệt **`anomaly_score > 0.7`** hoặc thuộc các kịch bản tấn công (`export_abuse`, `delete_abuse`, `bola_scan`), hệ thống **tự động đặt `user.locked_until = now + 60 phút`**.
  2. Kẻ tấn công ngay sau đó gửi bất kỳ request nào sẽ bị Middleware chặn đứng với lỗi **HTTP 403**:  
     *"Tài khoản của bạn đã bị khóa tạm thời do phát hiện hành vi bất thường."*
  3. Quản trị viên (Admin) có thể vào `/admin/users` để xem trạng thái và nhấn nút **Mở khóa (Unlock)** thủ công nếu cần.

---

## 2. QUY TRÌNH DEMO ML 3 BƯỚC (CHỈ CHẠY 3 LỆNH)

### 📌 Bước 1: Khởi động Web Server (Mở Terminal 1)
```powershell
python run.py
```
*(Giữ Terminal 1 luôn chạy)*

---

### 📌 Bước 2: Kích hoạt Tấn công Giả lập (Mở Terminal 2)

Chọn **1 trong 3 kịch bản** bên dưới để demo:

#### 👉 Lựa chọn A: Demo Tấn công Xuất dữ liệu (Export Abuse)
```powershell
python -m scripts.simulate_export_abuse --username user1 --severity high --fast
```
*(Gửi liên tiếp 35 request export tải dữ liệu)*

#### 👉 Lựa chọn B: Demo Tấn công Xóa phá hoại (Delete Abuse)
```powershell
python -m scripts.simulate_delete_abuse --username user2 --severity high --fast
```
*(Gửi dồn dập 28 request xóa mềm tệp tin)*

#### 👉 Lựa chọn C: Demo Tấn công Rà quét BOLA/IDOR (BOLA Scan)
```powershell
python -m scripts.simulate_bola_scan --username user3 --mode burst --fast
```
*(Gửi hàng trăm request dò quét file_id trái phép $\rightarrow$ Lỗi 403 & 404)*

---

### 📌 Bước 3: Chạy Quét Machine Learning & Xem Cảnh Báo

Tại **Terminal 2**, chạy lệnh quét phát hiện:
```powershell
python scripts/run_detection.py
```
*(Hoặc vào Web Admin nhấn nút "Run Detection")*

---

## 3. KẾT QUẢ TRÌNH CHIẾU TRÊN WEB CHO THẦY CÔ XEM

1. **Xem Cảnh báo trên Dashboard:**
   - Mở trình duyệt vào `http://127.0.0.1:5000/alerts/` (đăng nhập `admin` / `StudyDriveAdmin@2026`).
   - Thấy ngay cảnh báo mới: Tên kịch bản (**Export Abuse** / **Delete Abuse** / **BOLA Scan**), **Anomaly Score $\approx 0.68 - 0.72$** (Vượt ngưỡng $\tau = 0.512$).
   - Nhấn vào xem chi tiết để thấy **Top 3 đặc trưng đóng góp** (JSON).

2. **Chứng minh Tự Động Khóa Tài Khoản (Active Defense):**
   - Mở tab Ẩn danh, đăng nhập vào tài khoản vừa tấn công (`user1` / `user2` / `user3`).
   - Nhấp vào bất kỳ trang nào $\rightarrow$ **Bị chặn ngay lập tức với thông báo khóa 60 phút**.

3. **Xem Bằng chứng Nhật ký Gốc (Forensics):**
   - Tại trang Alert, bấm vào liên kết **"Xem Log gốc"** $\rightarrow$ Hệ thống lọc đúng chuỗi request của kẻ tấn công trong cửa sổ 5 phút.

---

## 4. CÁCH CHẠY 1 LỆNH DUY NHẤT TOÀN BỘ (NẾU THẦY CÔ CẦN XEM NHANH)

Chạy lệnh tự động hóa toàn bộ ML Pipeline (Tạo data $\rightarrow$ Feature $\rightarrow$ Train $\rightarrow$ Eval $\rightarrow$ Tạo Alert):
```powershell
python -m scripts.run_demo_scenario --scenario all --fast
```
*Thời gian chạy: 30 giây xong toàn bộ.*
