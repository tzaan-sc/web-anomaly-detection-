# API MATRIX — ROUTE/API CỐT LÕI

## 1. Authentication

| Method | Route | Actor | Input | Success | Lỗi chính | Action log |
|---|---|---|---|---:|---|---|
| GET | `/login` | Public | — | 200 | — | `VIEW_LOGIN` tùy chọn |
| POST | `/login` | Public | username/email, password, csrf | 200/302 | 400, 401, 403 | `LOGIN_SUCCESS`, `LOGIN_FAILED` |
| POST | `/logout` | USER/ADMIN | csrf | 200/302 | 401 | `LOGOUT` |
| GET | `/api/auth/me` | USER/ADMIN | session | 200 | 401 | `VIEW_CURRENT_USER` |
| GET/POST | `/profile` | USER/ADMIN | profile fields | 200 | 400, 401 | `VIEW_PROFILE`, `UPDATE_PROFILE` |
| POST | `/change-password` | USER/ADMIN | old/new password, csrf | 200 | 400, 401, 403 | `CHANGE_PASSWORD` |

---

## 2. Dashboard

| Method | Route | Actor | Dữ liệu | Success | Lỗi | Action log |
|---|---|---|---|---:|---|---|
| GET | `/dashboard` | USER | files, folders, shares, logs | 200 | 401 | `VIEW_DASHBOARD` |
| GET | `/admin` | ADMIN | users, files, logs, alerts | 200 | 401, 403 | `ADMIN_VIEW_DASHBOARD` |

---

## 3. Folder

| Method | Route | Actor/Permission | Input | Success | Lỗi chính | Action log |
|---|---|---|---|---:|---|---|
| GET | `/folders/{folder_id}` | OWNER | folder_id | 200 | 403/404 | `VIEW_FOLDER`, `PERMISSION_DENIED` |
| POST | `/api/folders` | USER | name, parent_folder_id | 201 | 400, 403, 404, 409 | `CREATE_FOLDER` |
| PUT | `/api/folders/{folder_id}` | OWNER | name hoặc parent_id | 200 | 400, 403, 404, 409 | `UPDATE_FOLDER` |
| DELETE | `/api/folders/{folder_id}` | OWNER | folder_id | 204 | 403, 404, 409 | `DELETE_FOLDER` |

> Bản chính không có API chia sẻ folder.

---

## 4. File

| Method | Route | Actor/Permission | Input | Success | Lỗi chính | Action log |
|---|---|---|---|---:|---|---|
| GET | `/files` | USER | search, type, sort, page, folder_id | 200 | 400, 401 | `LIST_FILES` |
| GET | `/files/{file_id}` | OWNER/VIEWER | file_id | 200 | 403/404 | `VIEW_FILE`, `PERMISSION_DENIED` |
| POST | `/files/upload` | USER | multipart file, folder_id, csrf | 201/302 | 400, 403, 404, 413 | `UPLOAD_FILE`, `UPLOAD_REJECTED` |
| GET | `/files/{file_id}/download` | OWNER/VIEWER | file_id | 200 | 403/404 | `DOWNLOAD_FILE`, `PERMISSION_DENIED` |
| PUT | `/api/files/{file_id}` | OWNER | new_name hoặc folder_id | 200 | 400, 403, 404, 409 | `RENAME_FILE`, `MOVE_FILE` |
| DELETE | `/api/files/{file_id}` | OWNER | file_id, csrf | 204 | 403, 404 | `DELETE_FILE` |
| POST | `/api/files/{file_id}/restore` | OWNER | file_id, csrf | 200 | 403, 404, 409 | `RESTORE_FILE` |
| DELETE | `/api/files/{file_id}/permanent` | OWNER | file_id, csrf | 204 | 403, 404 | `PERMANENT_DELETE_FILE` |

---

## 5. Sharing

| Method | Route | Actor/Permission | Input | Success | Lỗi chính | Action log |
|---|---|---|---|---:|---|---|
| GET | `/shared-with-me` | USER | search, type, page | 200 | 401 | `VIEW_SHARED_FILES` |
| GET | `/api/files/{file_id}/shares` | OWNER | file_id | 200 | 403/404 | `VIEW_FILE_SHARES` |
| POST | `/api/files/{file_id}/shares` | OWNER | target_user/email, permission=VIEWER | 201 | 400, 403, 404, 409 | `SHARE_FILE` |
| DELETE | `/api/files/{file_id}/shares/{user_id}` | OWNER | file_id, user_id | 204 | 403, 404 | `REVOKE_SHARE` |

---

## 6. Trash

| Method | Route | Actor | Input | Success | Lỗi | Action log |
|---|---|---|---|---:|---|---|
| GET | `/trash` | USER | search, page | 200 | 401 | `VIEW_TRASH` |

Các thao tác restore/permanent delete dùng API file ở mục 4.

---

## 7. Export

| Method | Route | Actor/Permission | Input | Success | Lỗi chính | Action log |
|---|---|---|---|---:|---|---|
| GET | `/exports` | USER | page, status | 200 | 401 | `VIEW_EXPORT_HISTORY` |
| POST | `/api/exports` | USER | type, file_ids hoặc filter | 201 | 400, 403, 404 | `CREATE_EXPORT_JOB` |
| GET | `/api/exports/{export_job_id}` | Job owner | export_job_id | 200 | 403/404 | `VIEW_EXPORT_JOB` |
| GET | `/api/exports/{export_job_id}/download` | Job owner | export_job_id | 200 | 403/404, 409 | `DOWNLOAD_EXPORT` |

Quy tắc:

- `CSV`: metadata tệp user có quyền export.
- `ZIP`: chỉ chứa file user có quyền theo chính sách đã chốt.
- Không cho người khác tải job bằng cách đổi `export_job_id`.

---

## 8. Admin Users và Metadata

| Method | Route | Actor | Input | Success | Lỗi | Action log |
|---|---|---|---|---:|---|---|
| GET | `/admin/users` | ADMIN | search, status, page | 200 | 401, 403 | `ADMIN_VIEW_USERS` |
| GET | `/admin/users/{user_id}` | ADMIN | user_id | 200 | 403, 404 | `ADMIN_VIEW_USER` |
| POST | `/admin/users/{user_id}/lock` | ADMIN | csrf | 200 | 403, 404, 409 | `ADMIN_LOCK_USER` |
| POST | `/admin/users/{user_id}/unlock` | ADMIN | csrf | 200 | 403, 404, 409 | `ADMIN_UNLOCK_USER` |
| GET | `/admin/files` | ADMIN | owner, type, deleted, page | 200 | 401, 403 | `ADMIN_VIEW_FILE_METADATA` |

---

## 9. Admin Logs và Alerts

| Method | Route | Actor | Input | Success | Lỗi | Action log |
|---|---|---|---|---:|---|---|
| GET | `/admin/logs` | ADMIN | user, action, status, date, page | 200 | 401, 403 | `ADMIN_VIEW_LOGS` |
| GET | `/admin/logs/{log_id}` | ADMIN | log_id | 200 | 403, 404 | `ADMIN_VIEW_LOG_DETAIL` |
| GET | `/admin/logs/export` | ADMIN | current filters | 200 | 400, 403 | `ADMIN_EXPORT_LOGS` |
| POST | `/admin/detection/run` | ADMIN | time range/model version | 200/201 | 400, 403, 409 | `RUN_DETECTION` |
| GET | `/admin/alerts` | ADMIN | user, hint, status, page | 200 | 401, 403 | `ADMIN_VIEW_ALERTS` |
| GET | `/admin/alerts/{alert_id}` | ADMIN | alert_id | 200 | 403, 404 | `ADMIN_VIEW_ALERT_DETAIL` |
| POST | `/admin/alerts/{alert_id}/status` | ADMIN | NEW/REVIEWING/RESOLVED | 200 | 400, 403, 404 | `UPDATE_ALERT` |

---

## 10. Response body chuẩn cho API

### Thành công

```json
{
  "success": true,
  "data": {},
  "message": "Thao tác thành công"
}
```

### Lỗi

```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "Bạn không có quyền thực hiện thao tác này"
  }
}
```

Không trả:

- đường dẫn file vật lý;
- password hash;
- session token;
- thông tin của resource không thuộc quyền user.
