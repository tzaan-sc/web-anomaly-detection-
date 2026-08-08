# 01. YÊU CẦU & PHẠM VI DỰ ÁN (PROJECT REQUIREMENTS & SCOPE)

## 1. Thông tin đề tài
**Tên đề tài:** Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning  
**Ứng dụng nghiệp vụ:** Hệ thống lưu trữ và chia sẻ tài liệu trực tuyến (StudyDrive) với hai vai trò User và Admin.  

## 2. Mục tiêu dự án
1. Cho phép người dùng đăng nhập, đăng xuất và quản lý phiên làm việc.
2. Phân quyền hệ thống theo hai vai trò `USER` và `ADMIN`.
3. Cho phép User tạo thư mục, upload, xem, tải xuống, đổi tên, di chuyển, tìm kiếm, lọc, phân trang, export, xóa và khôi phục tệp thuộc quyền quản lý.
4. Cho phép chủ sở hữu chia sẻ từng tệp cho người dùng khác với quyền `VIEWER`; không chia sẻ thư mục trong phiên bản chính.
5. Kiểm tra quyền truy cập ở cấp đối tượng dựa trên chủ sở hữu và bản ghi chia sẻ.
6. Cho phép Admin quản lý người dùng, metadata tệp, request log và cảnh báo bất thường.
7. Thu thập structured log về hành vi truy cập, kết quả phân quyền và tài nguyên liên quan.
8. Cho phép Admin tìm kiếm, lọc, xem chi tiết và export log.
9. Chuyển log thành các đặc trưng phục vụ Machine Learning (Isolation Forest).
10. Phát hiện ba scenario: Export Abuse, Delete Abuse và IDOR/BOLA Scan.
11. Đánh giá mô hình trên dữ liệu kiểm thử có ground truth.

## 3. Đối tượng người dùng (Actors) & Phân quyền
### 3.1. Phân quyền cấp hệ thống
- **USER:** Người dùng thông thường có không gian lưu trữ cá nhân, có thể quản lý file của mình và xem các file được chia sẻ.
- **ADMIN:** Quản lý tài khoản, metadata, log và cảnh báo. Không mặc định được xem hoặc tải nội dung tệp của USER.

### 3.2. Phân quyền cấp tệp (File Permissions)
| Quyền | Ý nghĩa | Thao tác được phép |
| --- | --- | --- |
| `OWNER` | Chủ sở hữu tệp | Xem, download, đổi tên, di chuyển, chia sẻ, hủy chia sẻ, export, xóa và khôi phục |
| `VIEWER` | Người được chia sẻ | Xem metadata và download tệp |
| `NONE` | Không có quyền | Request bị từ chối bằng 403 hoặc 404 |

### 3.3. Giới hạn upload & lưu trữ
- Kích thước: Tối đa 20MB/tệp.
- Định dạng: pdf, doc/x, xls/x, ppt/x, txt, csv, png, jpg/jpeg, zip. (Cấm exe, sh, py, js...).
- Tên tệp vật lý lưu dưới dạng UUID, không dùng original name.

## 4. Danh sách Use Cases
### User
- Đăng nhập/Đăng xuất
- Xem Dashboard cá nhân
- Quản lý thư mục (Tạo, Xem)
- Quản lý tệp (Upload, Xem danh sách, Chi tiết, Tải xuống, Đổi tên, Di chuyển, Xóa, Khôi phục)
- Chia sẻ tệp & Xem tệp được chia sẻ
- Export tệp (CSV metadata / ZIP)
- Cập nhật Profile, Đổi mật khẩu

### Admin
- Đăng nhập/Đăng xuất
- Xem Dashboard quản trị
- Quản lý người dùng (Xem, Khóa/Mở khóa)
- Xem metadata tệp toàn hệ thống
- Quản lý log (Xem, Lọc, Export)
- Chạy hệ thống phát hiện bất thường (Detection)
- Quản lý Cảnh báo (Alerts)

## 5. Tiêu chí nghiệm thu (Acceptance Criteria)
- **Authentication:** Đăng nhập đúng role, sai báo lỗi chung. Cookie HttpOnly, SameSite. Bị khóa không đăng nhập được.
- **Dashboard User:** Chỉ thấy dữ liệu của mình.
- **Tệp của tôi & Upload:** Upload giới hạn 20MB, lọc đúng định dạng. Đổi tên lưu file bằng UUID.
- **Shared with me:** Chỉ xem và tải file được chia sẻ. Không thấy file bị hủy chia sẻ.
- **Trash:** Xóa mềm. Xóa vĩnh viễn cần xác nhận.
- **Export:** Export tạo Job ID. Tệp CSV hoặc ZIP.
- **Admin Logs:** Không lưu mật khẩu/cookie/token thô. Lọc/Export đúng dữ liệu.
- **Admin Alerts:** Truy ngược được log gốc và đặc trưng (features) từ cảnh báo.
- **Authorization:** Request trái quyền không làm lộ thông tin hay tải được file. Phải chặn ở API level.
