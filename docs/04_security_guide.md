# 04. HƯỚNG DẪN BẢO MẬT (SECURITY GUIDE)

## 1. Authentication vs Authorization
- **Authentication (Xác thực):** Trả lời câu hỏi "Bạn là ai?". Xác minh danh tính người dùng thông qua Email và Mật khẩu. Trạng thái đăng nhập được lưu trữ qua Session.
- **Authorization (Phân quyền):** Trả lời câu hỏi "Bạn được phép làm gì?". Kiểm tra xem User đã đăng nhập có quyền (`OWNER`, `VIEWER`) thao tác trên một tài nguyên cụ thể hay không.

## 2. Quản lý Phiên (Session & Cookie)
- **Session:** Dữ liệu lưu phía Server (hoặc được Server ký) để ghi nhớ trạng thái người dùng.
- **Cookie:** Browser dùng Cookie để lưu trữ Session ID.
- **Thuộc tính an toàn của Cookie:**
  - `HttpOnly`: Ngăn chặn JavaScript (XSS) đọc được cookie.
  - `Secure`: Cookie chỉ gửi qua giao thức HTTPS.
  - `SameSite (Lax/Strict)`: Hạn chế Cookie được gửi qua các request cross-site để chống CSRF.

## 3. Chống CSRF (Cross-Site Request Forgery)
- Mọi form thực hiện thay đổi dữ liệu (POST, PUT, DELETE) đều phải gắn `csrf_token`.
- Server từ chối request nếu thiếu hoặc sai token.

## 4. Ngăn chặn BOLA/IDOR (Broken Object Level Authorization)
**IDOR (Insecure Direct Object Reference) / BOLA** là lỗ hổng khi client truyền `resource_id` (VD: `file_id = 101`) lên server, nhưng server không kiểm tra xem user hiện tại có quyền đối với `resource_id` đó hay không.

**Cách xử lý chuẩn:**
Mọi request truy cập tài nguyên phải kiểm tra:
1. User đã đăng nhập chưa?
2. User có phải là `OWNER` hoặc có `VIEWER` share record hay không?
3. Nếu không có quyền: Trả về `403 Forbidden` hoặc `404 Not Found`. Tuyệt đối không trả về thông tin metadata hoặc nội dung file.

## 5. Dấu hiệu dò quét BOLA trong Logs
- Số lượng `unique_resource_id_count` cao.
- Tỷ lệ lỗi 403 và 404 cao trong một thời gian ngắn.
- `authorization_result = DENIED` liên tục.
- Dò quét tuần tự ID hoặc low-and-slow (giãn cách thời gian để tránh rate-limit).
