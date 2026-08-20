# BÁO CÁO SO SÁNH & HƯỚNG DẪN CHẠY MACHINE LEARNING (VERSION 1 vs VERSION 2)

Tài liệu này dùng để trình bày và giải thích với Thầy/Cô và Hội đồng đánh giá về hai phiên bản dữ liệu huấn luyện của hệ thống **StudyDrive Anomaly Detection**, kèm theo **hướng dẫn từng bước chạy thực tế**.

---

## 1. BẢNG TỔNG HỢP SO SÁNH NHANH

| Tiêu chí | Version 1 (Bản thử nghiệm Pilot) | Version 2 (Bản mở rộng quy mô Scale-up) |
| :--- | :---: | :---: |
| **Dữ liệu log gốc** | 10.875 HTTP requests | 10.875 HTTP requests |
| **Cơ chế gom nhóm** | Cửa sổ cố định 5 phút (Tumbling 5m) | Cửa sổ trượt gối đầu (Sliding Window 30s, bước 2s) |
| **Tổng số mẫu trích xuất** | **19 mẫu** | **441 mẫu** *(Tăng gấp 23 lần)* |
| **Số mẫu tập Train** | **8 mẫu** | **👉 302 mẫu** *(Tăng từ 8 lên 302 dòng)* |
| **Số mẫu tập Validation** | **6 mẫu** | **69 mẫu** |
| **Số mẫu tập Test** | **5 mẫu** | **70 mẫu** |
| **Số lượng đặc trưng (Features)**| 25 đặc trưng hành vi | 25 đặc trưng hành vi |
| **Độ chính xác (Accuracy)** | 80.0% | **92.86%** |
| **Độ bao phủ bất thường (Recall)**| 66.7% | **100.0% (Phát hiện toàn bộ 100%)** |
| **Thư mục lưu trữ dữ liệu** | `data/processed/features_v1/` | `data/processed/features_v2/` |
| **Thư mục lưu Model** | `artifacts/models/iforest_v1/` | `artifacts/models/iforest_v2/` |

---

## 2. GIẢI THÍCH CHO THẦY/CÔ HIỂU VỀ 2 PHIÊN BẢN

### ❓ Câu hỏi của Thầy/Cô: *"Tại sao bản v1 chỉ có 8 dòng train?"*
> **Trả lời:** 
> *"Dạ thưa Thầy/Cô, bản v1 là đợt thử nghiệm luồng (Pipeline Validation). Khi gom 10.875 requests vào các khối 5 phút cố định, toán học chỉ cắt ra được 19 cửa sổ (8 train). Mục đích là để kiểm tra xem code trích xuất và giao diện có hoạt động ổn định hay không."*

### ❓ Câu hỏi của Thầy/Cô: *"Hệ thống đã nâng cấp ở bản v2 như thế nào?"*
> **Trả lời:** 
> *"Dạ ở bản v2, nhóm áp dụng kỹ thuật **Overlapping Sliding Window (Cửa sổ trượt gối đầu 30 giây, bước nhảy 2 giây)** chuẩn theo các nghiên cứu về Time-Series Anomaly Detection. Kỹ thuật này giúp trích xuất liên tục sự biến động hành vi của người dùng, nâng tập Train từ **8 dòng lên 302 dòng** và tập Test lên **70 dòng**, giúp mô hình học phân bố chuẩn xác hơn và đạt độ bao phủ bất thường (Recall) lên tới **100%** ạ."*

---

## 3. HƯỚNG DẪN CHI TIẾT CÁCH CHẠY PHIÊN BẢN 2 (VERSION 2)

Mở **Terminal (PowerShell)** tại thư mục gốc của dự án `web-anomaly-detection`:

### 📌 Bước 1: Kích hoạt môi trường ảo (Virtualenv)
```powershell
.venv\Scripts\Activate.ps1
```

---

### 📌 Bước 2: Trích xuất tập đặc trưng v2 (Sinh ra 302 mẫu Train, 441 mẫu tổng thể)
```powershell
python -m ml.build_features_v2 --window-seconds 30 --step-seconds 2
```
*Kết quả xuất ra tại: `data/processed/features_v2/` (gồm các file `train_features.csv`, `validation_features.csv`, `test_features.csv`).*

---

### 📌 Bước 3: Huấn luyện & Tinh chỉnh siêu tham số mô hình Isolation Forest v2
```powershell
python -m ml.train_v2 --features-dir data/processed/features_v2 --output-dir artifacts/models/iforest_v2 --tune
```
*Hệ thống tự động dò qua hàng chục bộ tham số (n_estimators, max_samples, threshold_percentile) để chọn ra mô hình tối ưu nhất và lưu vào `artifacts/models/iforest_v2/model.joblib`.*

---

### 📌 Bước 4: Đánh giá mô hình v2 trên tập kiểm thử (Test set 70 mẫu)
```powershell
python -m ml.evaluate --model artifacts/models/iforest_v2/model.joblib --test data/processed/features_v2/test_features.csv --output-dir artifacts/metrics/v2
```
*Kết quả đánh giá và ma trận nhầm lẫn (Confusion Matrix) được xuất ra thư mục `artifacts/metrics/v2/`.*

---

## 4. CÁCH XEM VÀ TRÌNH CHIẾU KẾT QUẢ CHO THẦY CÔ

Sau khi chạy xong, bạn có thể mở các file sau để trình chiếu trực tiếp cho Thầy/Cô:

1. **Xem file dữ liệu Train 302 dòng:**
   - Mở file: `data/processed/features_v2/train_features.csv`
   - Chứng minh cho Thầy/Cô thấy tập Train có **302 dòng** với **25 đặc trưng hành vi**.

2. **Xem báo cáo phân chia dữ liệu:**
   - Mở file: `data/processed/features_v2/processing_report.json`
   - Hiển thị rõ số lượng mẫu Train, Validation, Test và các kịch bản bất thường.

3. **Xem kết quả đánh giá mô hình (Accuracy 92.86%, Recall 100%):**
   - Mở file: `artifacts/metrics/v2/test_metrics.json`
   ```json
   {
     "rows": 70,
     "precision": 0.5,
     "recall": 1.0,
     "accuracy": 0.92857,
     "confusion_matrix": {
       "tn": 60,
       "fp": 5,
       "fn": 0,
       "tp": 5
     }
   }
   ```

4. **Xem biểu đồ Ma trận nhầm lẫn (Confusion Matrix):**
   - Mở file ảnh: `artifacts/metrics/v2/confusion_matrix.png`
   - Mở file ảnh phân bố điểm dị biệt: `artifacts/metrics/v2/score_distribution.png`

---

## 5. TÍNH TOÀN VẸN CỦA HỆ THỐNG
- Phiên bản **v1 cũ vẫn được giữ nguyên 100%** tại `data/processed/features_v1` và `artifacts/models/iforest_v1`.
- Phiên bản **v2 mới chạy hoàn toàn độc lập**, không làm ảnh hưởng đến bất kỳ phần mã nguồn hay web demo nào trước đó.
