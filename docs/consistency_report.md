# CONSISTENCY REPORT — 12/06/2026

## Kết luận

Bộ tài liệu đã được đồng bộ theo một phạm vi duy nhất:

```text
StudyDrive lưu tệp thật
→ Flask authorization OWNER/VIEWER/NONE
→ structured request logs
→ feature theo user/session/window
→ Isolation Forest
→ alert cho Export Abuse, Delete Abuse, IDOR/BOLA Scan
```

## Quyết định đã khóa

- Database: SQLite + SQLAlchemy.
- File database: `instance/app.db`.
- File vật lý: `instance/uploads/`.
- Không dùng `Document(title/content/category/status)`.
- Model tệp: `StoredFile`, bảng `files`.
- Không có register và forgot password.
- User bulk export tệp do mình sở hữu.
- CSV export là M0; ZIP là M1.
- Admin export request logs, không export nội dung file của User.
- Sharing, profile nâng cao, ZIP và permanent delete là M1.
- Simulator chỉ chạy local.

## File đã sửa

- `acceptance_criteria.md`
- `api_matrix.md`
- `architecture.md`
- `project_scope.md`
- `project_structure.md`
- `requirements.md`
- `web_security_notes.md`
- `wireframes.md`
- `use_cases.md` — bổ sung mới
