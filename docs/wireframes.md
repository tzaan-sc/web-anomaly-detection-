# WIREFRAMES — HỆ THỐNG LƯU TRỮ VÀ CHIA SẺ TÀI LIỆU

Các wireframe dưới đây tập trung vào cấu trúc và luồng thao tác, chưa quy định màu sắc hoặc thiết kế chi tiết.

---

## 1. Login

```text
+--------------------------------------------------------------+
|                         LOGO / TÊN HỆ THỐNG                  |
+------------------------------+-------------------------------+
|                              |  ĐĂNG NHẬP                    |
|  Hình minh họa / mô tả       |  Email/Username [__________]  |
|  ngắn về hệ thống            |  Mật khẩu       [__________]  |
|                              |  [ ] Ghi nhớ đăng nhập        |
|                              |  [ ĐĂNG NHẬP ]                |
|                              |  Quên mật khẩu                 |
+------------------------------+-------------------------------+
```

- **Route:** `GET/POST /login`
- **Dữ liệu:** `users`, session.
- **Quyền:** Public.
- **Action log:** `LOGIN_SUCCESS`, `LOGIN_FAILED`.

---

## 2. Dashboard User

```text
+------------------+-------------------------------------------+
| Sidebar          | Header: Tìm kiếm | Thông báo | Avatar    |
| - Tổng quan      +-------------------------------------------+
| - Tệp của tôi    | Xin chào, User                              |
| - Được chia sẻ   | [Tổng tệp] [Thư mục] [Được chia sẻ]       |
| - Gần đây        | [Trong thùng rác]                          |
| - Thùng rác      +-------------------------------------------+
| - Export         | Tệp gần đây                                |
| - Cài đặt        | Tên | Chủ sở hữu | Ngày sửa | Hành động   |
+------------------+-------------------------------------------+
```

- **Route:** `GET /dashboard`
- **Dữ liệu:** `files`, `folders`, `file_shares`, `request_logs`.
- **Quyền:** USER.
- **Action log:** `VIEW_DASHBOARD`.

---

## 3. Tệp của tôi

```text
+------------------+-------------------------------------------+
| Sidebar          | Breadcrumb: Tệp của tôi / [Folder]        |
|                  | [Tạo thư mục] [Tải tệp lên] [Export]      |
|                  | Search [_______] Loại [v] Sắp xếp [v]     |
|                  +-------------------------------------------+
|                  | [ ] Tên       Chủ sở hữu  Kích thước      |
|                  | [ ] Folder A  Tôi          --              |
|                  | [ ] BaoCao.pdf Tôi         2.3 MB   [...]  |
|                  | [ ] Slide.pptx Tôi         5.1 MB   [...]  |
|                  +-------------------------------------------+
|                  | Trang 1 / 5   < 1 2 3 >                   |
+------------------+-------------------------------------------+
```

- **Route:** `GET /files`, `GET /folders/{folder_id}`.
- **Dữ liệu:** `files`, `folders`.
- **Quyền:** Chỉ owner.
- **Action log:** `LIST_FILES`, `VIEW_FOLDER`.

---

## 4. Upload

```text
+--------------------------------------------------------------+
| TẢI TỆP LÊN                                                   |
|                                                              |
| +----------------------------------------------------------+ |
| | Kéo thả hoặc chọn tệp                                   | |
| | Tối đa 20 MB                                            | |
| +----------------------------------------------------------+ |
| Thư mục đích: [ Tệp của tôi / Báo cáo v ]                   |
| Danh sách tệp đã chọn:                                      |
| - BaoCao.pdf      2.3 MB                                    |
|                                                              |
| [Hủy]                                         [Tải lên]     |
+--------------------------------------------------------------+
```

- **Route:** `GET/POST /files/upload`.
- **Dữ liệu:** `files`, `folders`.
- **Quyền:** USER; folder đích phải thuộc owner.
- **Action log:** `UPLOAD_FILE`, `UPLOAD_REJECTED`.

---

## 5. Được chia sẻ với tôi

```text
+------------------+-------------------------------------------+
| Sidebar          | ĐƯỢC CHIA SẺ VỚI TÔI                     |
|                  | Search [________] Loại [v]                 |
|                  +-------------------------------------------+
|                  | Tên tệp   Chủ sở hữu  Quyền   Ngày chia   |
|                  | A.pdf     user_a       VIEWER  09/06/2026 |
|                  | B.docx    user_b       VIEWER  10/06/2026 |
|                  |                         [Xem] [Tải]        |
+------------------+-------------------------------------------+
```

- **Route:** `GET /shared-with-me`.
- **Dữ liệu:** `file_shares`, `files`, `users`.
- **Quyền:** USER có share hợp lệ.
- **Action log:** `VIEW_SHARED_FILES`.

---

## 6. Chi tiết tệp

```text
+--------------------------------------------------------------+
| Breadcrumb: Tệp của tôi / Đồ án / BaoCao.pdf                 |
|                                                              |
| [Icon PDF] BaoCao.pdf                                        |
| Chủ sở hữu: Tôi          Quyền hiện tại: OWNER               |
| Kích thước: 2.3 MB       Loại: application/pdf               |
| Ngày tạo: 10/06/2026     Cập nhật: 10/06/2026                |
|                                                              |
| [Tải xuống] [Đổi tên] [Di chuyển] [Chia sẻ] [Xóa]            |
|                                                              |
| Người được chia sẻ:                                          |
| user_b@example.com | VIEWER | [Hủy chia sẻ]                  |
+--------------------------------------------------------------+
```

- **Route:** `GET /files/{file_id}`.
- **Dữ liệu:** `files`, `file_shares`.
- **Quyền:** OWNER hoặc VIEWER; action buttons tùy permission.
- **Action log:** `VIEW_FILE`, `PERMISSION_DENIED`.

---

## 7. Thùng rác

```text
+------------------+-------------------------------------------+
| Sidebar          | THÙNG RÁC                                 |
|                  | Search [________]                          |
|                  +-------------------------------------------+
|                  | Tên tệp     Ngày xóa     Hành động        |
|                  | Old.pdf     10/06/2026   [Khôi phục] [...]|
|                  | Draft.docx  09/06/2026   [Khôi phục] [...]|
|                  +-------------------------------------------+
|                  | Xóa vĩnh viễn luôn yêu cầu xác nhận       |
+------------------+-------------------------------------------+
```

- **Route:** `GET /trash`.
- **Dữ liệu:** `files` với `is_deleted = true`.
- **Quyền:** OWNER.
- **Action log:** `VIEW_TRASH`, `RESTORE_FILE`, `PERMANENT_DELETE_FILE`.

---

## 8. Export

```text
+--------------------------------------------------------------+
| XUẤT DỮ LIỆU                                                 |
| Loại export: (o) CSV metadata  ( ) ZIP tệp                   |
| Chọn phạm vi: (o) Tệp đã chọn ( ) Theo bộ lọc                |
| Tệp đã chọn: 8                                               |
| Tổng dung lượng dự kiến: 14.2 MB                              |
|                                                              |
| [Hủy]                                  [Tạo yêu cầu export]  |
+--------------------------------------------------------------+

+--------------------------------------------------------------+
| LỊCH SỬ EXPORT                                               |
| Job ID | Loại | Số tệp | Trạng thái | Ngày tạo | Tải xuống  |
+--------------------------------------------------------------+
```

- **Route:** `GET /exports`, `POST /exports`, `GET /exports/{id}/download`.
- **Dữ liệu:** `export_jobs`, `export_job_items`.
- **Quyền:** Người tạo job.
- **Action log:** `CREATE_EXPORT_JOB`, `DOWNLOAD_EXPORT`.

---

## 9. Admin Logs

```text
+------------------+-------------------------------------------+
| Admin Sidebar    | REQUEST LOGS                              |
| - Tổng quan      | User [v] Action [v] Status [v] Date [__] |
| - Người dùng     | Keyword endpoint [_________] [Lọc]        |
| - Metadata tệp   +-------------------------------------------+
| - Logs           | Time | User | Action | Resource | Status  |
| - Alerts         | ...  | ...  | ...    | ...      | ...     |
|                  +-------------------------------------------+
|                  | [Export CSV theo bộ lọc]                  |
+------------------+-------------------------------------------+
```

- **Route:** `GET /admin/logs`.
- **Dữ liệu:** `request_logs`.
- **Quyền:** ADMIN.
- **Action log:** `ADMIN_VIEW_LOGS`, `ADMIN_EXPORT_LOGS`.

---

## 10. Admin Alerts

```text
+------------------+-------------------------------------------+
| Admin Sidebar    | CẢNH BÁO BẤT THƯỜNG                      |
|                  | User [v] Scenario [v] Status [v]          |
|                  +-------------------------------------------+
|                  | Time | User | Score | Hint | Status       |
|                  | ...  | ...  | 0.87  | BOLA | NEW          |
|                  +-------------------------------------------+
|                  | Alert detail:                              |
|                  | - Window                                  |
|                  | - Feature nổi bật                         |
|                  | - Log gốc liên quan                       |
+------------------+-------------------------------------------+
```

- **Route:** `GET /admin/alerts`, `GET /admin/alerts/{alert_id}`.
- **Dữ liệu:** `alerts`, `request_logs`.
- **Quyền:** ADMIN.
- **Action log:** `ADMIN_VIEW_ALERTS`, `UPDATE_ALERT`.

---

## 11. Quy tắc UI chung

- OWNER thấy đầy đủ action phù hợp.
- VIEWER chỉ thấy `Xem` và `Tải xuống`.
- NONE không được thấy dữ liệu tệp.
- Nút xóa, hủy chia sẻ và xóa vĩnh viễn phải có xác nhận.
- Form thay đổi dữ liệu phải có CSRF token.
- Màn hình rỗng phải có empty state và hướng dẫn hành động tiếp theo.
- Lỗi `403`, `404`, `413`, `500` có trang riêng hoặc thông báo rõ.
