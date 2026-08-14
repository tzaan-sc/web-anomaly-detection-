# Hướng Dẫn Vận Hành Machine Learning Pipeline (Phát Hiện Bất Thường Web)

Tài liệu này hướng dẫn chi tiết quy trình thực thi toàn bộ **Machine Learning Pipeline** của dự án **Web Anomaly Detection (StudyDrive)**, từ khâu sinh dữ liệu log giả lập, trích xuất đặc trưng, huấn luyện mô hình, kiểm định đánh giá, đến tích hợp cảnh báo và phòng thủ chủ động trên ứng dụng Web.

---

## 1. Môi trường & Yêu cầu tiên quyết

Đảm bảo môi trường ảo Python đã được kích hoạt và cài đặt đầy đủ các gói phụ thuộc:

```powershell
# Di chuyển vào thư mục dự án
cd D:\web-anomaly-detection

# Kích hoạt môi trường ảo (PowerShell)
.\.venv\Scripts\Activate.ps1

# Kiểm tra các thư viện đã cài đặt
pip check
```

Cơ sở dữ liệu MySQL phải đang hoạt động tại cổng `3306` (hoặc `3307` theo cấu hình file `.env`).

---

## 2. Quy trình Thực thi ML Pipeline (Từng bước chi tiết)

### Bước 1: Khởi tạo Dữ liệu thô từ Bộ Mô phỏng (Simulators)

Bước này thực thi bộ kịch bản tương tác tự động bao gồm 1 kịch bản người dùng bình thường và 3 kịch bản tấn công nghiệp vụ:
- `simulate_normal.py`
- `simulate_export_abuse.py`
- `simulate_delete_abuse.py`
- `simulate_bola_scan.py`

**Lệnh thực thi:**
```powershell
python scripts/generate_raw_dataset_v1.py
```

**Kết quả đầu ra:**
- `data/raw/request_logs_raw.csv`: Bản ghi 10.875 dòng log thô có cấu trúc đầy đủ 21 trường.
- `data/raw/ground_truth.csv`: Nhãn đối chứng (Normal / Anomaly và Scenario) theo từng cửa sổ 5 phút.
- `data/raw/generation_metadata.json`: Metadata về thời gian chạy và tham số sinh dữ liệu.

---

### Bước 2: Tiền xử lý Dữ liệu & Trích xuất Đặc trưng (Feature Engineering)

Module `ml.build_features` tiến hành làm sạch log, loại bỏ request rác/trùng lặp, chia log thành các cửa sổ trượt 5 phút (5-minute sliding windows) theo từng người dùng và phiên làm việc (`user_id|session_id_hash`), sau đó trích xuất **vector 25 đặc trưng số**.

**Lệnh thực thi:**
```powershell
python -m ml.build_features --logs data/raw/request_logs_raw.csv --ground-truth data/raw/ground_truth.csv --output-dir data/processed/features_v1
```

**Kết quả đầu ra (tại `data/processed/features_v1/`):**
- `clean_logs.csv`: Dữ liệu log đã chuẩn hóa thời gian và kiểm tra tính toàn vẹn.
- `windowed_logs.csv` & `window_mapping.csv`: Ánh xạ từng request vào cửa sổ 5 phút tương ứng.
- `features_all.csv`: Toàn bộ ma trận đặc trưng 25 chiều của 19 cửa sổ.
- `train_features.csv`: Tập huấn luyện (8 cửa sổ, 100% Normal).
- `validation_features.csv`: Tập kiểm chuẩn (6 cửa sổ).
- `test_features.csv`: Tập kiểm thử độc lập (5 cửa sổ).
- `feature_list.json` & `feature_dictionary.md`: Danh mục và mô tả 25 đặc trưng.
- `split_manifest.json` & `processing_report.json`: Báo cáo phân chia tập dữ liệu chống rò rỉ (Group-aware Split).

---

### Bước 3: Huấn luyện Mô hình & Tinh chỉnh Siêu tham số (Training & Tuning)

Huấn luyện mô hình **Isolation Forest** theo chiến lược **Normal-only Training** trên `train_features.csv` và chạy Grid Tuning trên `validation_features.csv` để tìm bộ siêu tham số tối ưu (`n_estimators`, `max_samples`, `percentile threshold`).

**Lệnh thực thi:**
```powershell
# Chạy huấn luyện và tối ưu siêu tham số
python -m ml.train --features-dir data/processed/features_v1 --tune
```

**Kết quả đầu ra:**
- Mô hình và pipeline chuẩn hóa đã huấn luyện lưu tại: `artifacts/models/iforest_v1/model.joblib`
- Bảng kết quả tinh chỉnh siêu tham số: `artifacts/metrics/tuning_results.csv`

---

### Bước 4: Đánh giá Mô hình trên Tập Kiểm thử (Evaluation)

Đánh giá hiệu năng của mô hình đã lưu trên tập kiểm thử độc lập `test_features.csv`, tính toán các chỉ số thống kê (Accuracy, Precision, Recall, F1-Score, False Positive Rate) và xuất các biểu đồ trực quan hóa.

**Lệnh thực thi:**
```powershell
python -m ml.evaluate --features-dir data/processed/features_v1 --model-dir artifacts/models/iforest_v1
```

**Kết quả đầu ra (tại `artifacts/metrics/`):**
- `test_metrics.json`: Các chỉ số định lượng trên tập Test.
- `test_predictions.csv`: Kết quả dự đoán chi tiết từng cửa sổ kiểm thử.
- `scenario_metrics.csv`: Báo cáo hiệu năng phân rã theo từng kịch bản bất thường.
- `confusion_matrix.png`: Biểu đồ ma trận nhầm lẫn (Confusion Matrix).
- `score_distribution.png`: Biểu đồ phân bố Anomaly Score giữa nhóm Normal và Anomaly.

---

### Bước 5: Tích hợp Web & Quét Dò tìm Bất thường (Detection & Alerts)

Tích hợp mô hình đã huấn luyện vào cơ sở dữ liệu thực tế của ứng dụng StudyDrive. Tiến trình sẽ trích xuất log từ bảng `request_logs`, tính vector 25 đặc trưng theo cửa sổ 5 phút, so khớp ngưỡng Anomaly Score, tự động lưu bản ghi vào bảng `alerts` và kích hoạt **Active Defense** để khóa tài khoản khả nghi.

**Cách 1: Chạy script dòng lệnh**
```powershell
python scripts/run_detection.py
```

**Cách 2: Kích hoạt từ Web Admin Dashboard**
- Truy cập route: `http://127.0.0.1:5000/alerts/trigger-detection` (Dành cho Quản trị viên).

---

## 3. Khởi động Ứng dụng Web & Xem Bảng điều khiển (Dashboard)

1. **Chạy máy chủ web Flask:**
   ```powershell
   python run.py
   ```
2. **Truy cập ứng dụng:** Mở trình duyệt tại địa chỉ `http://127.0.0.1:5000/`.
3. **Đăng nhập với quyền Admin:**
   - **Tài khoản:** `admin`
   - **Mật khẩu:** `StudyDriveAdmin@2026`
4. **Theo dõi Cảnh báo & Nhật ký:**
   - Quản trị Cảnh báo (Alerts Dashboard): `http://127.0.0.1:5000/alerts/`
   - Quản trị Nhật ký Request Log: `http://127.0.0.1:5000/admin/logs`
   - Quản trị Tài khoản Người dùng (Khóa/Mở khóa): `http://127.0.0.1:5000/admin/users`

---

## 4. Chạy Toàn Bộ Kiểm Thử Tự Động (Automated Testing)

Chạy toàn bộ 44 test cases bao gồm kiểm thử chức năng web, phân quyền tài nguyên, ghi log middleware, xác thực đăng ký người dùng và kiểm thử pipeline Machine Learning:

```powershell
pytest
```

**Kết quả kỳ vọng:**
```text
============================== 44 passed in 23.53s ==============================
```
