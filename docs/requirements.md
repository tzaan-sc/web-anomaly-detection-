# REQUIREMENTS — HỆ THỐNG LƯU TRỮ VÀ CHIA SẺ TÀI LIỆU TRỰC TUYẾN

## 1. Mục đích tài liệu

Tài liệu này chốt yêu cầu nghiệp vụ và yêu cầu kỹ thuật cốt lõi để quá trình code không phải thay đổi cấu trúc giữa chừng. Hệ thống phục vụ hai vai trò cấp hệ thống là `USER` và `ADMIN`; quyền truy cập trên từng tệp gồm `OWNER`, `VIEWER` và `NONE`.

Trong phiên bản chính:

- Chỉ chia sẻ **tệp**, không chia sẻ thư mục.
- Người được chia sẻ chỉ có quyền `VIEWER`.
- Chỉ `OWNER` được đổi tên, di chuyển, chia sẻ, xóa, khôi phục và xóa vĩnh viễn tệp.
- `ADMIN` quản lý tài khoản, metadata, log và cảnh báo; không mặc định được tải nội dung mọi tệp.
- Machine Learning chỉ phát hiện hành vi bất thường, không thay thế Authentication hoặc Authorization.

---

## 2. Actor

### 2.1. USER

Người dùng thông thường có không gian lưu trữ cá nhân và có thể:

- Đăng nhập, đăng xuất.
- Xem dashboard.
- Tạo thư mục.
- Tải tệp lên.
- Xem, tìm kiếm, lọc, phân trang tệp.
- Tải tệp thuộc sở hữu hoặc được chia sẻ.
- Đổi tên, di chuyển, chia sẻ và xóa tệp do mình sở hữu.
- Xem các tệp được chia sẻ với mình.
- Xem thùng rác, khôi phục hoặc xóa vĩnh viễn tệp của mình.
- Tạo yêu cầu export danh sách CSV hoặc gói ZIP theo quyền hợp lệ.
- Xem profile và đổi mật khẩu.

### 2.2. ADMIN

Admin có thể:

- Đăng nhập vào khu vực quản trị.
- Xem thống kê hệ thống.
- Tìm kiếm, khóa hoặc mở khóa tài khoản.
- Xem metadata tệp và thư mục.
- Xem, lọc, phân trang và export request log.
- Chạy quá trình phát hiện bất thường.
- Xem, lọc và cập nhật trạng thái cảnh báo.
- Truy ngược alert về window và log gốc.

Admin không được xem password, cookie, token nguyên bản hoặc nội dung riêng tư của tệp chỉ vì có role `ADMIN`.

---

## 3. Ma trận quyền

| Hành động | OWNER | VIEWER | USER không có quyền | ADMIN |
|---|---:|---:|---:|---:|
| Xem metadata tệp | Có | Có | Không | Chỉ metadata phục vụ quản trị |
| Tải tệp | Có | Có | Không | Không mặc định |
| Đổi tên tệp | Có | Không | Không | Không mặc định |
| Di chuyển tệp | Có | Không | Không | Không mặc định |
| Chia sẻ/hủy chia sẻ tệp | Có | Không | Không | Không mặc định |
| Xóa mềm tệp | Có | Không | Không | Không mặc định |
| Khôi phục/xóa vĩnh viễn | Có | Không | Không | Không mặc định |
| Export tệp | Có | Theo chính sách export | Không | Không mặc định |
| Tạo/xóa thư mục cá nhân | Có | Không áp dụng | Không | Không mặc định |
| Quản lý user | Không | Không | Không | Có |
| Xem request log | Chỉ lịch sử cá nhân nếu có | Không | Không | Có |
| Chạy detection/xem alert | Không | Không | Không | Có |

### 3.1. Quy tắc quyết định quyền

Một user được **xem hoặc tải tệp** khi:

```text
file.owner_id == current_user.id
HOẶC
tồn tại file_share(file_id, current_user.id, permission = VIEWER)
```

Một user được **thay đổi tệp** khi:

```text
file.owner_id == current_user.id
```

Một user được thao tác với thư mục khi:

```text
folder.owner_id == current_user.id
```

Một user được tải kết quả export khi:

```text
export_job.requested_by == current_user.id
VÀ
export_job.status == COMPLETED
```

---

## 4. Use case

## UC01 — Đăng nhập

- **Actor:** USER, ADMIN
- **Tiền điều kiện:** Tài khoản tồn tại và chưa bị khóa.
- **Luồng chính:**
  1. Người dùng nhập email/username và mật khẩu.
  2. Hệ thống kiểm tra CSRF token.
  3. Hệ thống xác minh mật khẩu hash và trạng thái tài khoản.
  4. Hệ thống tạo session.
  5. Hệ thống redirect đến dashboard phù hợp.
- **Ngoại lệ:** Sai thông tin → báo lỗi; tài khoản bị khóa → từ chối.
- **Action log:** `LOGIN_SUCCESS`, `LOGIN_FAILED`.
- **Kết quả:** Session hợp lệ được tạo.

## UC02 — Xem dashboard

- **Actor:** USER
- **Tiền điều kiện:** Đã đăng nhập.
- **Dữ liệu:** Tổng tệp, thư mục, tệp được chia sẻ, tệp trong thùng rác, hoạt động gần đây.
- **Action log:** `VIEW_DASHBOARD`.
- **Kết quả:** Chỉ hiển thị thống kê thuộc phạm vi user hiện tại.

## UC03 — Tạo thư mục

- **Actor:** USER
- **Tiền điều kiện:** Đã đăng nhập.
- **Đầu vào:** Tên thư mục, `parent_folder_id` tùy chọn.
- **Kiểm tra quyền:** Parent folder phải thuộc user.
- **Action log:** `CREATE_FOLDER`.
- **Kết quả:** Thư mục mới được tạo.

## UC04 — Upload tệp

- **Actor:** USER
- **Đầu vào:** File, `folder_id` tùy chọn.
- **Kiểm tra:** Kích thước, extension, MIME type, tên file, quyền với folder.
- **Lưu trữ:** Tên hiển thị giữ nguyên; tên lưu vật lý dùng UUID.
- **Action log:** `UPLOAD_FILE`.
- **Kết quả:** Metadata và file vật lý được lưu nhất quán.

## UC05 — Xem và tải tệp

- **Actor:** OWNER hoặc VIEWER
- **Đầu vào:** `file_id`.
- **Kiểm tra:** User là owner hoặc có bản ghi chia sẻ `VIEWER`.
- **Action log:** `VIEW_FILE`, `DOWNLOAD_FILE`, hoặc `PERMISSION_DENIED`.
- **Kết quả:** Trả metadata hoặc nội dung tệp nếu có quyền.

## UC06 — Đổi tên và di chuyển tệp

- **Actor:** OWNER
- **Đầu vào:** `file_id`, tên mới hoặc `folder_id` đích.
- **Kiểm tra:** File và folder đích đều thuộc owner.
- **Action log:** `RENAME_FILE`, `MOVE_FILE`.
- **Kết quả:** Metadata được cập nhật, không đổi tên file vật lý UUID.

## UC07 — Chia sẻ và hủy chia sẻ tệp

- **Actor:** OWNER
- **Đầu vào:** `file_id`, email/user_id người nhận.
- **Giới hạn:** Chỉ chia sẻ file; permission duy nhất là `VIEWER`.
- **Action log:** `SHARE_FILE`, `REVOKE_SHARE`.
- **Kết quả:** Tạo hoặc xóa bản ghi `file_shares`.

## UC08 — Xem “Được chia sẻ với tôi”

- **Actor:** USER
- **Dữ liệu:** Các file chưa bị xóa và có `file_shares` hợp lệ.
- **Action log:** `VIEW_SHARED_FILES`.
- **Kết quả:** Không hiển thị folder của owner hoặc file đã bị hủy chia sẻ.

## UC09 — Xóa mềm, thùng rác và khôi phục

- **Actor:** OWNER
- **Đầu vào:** `file_id`.
- **Luồng:** Xóa mềm → xem thùng rác → khôi phục hoặc xóa vĩnh viễn.
- **Action log:** `DELETE_FILE`, `RESTORE_FILE`, `PERMANENT_DELETE_FILE`.
- **Kết quả:** File bị ẩn khỏi danh sách thông thường khi `is_deleted = true`.

## UC10 — Export

- **Actor:** USER
- **Đầu vào:** Loại export, danh sách `file_id` hoặc bộ lọc.
- **Loại:** CSV metadata hoặc ZIP tệp.
- **Kiểm tra:** Mỗi file phải thuộc quyền hợp lệ theo chính sách export.
- **Dữ liệu:** Tạo `export_job`.
- **Action log:** `CREATE_EXPORT_JOB`, `DOWNLOAD_EXPORT`.
- **Kết quả:** Job có trạng thái `PENDING`, `PROCESSING`, `COMPLETED` hoặc `FAILED`.

## UC11 — Quản lý user

- **Actor:** ADMIN
- **Chức năng:** Danh sách, tìm kiếm, khóa/mở tài khoản.
- **Action log:** `ADMIN_VIEW_USERS`, `ADMIN_LOCK_USER`, `ADMIN_UNLOCK_USER`.
- **Kết quả:** User bị khóa không thể tạo session mới.

## UC12 — Quản lý log và cảnh báo

- **Actor:** ADMIN
- **Chức năng:** Lọc log, xem chi tiết, export CSV, chạy detection, xem alert.
- **Action log:** `ADMIN_VIEW_LOGS`, `ADMIN_EXPORT_LOGS`, `RUN_DETECTION`, `UPDATE_ALERT`.
- **Kết quả:** Alert truy ngược được về log gốc.

---

## 5. Mức ưu tiên chức năng

### M0 — Bắt buộc

- Authentication, session, CSRF.
- Role `USER`/`ADMIN`.
- Folder cá nhân.
- Upload, danh sách, xem, tải tệp.
- OWNER/VIEWER và chia sẻ file.
- Search, filter, pagination.
- Xóa mềm, thùng rác, khôi phục.
- Export CSV/ZIP.
- Structured logging.
- Admin log management.
- Simulator normal và ba anomaly.
- Feature engineering, Isolation Forest, alert.

### M1 — Nên có

- Đổi tên và di chuyển tệp.
- Profile và đổi mật khẩu.
- Xóa vĩnh viễn có xác nhận.
- Dashboard thống kê.
- Export history.
- Admin quản lý metadata tệp.

### M2 — Chỉ làm khi M0/M1 ổn định

- Preview PDF/ảnh.
- Kéo thả upload.
- Biểu đồ đẹp.
- Download progress hoặc upload progress nâng cao.
- Thông báo trong ứng dụng.

---

## 6. Giới hạn upload và lưu trữ

### 6.1. Kích thước

- Tối đa **20 MB cho mỗi tệp** trong bản chính.
- Có thể cấu hình bằng `MAX_CONTENT_LENGTH`.
- Request vượt giới hạn trả `413 Payload Too Large`.

### 6.2. Loại file cho phép

```text
.pdf
.doc
.docx
.xls
.xlsx
.ppt
.pptx
.txt
.csv
.png
.jpg
.jpeg
.zip
```

Không cho phép:

```text
.exe
.bat
.cmd
.ps1
.sh
.php
.py
.js
.jar
```

Kiểm tra cả extension và MIME type; không chỉ tin tên file từ client.

### 6.3. Quy tắc tên file

- `original_name`: tên hiển thị của người dùng, đã sanitize.
- `stored_name`: UUID ngẫu nhiên + extension hợp lệ.
- Không dùng tên gốc làm tên file vật lý.
- Không cho phép path traversal như `../`.
- Ví dụ:

```text
original_name = "Bao cao do an.pdf"
stored_name = "0d5a59f4-2c55-4bb0-a1de-d9e2283df340.pdf"
```

---

## 7. Yêu cầu phi chức năng

- Password phải hash, không lưu plaintext.
- Các form thay đổi dữ liệu phải có CSRF token.
- Cookie session cấu hình `HttpOnly`, `SameSite=Lax`; `Secure` khi dùng HTTPS.
- Request trái quyền không làm lộ metadata hoặc nội dung tệp.
- Log không chứa password, cookie, session token thô hoặc nội dung tệp.
- Database có index cho `timestamp`, `user_id`, `session_id_hash`, `action`, `status_code`.
- Các thao tác M0 phải có validation và error handling.
- Hệ thống phải reset/seed được để demo lặp lại.
- Chỉ chạy simulator trên hệ thống local của chính dự án.

---

## 8. Điều kiện khóa thiết kế

Thiết kế được xem là đủ để bắt đầu code khi:

- Mỗi màn hình có route tương ứng.
- Mỗi route xác định rõ actor và permission.
- Mỗi hành động quan trọng xác định được action log.
- Mỗi object có bảng dữ liệu và khóa ngoại tương ứng.
- Status code thành công và lỗi được quy ước.
- Giới hạn upload và quy tắc lưu file đã cố định.
