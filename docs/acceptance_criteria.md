# ACCEPTANCE CRITERIA — CÁC MÀN HÌNH MUST-HAVE

## 1. Login

- [ ] Hiển thị form username/email, password và CSRF token.
- [ ] Đăng nhập đúng tạo session và redirect đúng role.
- [ ] Sai mật khẩu hiển thị lỗi chung, không tiết lộ tài khoản có tồn tại.
- [ ] User bị khóa không đăng nhập được.
- [ ] Cookie session cấu hình `HttpOnly`, `SameSite`.
- [ ] Có log `LOGIN_SUCCESS` hoặc `LOGIN_FAILED`.
- [ ] Logout làm route bảo vệ không truy cập lại được.

---

## 2. Dashboard User

- [ ] Chỉ truy cập được khi đã đăng nhập.
- [ ] Hiển thị số tệp thuộc sở hữu, thư mục, tệp được chia sẻ và tệp đã xóa.
- [ ] Không tính dữ liệu của user khác vào thống kê cá nhân.
- [ ] Có link đến Tệp của tôi, Upload, Shared with me và Trash.
- [ ] Có log `VIEW_DASHBOARD`.
- [ ] Trạng thái rỗng hiển thị đúng khi user chưa có tệp.

---

## 3. Tệp của tôi

- [ ] Danh sách chỉ hiển thị file/folder thuộc user hiện tại.
- [ ] Hỗ trợ search, filter loại file, sort và pagination.
- [ ] Query parameters được giữ khi chuyển trang.
- [ ] File đã xóa không xuất hiện trong danh sách thông thường.
- [ ] OWNER thấy các action hợp lệ.
- [ ] User A không thấy file riêng của User B.
- [ ] Có log `LIST_FILES` và `VIEW_FOLDER`.

---

## 4. Upload

- [ ] Cho phép upload vào root hoặc folder thuộc user.
- [ ] Từ chối folder đích không thuộc user.
- [ ] Giới hạn 20 MB/tệp.
- [ ] Chỉ chấp nhận extension và MIME type đã cho phép.
- [ ] Tên file vật lý được tạo bằng UUID.
- [ ] Tên hiển thị được sanitize.
- [ ] Không lưu file trong thư mục public/static.
- [ ] Upload thành công tạo metadata và file vật lý tương ứng.
- [ ] Upload thất bại không để metadata/file rác.
- [ ] Có log `UPLOAD_FILE` hoặc `UPLOAD_REJECTED`.

---

## 5. Chi tiết và Download tệp

- [ ] OWNER xem metadata và có đầy đủ action.
- [ ] VIEWER xem metadata và chỉ có action xem/tải.
- [ ] NONE nhận `403` hoặc `404` theo quy ước.
- [ ] Request trái quyền không trả original name, owner hoặc đường dẫn vật lý.
- [ ] Download đi qua route authorization, không truy cập file trực tiếp.
- [ ] File không tồn tại trả `404`.
- [ ] Có log `VIEW_FILE`, `DOWNLOAD_FILE` hoặc `PERMISSION_DENIED`.
- [ ] `file_id` được ghi đúng trong log.

---

## 6. Shared with me

- [ ] Chỉ hiển thị file có bản ghi share hợp lệ với user hiện tại.
- [ ] Permission hiển thị là `VIEWER`.
- [ ] Không hiển thị folder của owner.
- [ ] File bị hủy chia sẻ biến mất khỏi danh sách.
- [ ] File bị owner xóa mềm không còn tải được.
- [ ] Viewer không thấy nút đổi tên, di chuyển, chia sẻ hoặc xóa.
- [ ] Có log `VIEW_SHARED_FILES`.

---

## 7. Chia sẻ tệp

- [ ] Chỉ OWNER được mở danh sách share.
- [ ] Chỉ chia sẻ file, không có chức năng chia sẻ folder.
- [ ] Permission duy nhất trong bản chính là `VIEWER`.
- [ ] Không thể chia sẻ cho chính owner.
- [ ] Không tạo bản ghi trùng.
- [ ] Hủy chia sẻ làm user đích mất quyền ngay.
- [ ] Viewer cố chia sẻ tiếp nhận `403/404`.
- [ ] Có log `SHARE_FILE`, `REVOKE_SHARE` hoặc `PERMISSION_DENIED`.

---

## 8. Trash

- [ ] Chỉ hiển thị file đã xóa thuộc owner hiện tại.
- [ ] Delete là soft delete và không xóa file vật lý ngay.
- [ ] Restore đưa file trở lại danh sách thông thường.
- [ ] Permanent delete yêu cầu xác nhận và CSRF.
- [ ] Viewer không thể xóa hoặc khôi phục file.
- [ ] Delete lặp lại không gây trạng thái sai.
- [ ] Có log `DELETE_FILE`, `RESTORE_FILE`, `PERMANENT_DELETE_FILE`.

---

## 9. Export

- [ ] User chọn được CSV hoặc ZIP.
- [ ] Mỗi lần export tạo `export_job_id`.
- [ ] Job lưu user tạo, loại, số tệp, tổng dung lượng, trạng thái và thời gian.
- [ ] Chỉ file hợp lệ theo quyền mới được đưa vào job.
- [ ] User không tải được export job của người khác.
- [ ] Job chưa `COMPLETED` không tải được.
- [ ] CSV mở được bằng Pandas/Excel.
- [ ] ZIP không chứa file ngoài quyền.
- [ ] Có log `CREATE_EXPORT_JOB` và `DOWNLOAD_EXPORT`.
- [ ] Log có `export_job_id`, `export_item_count`, `export_total_size`.

---

## 10. Admin Logs

- [ ] Chỉ ADMIN truy cập được.
- [ ] Lọc theo user, thời gian, action, status, endpoint.
- [ ] Có pagination và giữ filter khi chuyển trang.
- [ ] Xem được chi tiết request, session hash, resource và authorization result.
- [ ] Không hiển thị password, cookie, token thô hoặc nội dung file.
- [ ] Export CSV theo đúng bộ lọc hiện tại.
- [ ] Có thể tìm được chuỗi request nhiều `file_id` và 403/404.
- [ ] User thường truy cập route admin nhận `403`.

---

## 11. Admin Alerts

- [ ] Chỉ ADMIN truy cập được.
- [ ] Hiển thị time, user, anomaly score, scenario hint và trạng thái.
- [ ] Alert detail hiển thị feature nổi bật.
- [ ] Alert truy ngược được về window và log gốc.
- [ ] Có filter theo user, hint, status và model version.
- [ ] Cập nhật được `NEW`, `REVIEWING`, `RESOLVED`.
- [ ] Chạy detection lại không tạo duplicate theo `window_id + model_version`.
- [ ] Không trình bày scenario hint như nhãn chắc chắn tuyệt đối.

---

## 12. Kiểm tra ánh xạ màn hình

| Màn hình | Route chính | Bảng dữ liệu | Permission | Action log |
|---|---|---|---|---|
| Login | `/login` | users, session | Public | LOGIN_SUCCESS/FAILED |
| Dashboard | `/dashboard` | files, folders, shares, logs | USER | VIEW_DASHBOARD |
| Tệp của tôi | `/files` | files, folders | OWNER | LIST_FILES |
| Upload | `/files/upload` | files, folders | USER/OWNER folder | UPLOAD_FILE |
| Shared with me | `/shared-with-me` | file_shares, files | VIEWER | VIEW_SHARED_FILES |
| Chi tiết tệp | `/files/{file_id}` | files, file_shares | OWNER/VIEWER | VIEW_FILE |
| Trash | `/trash` | files | OWNER | VIEW_TRASH |
| Export | `/exports` | export_jobs, items | Job owner | CREATE_EXPORT_JOB |
| Admin Logs | `/admin/logs` | request_logs | ADMIN | ADMIN_VIEW_LOGS |
| Admin Alerts | `/admin/alerts` | alerts, request_logs | ADMIN | ADMIN_VIEW_ALERTS |

---

## 13. Điều kiện hoàn thành ngày 10/06/2026

- [ ] Use case User/Admin đã chốt.
- [ ] Ma trận OWNER/VIEWER/ADMIN không mâu thuẫn.
- [ ] Wireframe đủ các màn hình Must-have.
- [ ] Architecture thể hiện authorization trước business response và logger.
- [ ] API matrix có method, route, quyền, status code và action log.
- [ ] Giới hạn file và quy tắc UUID đã chốt.
- [ ] Mỗi màn hình ánh xạ được route, dữ liệu, permission và action log.
