# Hướng dẫn kiểm tra ngày 17–18/06/2026

## 1. Phạm vi đã bổ sung

- `GET /files/<file_id>`: chi tiết metadata theo quyền OWNER/VIEWER.
- `GET /files/<file_id>/download`: tải bằng `file_id`; client không truyền đường dẫn vật lý.
- `GET /api/files/<file_id>`: API metadata cho simulator, không trả `stored_name` hoặc `storage_path`.
- `GET|POST /files/<file_id>/rename`: chỉ OWNER, chỉ đổi `original_name` và giữ nguyên extension.
- `GET|POST /files/<file_id>/move`: chỉ OWNER, chỉ chuyển vào folder của chính owner hoặc root.
- `GET|POST /files/<file_id>/share`: chỉ OWNER, permission cố định `VIEWER`.
- `POST /files/<file_id>/shares/<share_id>/revoke`: chỉ OWNER; revoke có hiệu lực ngay.
- `GET /shared-with-me`: chỉ hiện share còn hiệu lực và file chưa bị xóa.

Quy ước thống nhất: file không tồn tại, đã xóa hoặc user có quyền NONE đều trả **404**. API trả cùng JSON `{"error": "file_not_found"}` cho file không tồn tại và file trái quyền.

## 2. File code chính

- `app/services/document_service.py`
- `app/blueprints/documents/forms.py`
- `app/blueprints/documents/routes.py`
- `app/templates/documents/detail.html`
- `app/templates/documents/rename.html`
- `app/templates/documents/move.html`
- `app/templates/documents/share.html`
- `app/templates/documents/shared_with_me.html`
- `app/templates/documents/index.html`
- `app/templates/base.html`
- `tests/test_documents.py`

Không thay đổi schema database vì model hiện tại đã có đủ `FileShare.permission`, `shared_by_user_id` và `revoked_at`.

## 3. Chạy tự động

Trong PowerShell tại thư mục project:

```powershell
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
& .\.venv\Scripts\Activate.ps1
python -m pytest -q
```

Kết quả kiểm tra của bản này: **21 test PASS**.

## 4. Test thủ công OWNER

1. Chạy app:

```powershell
python run.py
```

2. Đăng nhập `user1` với mật khẩu demo trong README.
3. Vào **My Drive** → chọn **Chi tiết** một file.
4. Xác nhận có badge `OWNER` và các nút: Download, Đổi tên, Di chuyển, Chia sẻ.
5. Download file và xác nhận tên tải về là `original_name`.
6. Đổi tên `bai-giang-01.txt` thành `bai-giang-owner.txt`.
7. Kiểm tra database: `original_name` đổi nhưng `stored_name` và `storage_path` giữ nguyên.
8. Thử đổi thành `.pdf`: form phải từ chối vì extension không được đổi.
9. Di chuyển file sang một folder khác thuộc `user1`: phải thành công.
10. Sửa HTML/request để gửi `folder_id` thuộc user khác: phải nhận 404 và file không đổi folder.
11. Share file cho `user3`: phải tạo quyền `VIEWER`.
12. Share lại cùng user khi share còn hiệu lực: phải báo đã được chia sẻ và không tạo dòng trùng.

## 5. Test thủ công VIEWER

1. Đăng xuất OWNER, đăng nhập `user3`.
2. Vào **Được chia sẻ với tôi**.
3. File vừa share phải xuất hiện.
4. Mở chi tiết: có badge `VIEWER`, chỉ có xem và Download.
5. Sửa URL thủ công thành:

```text
/files/<file_id>/rename
/files/<file_id>/move
/files/<file_id>/share
```

Cả ba phải trả 404.

## 6. Test NONE và BOLA an toàn

1. Đăng nhập `user4`, là user không được share file vừa dùng.
2. Thử tuần tự:

```text
/files/<file_id>
/files/<file_id>/download
/api/files/<file_id>
/api/files/999999
```

3. Ba route với file thật nhưng trái quyền phải bị chặn.
4. Hai API cuối phải cùng status 404 và cùng body `{"error":"file_not_found"}`.
5. Không route nào trả `storage_path`, `stored_name` hoặc nội dung file user khác.
6. Các URL giữ `<file_id>` trong `view_args`, nên middleware logger ở tuần 3 có thể ghi `resource_id` mà không cần tạo lỗ hổng.

## 7. Test revoke có hiệu lực ngay

1. Đăng nhập lại OWNER.
2. Mở chi tiết file → tại danh sách đang chia sẻ, bấm **Thu hồi** user3.
3. Đăng nhập user3.
4. File phải biến mất khỏi **Được chia sẻ với tôi**.
5. Dùng lại URL chi tiết/download cũ: phải nhận 404 ngay.
6. OWNER share lại cho user3: hệ thống tái kích hoạt dòng share cũ, không vi phạm unique key và không tạo record trùng.

## 8. Test file vật lý bị thiếu

1. Tìm đường dẫn vật lý của một file OWNER bằng lệnh:

```powershell
python -c "from pathlib import Path; from app import create_app; from app.extensions import db; from app.models import StoredFile; app=create_app(); ctx=app.app_context(); ctx.push(); f=StoredFile.query.filter_by(is_deleted=False).first(); p=Path(f.storage_path); p=p if p.is_absolute() else Path(app.instance_path)/p; print('file_id=',f.id); print('path=',p); ctx.pop()"
```

2. Đổi tên tạm file vật lý, ví dụ thêm `.bak`.
3. Trang chi tiết metadata vẫn có thể mở cho OWNER.
4. Route Download phải trả 404, không crash và không cho client thay `?path=` để tải file khác.
5. Đổi file `.bak` về tên cũ sau khi test.

## 9. Điều kiện đánh dấu hoàn thành

### Ngày 17

- OWNER và VIEWER xem/download đúng quyền.
- NONE, file đã xóa và ID không tồn tại cùng bị 404.
- API không lộ đường dẫn lưu trữ.
- File vật lý thiếu làm download trả 404.
- Tất cả route nhạy cảm dùng `file_id` trên URL để logger ghi resource về sau.

### Ngày 18

- OWNER rename/move/share/revoke được.
- `stored_name` UUID không đổi khi rename.
- Folder user khác bị từ chối.
- Không self-share và không có share active trùng.
- VIEWER không modify được.
- Revoke làm mất quyền ngay và file biến mất khỏi `/shared-with-me`.
