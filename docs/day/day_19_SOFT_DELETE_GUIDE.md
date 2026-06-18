# StudyDrive — Soft delete, Trash, Restore

## Đã thêm/sửa file

1. `app/services/document_service.py`
   - `soft_delete_file()`
   - `restore_file()`
   - `permanently_delete_file()`
   - owner check riêng cho file trong trash.

2. `app/blueprints/documents/routes.py`
   - `POST/DELETE /files/<file_id>/delete`
   - `GET /trash`
   - `POST /files/<file_id>/restore`
   - `POST /files/<file_id>/permanent-delete`

3. `app/templates/documents/detail.html`
   - thêm nút `Xóa` cho OWNER.
   - thêm Bootstrap confirm modal trước khi đưa file vào thùng rác.

4. `app/templates/documents/trash.html`
   - trang thùng rác.
   - restore.
   - permanent delete có confirm modal và CSRF.

5. `app/templates/base.html`
   - thêm menu `Thùng rác` cho USER.

6. `app/templates/main/dashboard.html`
   - thêm quick action `Thùng rác`.

7. `tests/test_documents.py`
   - thêm test soft delete/trash/restore/viewer access.
   - thêm test repeated delete idempotent và permanent delete.

## Luồng test thủ công

### Test 1 — OWNER xóa mềm
1. Đăng nhập `user1`.
2. Vào `My Drive`.
3. Mở chi tiết một file.
4. Bấm `Xóa`.
5. Modal hiện ra, bấm `Đưa vào thùng rác`.
6. Kết quả đúng:
   - chuyển sang `/trash`.
   - file nằm trong thùng rác.
   - file không còn xuất hiện trong `My Drive`.
   - vào lại `/files/<file_id>` trả 404.
   - file vật lý chưa bị xóa.

### Test 2 — Restore
1. Đang ở `/trash`.
2. Bấm `Khôi phục`.
3. Kết quả đúng:
   - chuyển về chi tiết file.
   - file xuất hiện lại trong `My Drive`.
   - download được.
   - `deleted_at = NULL`, `is_deleted = false`.

### Test 3 — File được share
1. `user1` share file cho `user3`.
2. `user3` thấy file ở `Được chia sẻ với tôi`.
3. `user1` xóa mềm file.
4. `user3` kiểm tra lại.
5. Kết quả đúng:
   - `user3` không còn thấy file ở `/shared-with-me`.
   - `user3` vào `/files/<file_id>` bị 404.
   - `user3` không restore/delete được.

### Test 4 — Delete lặp
1. Gửi `POST /files/<file_id>/delete` hai lần bằng browser/test client.
2. Kết quả đúng:
   - request không làm hỏng dữ liệu.
   - file vẫn trong trash.
   - `deleted_at` không bị đổi ở lần thứ hai.

### Test 5 — Permanent delete
1. Vào `/trash`.
2. Bấm `Xóa vĩnh viễn`.
3. Confirm modal hiện ra.
4. Bấm `Xóa vĩnh viễn`.
5. Kết quả đúng:
   - metadata file bị xóa khỏi DB.
   - file vật lý bị xóa nếu còn tồn tại.
   - file không restore được nữa.

## Lệnh test tự động

Trong project của bạn trên Windows PowerShell:

```powershell
python -m pytest tests/test_documents.py -q
```

Hoặc chạy toàn bộ:

```powershell
python -m pytest -q
```

## Ghi chú quan trọng

- Route detail/download/share vẫn dùng `can_view_file()`/`can_modify_file()` nên file đã xóa bị ẩn khỏi luồng bình thường.
- Trash dùng owner-check riêng vì file đã xóa không được xem như `can_modify_file()` nữa.
- Soft delete không xóa file vật lý, phục vụ Delete Abuse simulator an toàn hơn.
- Permanent delete chỉ cho file đã nằm trong trash, có CSRF và modal xác nhận.
