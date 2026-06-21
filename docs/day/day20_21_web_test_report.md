# WEB TEST REPORT — StudyDrive Web v1

Ngày kiểm tra: 21/06/2026  
Mốc: Hoàn thiện UI, regression test và WEB FREEZE  
Phạm vi: Auth, My Drive, OWNER/VIEWER authorization, share, trash/restore, export CSV metadata, admin users/file/folder metadata.

## 1. Kết quả tự động

Lệnh chạy:

```bash
python -m pytest -q
```

Kết quả hiện tại:

```text
25 passed
```

## 2. Must-have checklist

| Nhóm | Ca kiểm thử | Kết quả | Ghi chú |
|---|---|---:|---|
| Auth/Role | User thường vào `/admin/users`, `/admin/files` | PASS | Trả 403 |
| OWNER | Upload/list/detail/download/rename/move/share | PASS | Đã có test trước đó |
| VIEWER | Xem/download file được share | PASS | Không thấy action OWNER |
| VIEWER | Thử rename/move/share file được share | PASS | Trả 404 thống nhất |
| Trash | OWNER soft delete file | PASS | File vào `/trash`, detail/download thường bị 404 |
| Trash | Restore file | PASS | File quay lại truy cập bình thường |
| Trash | File đã xóa không hiện ở shared-with-me | PASS | VIEWER mất quyền ngay |
| Export CSV | Export file đã chọn | PASS | Chỉ xuất file owner, active |
| Export CSV | CSV trái quyền/deleted | PASS | Không chứa file foreign/deleted |
| Export CSV | UTF-8 BOM + Content-Disposition | PASS | Excel/Pandas đọc được |
| Export Abuse prep | 10 export liên tiếp | PASS | Tạo 10 ExportJob |
| Admin | Dashboard/users search/pagination | PASS | Có route `/admin/users` |
| Admin | Khóa/mở user | PASS | Không cho tự khóa admin đang login |
| Admin | File metadata toàn hệ thống | PASS | Không có link download nội dung |
| Admin | Folder metadata toàn hệ thống | PASS | Có filter owner/deleted |
| Error pages | 403/404/413/500 custom | PASS cơ bản | Cần chụp ảnh minh họa thủ công |

## 3. Flow kiểm thử thủ công cần chụp ảnh

### OWNER flow

1. Login `user1`.
2. Tạo folder mới.
3. Upload file `.txt` hoặc `.pdf` hợp lệ.
4. Vào My Drive, search/filter/sort file vừa upload.
5. Mở chi tiết file, download thử.
6. Đổi tên giữ nguyên extension.
7. Di chuyển file sang folder khác.
8. Share cho `user3`.
9. Export CSV theo file đã chọn và export theo bộ lọc.
10. Delete file, kiểm tra file biến mất khỏi list/detail/download.
11. Vào Trash, restore file.

### VIEWER flow

1. Login `user3`.
2. Vào `Được chia sẻ với tôi`.
3. Mở file được share và download.
4. Thử truy cập `/files/<file_id>/rename` hoặc POST move/delete.
5. Kỳ vọng: không có nút OWNER; thao tác trái quyền trả 404/403 nhất quán.

### ADMIN flow

1. Login `admin`.
2. Mở `/admin/`.
3. Mở `/admin/users`, search user, khóa/mở user.
4. Mở `/admin/files`, filter owner/extension/deleted.
5. Mở `/admin/folders`, filter owner/deleted.
6. Đăng nhập user thường và thử vào route admin: phải bị 403.

## 4. Bug list sau mốc web-v1

| Mức | Lỗi | Trạng thái |
|---|---|---|
| Critical | Chưa ghi nhận | CLOSED |
| High | Chưa ghi nhận | CLOSED |
| Medium | Cần chụp ảnh responsive thủ công trên màn hình nhỏ | OPEN |
| Low | Có thể làm đẹp bảng admin sau web freeze | OPEN |

## 5. Kết luận WEB FREEZE

StudyDrive web v1 đạt scope tối thiểu tuần 2: folder/upload/list/detail/download/share/shared-with-me/trash/restore/export CSV và admin users/file/folder metadata. Từ sau mốc này chỉ sửa bug Critical/High để chuyển sang tuần 3: structured logging, simulator và dataset.
