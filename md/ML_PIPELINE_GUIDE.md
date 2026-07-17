# Hướng dẫn Chạy Machine Learning Pipeline (Phát hiện Bất thường Web)

Tài liệu này hướng dẫn chi tiết các bước chạy toàn bộ ML Pipeline của dự án **Web Anomaly Detection**, bao gồm từ bước tiền xử lý dữ liệu, huấn luyện mô hình, kiểm định, cho tới tích hợp với hệ thống Web và Cảnh báo.

---

## 1. Môi trường chạy

Đảm bảo bạn đã kích hoạt môi trường ảo (virtual environment) của dự án và cài đặt đầy đủ các thư viện trong `requirements.txt`.
Đặc biệt, thư viện `matplotlib` cần thiết để trực quan hóa kết quả kiểm định.

```powershell
# Kích hoạt môi trường (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

---

## 2. Các Bước Chạy Pipeline

### Bước 1: Tiền xử lý dữ liệu & Feature Engineering
Bước này sẽ lấy dữ liệu log thô (đã được lưu hoặc sinh từ simulator) và thực hiện gom nhóm (sliding window 5 phút) để tạo ra các vector đặc trưng (Feature Vector).

**Cú pháp:**
```powershell
python -m ml.build_features
```
**Kết quả đầu ra:** Các tập tin chứa tập đặc trưng (đã xử lý) sẽ được lưu hoặc chuẩn bị sẵn sàng cho quá trình huấn luyện.

### Bước 2: Huấn luyện Mô hình & Tuning (Isolation Forest)
Tại bước này, hệ thống sử dụng thuật toán **Isolation Forest** để huấn luyện trên tập log bình thường. Hệ thống cũng chạy **Grid Tuning** trên tập validation nhằm tìm ra tham số tốt nhất.

**Cú pháp:**
```powershell
python -m ml.train
```
**Kết quả đầu ra:**
- Mô hình Isolation Forest đã huấn luyện xong (và pipeline chuẩn hóa dữ liệu).
- Tập tin lưu tại: `artifacts/models/iforest_v1/model.joblib`

### Bước 3: Kiểm định Mô hình (Evaluation)
Mô hình đã huấn luyện sẽ được đánh giá trên tập kiểm thử (test set) bao gồm cả log bình thường và log tấn công/bất thường.

**Cú pháp:**
```powershell
python -m ml.evaluate
```
**Kết quả đầu ra:**
- Báo cáo kết quả đánh giá (Precision, Recall, F1-Score).
- Các biểu đồ đánh giá tự động lưu tại thư mục `artifacts/metrics/`:
  - `confusion_matrix.png`
  - `score_distribution.png`

### Bước 4: Tích hợp Web - Quét & Lưu Vết Cảnh Báo (Alerts)
Bước cuối cùng là tích hợp mô hình vào luồng ứng dụng thực tế. Script dưới đây quét toàn bộ log trong Database thông qua Mô hình. Nếu phát hiện Request log nào bất thường, nó sẽ tự động lưu cảnh báo vào bảng `Alert` trong cơ sở dữ liệu.

**Cú pháp:**
```powershell
python scripts/run_detection.py
```
**Kết quả đầu ra:**
- In ra màn hình thông báo dò tìm thành công (ví dụ: phát hiện 4 cảnh báo bất thường).
- Dữ liệu `Alert` đã được thêm vào CSDL.

---

## 3. Quản trị viên theo dõi Cảnh Báo (Dashboard)

Sau khi hệ thống quét và lưu `Alert` thành công vào CSDL, Quản trị viên có thể xem trực quan trên Dashboard của Web Application.

1. Bật Web Server (nếu chưa bật):
   ```powershell
   python run.py
   ```
2. Truy cập vào trang Web của hệ thống và đăng nhập với tài khoản Admin:
   - **Username:** `admin`
   - **Password:** `StudyDriveAdmin@2026`
3. Truy cập vào trang **Dashboard Alert** để xem chi tiết các cảnh báo đã được ghi nhận từ bước dò tìm.

---

## 4. Kiểm thử Tự động (Testing)

Bạn cũng có thể chạy lại bộ Test tự động để đảm bảo rằng quá trình tích hợp ML và Web hoạt động chính xác.

**Cú pháp:**
```powershell
pytest
```
**Kết quả đầu ra:** Xác nhận toàn bộ bài test passed (Ví dụ: 38/38 passed).
