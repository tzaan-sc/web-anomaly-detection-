# Hướng dẫn ngày 15–16/06/2026: Folder, upload an toàn và My Files

## 1. Các file đã triển khai

- `app/blueprints/documents/forms.py`: `CreateFolderForm`, `UploadFileForm`.
- `app/blueprints/documents/routes.py`: `/files`, `/files/upload`, `/folders/create`, `/folders/<folder_id>`.
- `app/services/document_service.py`: kiểm tra folder owner, extension/MIME/chữ ký tệp, UUID, ghi file + metadata và rollback.
- `app/templates/documents/index.html`: breadcrumb, search, filter, sort, pagination, empty state.
- `app/templates/documents/create_folder.html`, `upload.html`: form có CSRF và hiển thị lỗi.
- `app/templates/errors/413.html`: lỗi file vượt giới hạn.
- `tests/test_documents.py`: test matrix của ngày 15–16/06.

## 2. Luồng tạo thư mục

1. User mở `GET /folders/create`.
2. Server chỉ đưa vào `parent_id` những folder `owner_id == current_user.id` và `is_deleted == false`.
3. Khi POST, route đọc lại `parent_id` từ request và truy vấn bằng cả `id` lẫn `owner_id`.
4. Nếu client tự sửa ID thành folder của user khác, server trả `404` và không tạo dữ liệu.
5. Service kiểm tra tên rỗng, `/`, `\\`, `.`, `..` và folder trùng tên trong cùng parent.
6. Chỉ commit sau khi toàn bộ kiểm tra hợp lệ.

## 3. Luồng upload an toàn

1. `MAX_CONTENT_LENGTH = 20 * 1024 * 1024` chặn request quá 20 MB và trả `413`.
2. `secure_filename()` chỉ tạo tên hiển thị an toàn; tên lưu vật lý không dùng tên client.
3. Extension phải thuộc `ALLOWED_EXTENSIONS`.
4. MIME type phải phù hợp với extension.
5. PDF, PNG, JPEG, ZIP và Office Open XML được kiểm tra chữ ký đầu file; TXT/CSV bị từ chối nếu có byte NUL.
6. Tên lưu được tạo bằng `uuid.uuid4().hex + extension`.
7. File nằm tại `instance/uploads/<user_id>/<uuid>.<ext>`, ngoài `static`.
8. Sau khi ghi file vật lý, metadata được commit vào bảng `files`.
9. Nếu commit DB lỗi, `rollback()` được gọi và file vừa ghi bị xóa bằng `unlink()`.

## 4. Luồng My Files

- `GET /files`: hiển thị toàn bộ file chưa xóa của user hiện tại và các folder gốc.
- `GET /folders/<folder_id>`: chỉ mở folder khi folder thuộc user hiện tại.
- Search: query parameter `q`, tìm trong `original_name`.
- Filter: `extension` và `folder`.
- Sort: `newest`, `oldest`, `name_asc`, `name_desc`, `size_asc`, `size_desc`.
- Pagination: 10 file/trang; URL trang tiếp theo giữ nguyên các query parameters.
- Breadcrumb được dựng từ quan hệ `parent` và có chống vòng lặp dữ liệu lỗi.

## 5. Chạy ứng dụng

```powershell
cd D:\web-anomaly-detection
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Mở:

- `http://127.0.0.1:5000/files`
- `http://127.0.0.1:5000/folders/create`
- `http://127.0.0.1:5000/files/upload`

## 6. Chạy test

```powershell
pytest -q
```

Kết quả mong đợi của source này:

```text
15 passed
```

Pytest dùng SQLite memory và thư mục upload tạm, không chạm database MySQL `studydrive` thật.

## 7. Test thủ công bắt buộc

### Tạo folder

- Login `user1` → tạo folder ở root → PASS.
- Tạo folder con trong folder của `user1` → PASS.
- Dùng DevTools sửa `parent_id` thành folder của `user2` → phải nhận `404`, không có folder mới.
- Tạo trùng tên trong cùng parent → form báo lỗi.

### Upload

- Upload TXT/PDF hợp lệ dưới 20 MB → DB có metadata và ổ đĩa có file UUID.
- Upload file trên 20 MB → `413`, không có metadata/file rác.
- Upload `.exe` → bị từ chối.
- Đổi tên file giả thành `.pdf` nhưng nội dung không có `%PDF-` → bị từ chối.
- Sửa `folder_id` thành folder user khác → `404`.
- Upload tên `../../bài tập 01.txt` → tên hiển thị được làm sạch, file vẫn nằm dưới `instance/uploads/<user_id>/`.

### Danh sách

- Search `bai-giang` kết hợp extension `txt` và sort kích thước → kết quả đúng.
- Chuyển sang trang 2 → URL vẫn giữ `q`, `extension`, `folder`, `sort`.
- Login user khác → không nhìn thấy file/folder riêng của user trước.
- Folder rỗng hoặc search không có kết quả → hiện empty state và nút upload.

## 8. Kiểm tra metadata khớp file vật lý

Chạy trong PowerShell:

```powershell
python -c "from pathlib import Path; from app import create_app; from app.extensions import db; from app.models import StoredFile; app=create_app(); ctx=app.app_context(); ctx.push(); rows=StoredFile.query.all(); print([(f.id, f.original_name, f.file_size, (Path(app.instance_path)/f.storage_path).exists()) for f in rows[-10:]]); ctx.pop()"
```

Mỗi file mới phải có:

- `stored_name` khác `original_name`.
- `stored_name` là UUID và không trùng.
- `file_size` bằng kích thước file vật lý.
- Đường dẫn vật lý tồn tại và nằm ngoài `app/static/`.
