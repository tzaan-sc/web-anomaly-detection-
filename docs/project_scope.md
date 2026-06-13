# PROJECT SCOPE

## 1. Thông tin đề tài

**Tên đề tài:**  
**Xây dựng hệ thống phát hiện hành vi truy cập bất thường trên ứng dụng web bằng Machine Learning**

**Ứng dụng nghiệp vụ:**  
**Hệ thống lưu trữ và chia sẻ tài liệu trực tuyến với hai vai trò User và Admin.**

**Thời gian thực hiện:** 08/06/2026 – 19/07/2026

**Trạng thái hiện tại:** Đã hoàn thành phần thiết kế và setup Flask đến hết ngày 11/06/2026; ngày 12/06/2026 bắt đầu models, seed và reset demo.

---

## 2. Mô tả vấn đề

Các cuộc tấn công web có dấu hiệu rõ ràng như gửi quá nhiều request trong thời gian ngắn thường có thể được phát hiện bằng rule-based, rate limiting, firewall hoặc WAF. Tuy nhiên, một số hành vi nguy hiểm vẫn sử dụng tài khoản và phiên đăng nhập hợp lệ, không vượt qua các ngưỡng cố định nên khó phát hiện chỉ bằng luật. Ví dụ, một người dùng thường chỉ xem hoặc tải một vài tệp nhưng đột ngột tạo nhiều yêu cầu export, xóa liên tiếp nhiều tệp hoặc thay đổi tuần tự `file_id` để dò tài nguyên không thuộc quyền truy cập. Vì vậy, đề tài xây dựng một ứng dụng lưu trữ và chia sẻ tài liệu trực tuyến làm môi trường phát sinh hành vi, đồng thời thu thập structured log theo người dùng, phiên đăng nhập, tài nguyên và kết quả phân quyền. Dữ liệu log được chuyển thành các đặc trưng hành vi theo cửa sổ thời gian và sử dụng mô hình Isolation Forest để nhận diện các phiên hoạt động lệch khỏi hành vi bình thường. Machine Learning chỉ hỗ trợ phát hiện và cảnh báo; cơ chế authorization của ứng dụng vẫn phải chặn mọi request trái quyền.

---

## 3. Mục tiêu đề tài

Xây dựng một hệ thống lưu trữ và chia sẻ tài liệu trực tuyến có khả năng:

1. Cho phép người dùng đăng nhập, đăng xuất và quản lý phiên làm việc.
2. Phân quyền hệ thống theo hai vai trò `USER` và `ADMIN`.
3. Cho phép User tạo thư mục, upload, xem, tải xuống, đổi tên, di chuyển, tìm kiếm, lọc, phân trang, export, xóa và khôi phục tệp thuộc quyền quản lý.
4. Cho phép chủ sở hữu chia sẻ từng tệp cho người dùng khác với quyền `VIEWER`; không chia sẻ thư mục trong phiên bản chính.
5. Kiểm tra quyền truy cập ở cấp đối tượng dựa trên chủ sở hữu và bản ghi chia sẻ.
6. Cho phép Admin quản lý người dùng, metadata tệp, request log và cảnh báo bất thường.
7. Thu thập structured log về hành vi truy cập, kết quả phân quyền và tài nguyên liên quan.
8. Cho phép Admin tìm kiếm, lọc, xem chi tiết và export log.
9. Chuyển log thành các đặc trưng phục vụ Machine Learning.
10. Huấn luyện Isolation Forest chủ yếu trên dữ liệu hành vi bình thường.
11. Phát hiện ba scenario: Export Abuse, Delete Abuse và IDOR/BOLA Scan.
12. Hiển thị anomaly score, scenario nghi ngờ, feature nổi bật và log liên quan.
13. Đánh giá mô hình trên dữ liệu kiểm thử có ground truth.

### 3.1. Định nghĩa “web hoàn chỉnh” trong phạm vi đồ án

Trong đề tài này, “web hoàn chỉnh” không có nghĩa là hệ thống lưu trữ thương mại quy mô lớn. Web được xem là hoàn chỉnh khi:

* Có giao diện để người dùng thao tác, không chỉ gồm một số API dùng để sinh log.
* Có MySQL database, dữ liệu mẫu, đăng nhập, session và phân quyền.
* Có luồng quản lý tệp thực tế từ upload đến download, chia sẻ, export, xóa và khôi phục.
* Có cấu trúc thư mục, tìm kiếm, lọc, phân trang và xử lý lỗi.
* Có trang quản trị người dùng, metadata tệp, log và cảnh báo.
* Có thể kiểm thử và demo theo một luồng nghiệp vụ hoàn chỉnh.
* Không trộn lẫn “tài liệu dạng bản ghi có nội dung” với “tệp được lưu trên hệ thống”.

---

## 4. Phạm vi người dùng và phân quyền

### 4.1. Vai trò hệ thống

#### User

User sử dụng các chức năng lưu trữ, quản lý và chia sẻ tệp trong phạm vi được cấp quyền.

#### Admin

Admin quản lý tài khoản, metadata tài nguyên, request log, quá trình detection và cảnh báo. Admin không được xem password, cookie, session token nguyên bản hoặc tự động đọc nội dung tệp riêng tư nếu không thuộc luồng nghiệp vụ được cho phép.

### 4.2. Quyền trên tệp

| Quyền | Ý nghĩa | Thao tác được phép |
| --- | --- | --- |
| `OWNER` | Chủ sở hữu tệp | Xem, download, đổi tên, di chuyển, chia sẻ, hủy chia sẻ, export, xóa và khôi phục |
| `VIEWER` | Người được chia sẻ | Xem metadata và download tệp |
| `NONE` | Không có quyền | Request phải bị từ chối bằng 403 hoặc 404 theo quy ước của hệ thống |

### 4.3. Giới hạn chia sẻ

* Chỉ chia sẻ từng tệp trong phiên bản chính.
* Không chia sẻ thư mục.
* Không chia sẻ bằng liên kết công khai.
* Không cho `VIEWER` chia sẻ tiếp, đổi tên, di chuyển, export hàng loạt hoặc xóa tệp.
* Một cặp `file_id` và `shared_with_user_id` chỉ có một bản ghi chia sẻ đang hiệu lực.

### 4.5. Quy tắc export

* Mỗi lần export tạo một `ExportJob`.
* CSV metadata là M0 và có thể hoàn thành đồng bộ.
* ZIP là M1, chỉ làm sau khi M0 ổn định.
* Bulk export chỉ gồm tệp do user sở hữu; `VIEWER` chỉ được download từng tệp được chia sẻ.
* User chỉ xem và tải export job do chính mình tạo.

---

### 4.4. Nguyên tắc authorization

Mỗi request truy cập tệp phải kiểm tra ít nhất một trong hai điều kiện:

```text
current_user.id == file.owner_id
HOẶC
current_user có bản ghi chia sẻ hợp lệ với file và permission == VIEWER
```

Đối với thao tác thay đổi dữ liệu như rename, move, share, delete, restore và export tệp riêng lẻ, người dùng phải là `OWNER`, trừ khi đặc tả chức năng ghi rõ khác.

Machine Learning không thay thế cơ chế phân quyền. Dù mô hình chưa phát hiện bất thường, request không đủ quyền vẫn phải bị chặn.

---

## 5. Phân mức chức năng M0/M1/M2

### 5.1. M0 — Bắt buộc để hệ thống chạy và thu thập dữ liệu

| Mã | Chức năng | Phục vụ scenario |
| --- | --- | --- |
| M0-01 | Đăng nhập, đăng xuất, session, khóa tài khoản | Cả ba |
| M0-02 | Phân quyền User/Admin | Cả ba |
| M0-03 | Tạo thư mục cá nhân | BOLA qua `folder_id` |
| M0-04 | Upload tệp thật và lưu metadata | Cả ba |
| M0-05 | Danh sách, chi tiết và download tệp | BOLA |
| M0-06 | Kiểm tra `OWNER/VIEWER/NONE` ở cấp đối tượng | BOLA |
| M0-07 | Xóa mềm, thùng rác và khôi phục tệp | Delete Abuse |
| M0-08 | Tạo export job CSV metadata thuộc tệp do user sở hữu | Export Abuse |
| M0-09 | Structured request logging | Cả ba |
| M0-10 | Trang Admin xem, lọc và export log | Cả ba |
| M0-11 | Script sinh normal và ba scenario bất thường | Cả ba |
| M0-12 | Feature engineering, Isolation Forest và alert cơ bản | Cả ba |

### 5.2. M1 — Cần có để web sử dụng tốt và scenario rõ hơn

| Mã | Chức năng | Phục vụ scenario |
| --- | --- | --- |
| M1-01 | Dashboard User | Hỗ trợ demo |
| M1-02 | Search, filter, sort và pagination | Normal behavior |
| M1-03 | Đổi tên và di chuyển tệp giữa các thư mục | Normal behavior/BOLA |
| M1-04 | Chia sẻ tệp với quyền `VIEWER` | BOLA theo permission |
| M1-05 | Danh sách “Được chia sẻ với tôi” | BOLA theo permission |
| M1-06 | Export nhiều tệp thành ZIP bằng `export_job` | Export Abuse |
| M1-07 | Profile và đổi mật khẩu | Hoàn thiện web |
| M1-08 | Admin quản lý user và metadata tệp | Quản trị |
| M1-09 | Dashboard alert và liên kết log gốc | Cả ba |

### 5.3. M2 — Mở rộng, chỉ làm khi M0 và M1 đã ổn định

| Mã | Chức năng | Ghi chú |
| --- | --- | --- |
| M2-01 | Biểu đồ thống kê nâng cao | Không bắt buộc |
| M2-02 | Xem trước PDF/hình ảnh | Không phục vụ trực tiếp ML |
| M2-03 | Kéo thả upload và di chuyển | Chỉ cải thiện UX |
| M2-04 | Lịch sử hoạt động cá nhân chi tiết | Có thể dùng lại log |
| M2-05 | Email hoặc thông báo mời chia sẻ | Ngoài phạm vi chính |
| M2-06 | Nhiều mức quyền như `EDITOR` | Chưa cần trong phiên bản chính |

---

## 6. Sản phẩm cuối cùng

### 6.1. Ứng dụng lưu trữ và chia sẻ tài liệu trực tuyến

Ứng dụng được xây dựng bằng Python Flask, HTML, CSS, Jinja2 và Bootstrap. Tệp được lưu trong thư mục upload cục bộ; database lưu metadata và quan hệ quyền.

#### Chức năng User

* Đăng nhập và đăng xuất.
* Xem dashboard cá nhân.
* Tạo và quản lý thư mục cá nhân.
* Upload tệp.
* Xem danh sách và metadata tệp.
* Download tệp thuộc sở hữu hoặc được chia sẻ.
* Đổi tên và di chuyển tệp thuộc sở hữu.
* Tìm kiếm, lọc, sắp xếp và phân trang.
* Chia sẻ hoặc hủy chia sẻ từng tệp với quyền `VIEWER`.
* Xem danh sách tệp được chia sẻ với mình.
* Tạo export job CSV metadata cho các tệp do mình sở hữu.
* Tạo export ZIP từ các tệp do mình sở hữu khi chức năng M1-06 được triển khai.
* Xóa mềm, xem thùng rác, khôi phục và xóa vĩnh viễn sau xác nhận.
* Xem profile và đổi mật khẩu.

#### Chức năng Admin

* Xem dashboard quản trị.
* Tìm kiếm, khóa hoặc mở tài khoản người dùng.
* Xem và lọc metadata tệp trong toàn hệ thống.
* Xem, tìm kiếm, lọc, phân trang và export request log.
* Chạy detection theo khoảng thời gian hoặc tập log chưa xử lý.
* Xem chi tiết cảnh báo, feature nổi bật và log liên quan.
* Cập nhật trạng thái cảnh báo: `NEW`, `REVIEWING`, `RESOLVED`.

### 6.2. Bảng chức năng và tiêu chí hoàn thành

| Mã | Chức năng | Actor | Đầu vào | Kết quả | Tiêu chí hoàn thành |
| --- | --- | --- | --- | --- | --- |
| U01 | Đăng nhập/đăng xuất | User/Admin | Username, password, session | Tạo hoặc xóa session | Login đúng; sai thông tin báo lỗi; logout chặn route bảo vệ |
| U02 | Dashboard cá nhân | User | User hiện tại | Thống kê tệp/thư mục | Chỉ hiển thị dữ liệu của user hiện tại |
| U03 | Quản lý thư mục | User | Tên thư mục, parent folder | Tạo/xem/đổi tên/xóa thư mục rỗng | Không thao tác thư mục user khác |
| U04 | Upload tệp | User | File, thư mục đích | File lưu trên disk và metadata lưu DB | Chặn tên/loại/kích thước không hợp lệ; không ghi đè ngoài ý muốn |
| U05 | Danh sách/chi tiết/download | User | Bộ lọc hoặc `file_id` | Metadata hoặc file tải xuống | Chỉ `OWNER/VIEWER` truy cập được |
| U06 | Đổi tên/di chuyển tệp | User | `file_id`, tên mới, `folder_id` | Metadata được cập nhật | Chỉ `OWNER`; folder đích phải thuộc user |
| U07 | Search/filter/pagination | User | Từ khóa, loại tệp, thời gian, trang | Danh sách phù hợp | Giữ query khi chuyển trang; không lộ tệp trái quyền |
| U08 | Chia sẻ/hủy chia sẻ tệp | User | `file_id`, user nhận | Tạo/xóa `file_share` | Chỉ `OWNER`; không chia sẻ folder |
| U09 | Tệp được chia sẻ | User | User hiện tại | Danh sách tệp có quyền `VIEWER` | Không cho sửa/xóa/chia sẻ tiếp |
| U10 | Export | User | Loại export, bộ lọc hoặc danh sách `file_id` thuộc sở hữu | `export_job`; CSV là M0, ZIP là M1 | Không bulk export tệp chỉ có quyền VIEWER; ghi đủ log |
| U11 | Trash/restore/permanent delete | User | `file_id` | Thay đổi trạng thái hoặc xóa vật lý | Chỉ `OWNER`; có xác nhận; thao tác idempotent hợp lý |
| U12 | Profile/đổi mật khẩu | User | Profile, mật khẩu cũ/mới | Cập nhật tài khoản | Password hash, không lưu plaintext |
| A01 | Quản lý user | Admin | User ID, trạng thái | Danh sách/khóa/mở | User bị khóa không đăng nhập được |
| A02 | Quản lý metadata tệp | Admin | Owner, loại, trạng thái | Danh sách metadata | Có filter/pagination; không lộ secret |
| A03 | Quản lý log | Admin | Bộ lọc log | Danh sách/chi tiết/export | Không hiển thị password, cookie, token nguyên bản |
| A04 | Chạy detection | Admin | Khoảng thời gian/log chưa xử lý | Score và prediction | Không tạo alert trùng theo window/model |
| A05 | Quản lý alert | Admin | Alert ID, trạng thái | Chi tiết/cập nhật trạng thái | Truy ngược được feature và log gốc |

---

## 7. Mô hình dữ liệu tối thiểu

### 7.1. Các bảng chính

```text
users
folders
files
file_shares
export_jobs
export_job_items
request_logs
alerts
```

### 7.2. Trường chính dự kiến

#### `users`

```text
id
username
email
password_hash
role
is_active
created_at
updated_at
```

#### `folders`

```text
id
name
owner_id
parent_id
is_deleted
created_at
updated_at
```

#### `files`

```text
id
original_name
stored_name
storage_path
mime_type
file_extension
file_size
owner_id
folder_id
is_deleted
deleted_at
created_at
updated_at
```

#### `file_shares`

```text
id
file_id
shared_with_user_id
permission
shared_by_user_id
created_at
revoked_at
```

#### `export_jobs`

```text
id
requested_by_user_id
export_type
item_count
total_size
status
output_path
created_at
completed_at
```

#### `export_job_items`

```text
id
export_job_id
file_id
created_at
```

#### `request_logs`

Lưu thông tin request, tài nguyên, permission, kết quả authorization và response.

#### `alerts`

Lưu window, model version, anomaly score, scenario hint, feature nổi bật và trạng thái xử lý.

---

## 8. Hệ thống thu thập structured log

Mỗi request quan trọng cần ghi lại ít nhất các trường:

| Trường | Ý nghĩa |
| --- | --- |
| `request_id` | Mã duy nhất của request |
| `timestamp` | Thời điểm request |
| `user_id` | Người dùng gửi request |
| `role` | Vai trò hệ thống của user |
| `session_id_hash` | Giá trị nhận diện phiên đã hash/rút gọn |
| `ip_address` | Địa chỉ IP |
| `user_agent` | Trình duyệt hoặc client |
| `http_method` | GET, POST, PUT/PATCH, DELETE |
| `endpoint` | Endpoint được truy cập |
| `action` | login, list, upload, view, download, share, export, delete, restore... |
| `resource_type` | file, folder, export_job, user hoặc none |
| `resource_id` | ID tài nguyên được yêu cầu |
| `owner_id` | Chủ sở hữu tài nguyên nếu xác định được |
| `permission` | OWNER, VIEWER hoặc NONE |
| `authorization_result` | ALLOWED hoặc DENIED |
| `status_code` | Mã phản hồi HTTP |
| `response_time_ms` | Thời gian xử lý request |
| `file_size` | Kích thước tệp liên quan nếu có |
| `export_item_count` | Số tệp trong export job nếu có |
| `export_total_size` | Tổng dung lượng export nếu có |

Trang quản lý log dành cho Admin phải hỗ trợ:

* Xem danh sách và chi tiết log.
* Tìm kiếm/lọc theo user, thời gian, method, endpoint, action, resource type, permission, authorization result và status code.
* Phân trang và sắp xếp theo thời gian.
* Export log thành CSV.
* Truy ngược từ alert về các log thuộc cùng cửa sổ hành vi.

Không được ghi password, nội dung form đăng nhập, cookie, CSRF token, session token nguyên bản hoặc nội dung tệp vào log.

---

## 9. Ba scenario bắt buộc

### 9.1. Scenario 1 — Export Abuse

#### Hành vi bình thường

Người dùng chủ yếu xem, tải một số tệp và chỉ thỉnh thoảng export danh sách tệp hoặc tạo một `export_job` nhỏ.

#### Hành vi bất thường

Người dùng đột ngột:

* Gửi nhiều request tạo export trong một cửa sổ thời gian ngắn.
* Tạo nhiều `export_job` liên tiếp.
* Export số lượng tệp hoặc tổng dung lượng lớn hơn đáng kể so với lịch sử.
* Export nhiều tệp ngay sau khi đăng nhập.
* Chuyển từ hành vi chỉ xem/download sang export liên tục.
* Cố đưa các `file_id` không thuộc quyền vào export job.

#### Tài nguyên liên quan

* `file_id`
* `folder_id` dùng để xác định phạm vi lọc hoặc vị trí tệp
* `export_job_id`
* `permission`

#### Dữ liệu cần quan sát

* `export_count`
* `export_ratio`
* `unique_export_job_count`
* `export_item_count`
* `export_total_size`
* `time_to_first_export_sec`
* Số `file_id` khác nhau được yêu cầu export
* Tỷ lệ export bị từ chối do permission

#### Kết quả mong đợi

Phiên hoạt động có anomaly score cao và được gợi ý là Export Abuse; alert liên kết được tới `export_job` và các request liên quan.

---

### 9.2. Scenario 2 — Delete Abuse

#### Hành vi bình thường

Người dùng hiếm khi xóa tệp và thường chỉ xóa một số ít tệp thuộc sở hữu của mình.

#### Hành vi bất thường

Người dùng đột ngột:

* Gửi nhiều request xóa trong một phiên.
* Xóa liên tiếp nhiều `file_id` hoặc nhiều tệp trong các `folder_id` khác nhau.
* Xóa ngay sau khi đăng nhập.
* Có tỷ lệ request delete cao bất thường so với lịch sử.
* Cố xóa tệp chỉ có quyền `VIEWER` hoặc không có quyền.
* Xóa rồi xóa vĩnh viễn nhiều tệp trong thời gian ngắn.

#### Tài nguyên liên quan

* `file_id`
* `folder_id`
* `permission`

#### Dữ liệu cần quan sát

* `delete_count`
* `delete_ratio`
* `unique_deleted_file_count`
* `unique_affected_folder_count`
* `avg_inter_delete_sec`
* `time_to_first_delete_sec`
* Tỷ lệ request delete có permission khác `OWNER`
* Tỷ lệ status 403/404 trong nhóm delete

#### Kết quả mong đợi

Hệ thống phát hiện sự thay đổi hành vi và gợi ý Delete Abuse; alert truy ngược được các `file_id`, `folder_id` và log xóa liên quan.

---

### 9.3. Scenario 3 — IDOR/BOLA Scan

#### Hành vi bình thường

Người dùng chỉ truy cập `file_id`, `folder_id` và `export_job_id` thuộc sở hữu hoặc được cấp quyền hợp lệ.

#### Hành vi bất thường

Người dùng hoặc script:

* Thay đổi liên tiếp `file_id`, `folder_id` hoặc `export_job_id`.
* Thử nhiều ID gần nhau hoặc có tính tuần tự.
* Truy cập nhiều tài nguyên có permission `NONE`.
* Cố thao tác thay đổi dữ liệu trên tệp chỉ có quyền `VIEWER`.
* Gửi request tốc độ thấp để tránh rate limiting.
* Nhận nhiều phản hồi 403 hoặc 404.

#### Tài nguyên liên quan

* `file_id`
* `folder_id`
* `export_job_id`
* `permission`
* `authorization_result`

#### Dữ liệu cần quan sát

* `unique_resource_id_count`
* `unique_failed_resource_id_count`
* `resource_id_change_rate`
* `permission_none_rate`
* `authorization_denied_rate`
* `forbidden_rate`
* `not_found_rate`
* Mức độ tuần tự của ID
* Số loại tài nguyên bị dò trong cùng phiên

#### Kết quả mong đợi

Hệ thống đánh dấu phiên có dấu hiệu IDOR/BOLA Scan kể cả khi request không vượt ngưỡng rate limiting. Ứng dụng vẫn phải chặn request trái quyền và không làm lộ metadata hoặc nội dung tệp.

---

## 10. Phạm vi thực hiện

### 10.1. Phạm vi bắt buộc

* Web lưu trữ và chia sẻ tài liệu trực tuyến bằng Python Flask.
* Giao diện HTML, CSS, Jinja2 và Bootstrap.
* Hai vai trò User và Admin.
* Đăng nhập, đăng xuất, session và phân quyền.
* Quyền tệp `OWNER/VIEWER`.
* Tạo thư mục cá nhân.
* Upload, danh sách, chi tiết, download, đổi tên và di chuyển tệp.
* Search, filter, sort và pagination.
* Chia sẻ từng tệp; không chia sẻ folder.
* Soft delete, thùng rác, khôi phục và xóa vĩnh viễn có xác nhận.
* Export CSV thông qua `export_job` là bắt buộc; export ZIP là M1.
* Profile và đổi mật khẩu.
* Admin quản lý user và metadata tệp.
* Structured request logging.
* Trang quản lý, tìm kiếm, lọc, xem chi tiết và export log.
* Tạo dữ liệu normal và ba scenario bất thường.
* Feature engineering.
* Isolation Forest.
* Trang hiển thị và quản lý cảnh báo.
* Đánh giá mô hình.
* README, báo cáo, slide và kịch bản demo.

### 10.2. Phạm vi không thực hiện

* Không gọi sản phẩm là bản sao của một nền tảng lưu trữ cụ thể.
* Không xây frontend bằng React trong phiên bản chính.
* Không triển khai cloud hoặc hệ thống lưu trữ phân tán.
* Không chỉnh sửa Word, Excel hoặc PDF trực tuyến.
* Không đồng bộ tệp với máy tính.
* Không lưu nhiều phiên bản của một tệp.
* Không chia sẻ thư mục.
* Không chia sẻ bằng liên kết công khai.
* Không có quyền `EDITOR` trong phiên bản chính.
* Không bình luận, cộng tác thời gian thực hoặc thông báo đa kênh.
* Không upload tệp lớn hoặc tối ưu truyền tệp theo chunk.
* Không dùng deep learning, Autoencoder hoặc LSTM trong phiên bản chính.
* Không xây dựng detection realtime phức tạp, Kafka hoặc streaming.
* Không xây dựng microservices.
* Không phát hiện SQL Injection, XSS, CSRF hoặc Session Hijacking trong phiên bản chính.
* Không xây dựng WAF hoặc Firewall.
* Không thay thế authorization bằng Machine Learning.
* Không thu thập dữ liệu thật hoặc dữ liệu cá nhân ngoài phạm vi demo.
* Không mở ứng dụng thử nghiệm có chủ ý chứa lỗ hổng ra Internet công khai.

Mọi chức năng ngoài M0 và M1 đều là nội dung mở rộng, chỉ thực hiện sau khi phiên bản chính ổn định.

---

## 11. Công nghệ dự kiến

| Thành phần | Công nghệ |
| --- | --- |
| Ngôn ngữ chính | Python |
| Web framework | Flask |
| Giao diện | Jinja2, HTML, CSS, Bootstrap |
| Form/CSRF | Flask-WTF |
| Cơ sở dữ liệu/ORM | MySQL, SQLAlchemy, PyMySQL |
| Lưu tệp | Thư mục local có kiểm soát đường dẫn |
| Xử lý dữ liệu | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Mô hình chính | Isolation Forest |
| Lưu mô hình | Joblib |
| Biểu đồ | Matplotlib |
| Kiểm thử | Pytest, Postman, requests |
| Quản lý mã nguồn | Git và GitHub |
| Quản lý công việc | GitHub Projects hoặc Trello |

---

## 12. Deadline và board công việc

**Deadline cuối cùng: Chủ nhật, ngày 19/07/2026.**

Đến deadline, hệ thống phải chạy được luồng:

```text
User thao tác trên hệ thống lưu trữ tài liệu
→ Web kiểm tra OWNER/VIEWER
→ Ghi structured log
→ Tạo feature theo cửa sổ thời gian
→ Isolation Forest chấm điểm
→ Lưu và hiển thị alert
→ Admin truy ngược alert về log gốc
```

### TUẦN 1 — THIẾT KẾ VÀ NỀN TẢNG WEB

| Mã | Công việc | Deadline |
| --- | --- | --- |
| T01 | Hoàn thiện `docs/project_scope.md` | 2026-06-08 |
| T02 | Thiết kế use case User và Admin | 2026-06-09 |
| T03 | Thiết kế kiến trúc hệ thống | 2026-06-10 |
| T04 | Thiết kế cơ sở dữ liệu | 2026-06-11 |
| T05 | Thiết kế structured log schema | 2026-06-11 |
| T06 | Setup Flask project | 2026-06-12 |
| T07 | Xây dựng authentication và session | 2026-06-13 |
| T08 | Xây dựng phân quyền User/Admin và OWNER/VIEWER | 2026-06-14 |

### TUẦN 2 — HOÀN THIỆN WEB LƯU TRỮ VÀ CHIA SẺ TÀI LIỆU

| Mã | Công việc | Deadline |
| --- | --- | --- |
| T09 | Xây dựng dashboard User | 2026-06-15 |
| T10 | Xây dựng quản lý thư mục, upload, danh sách, chi tiết và download tệp | 2026-06-16 |
| T11 | Xây dựng search, filter, sort và pagination | 2026-06-17 |
| T12 | Xây dựng đổi tên, di chuyển, chia sẻ tệp và danh sách được chia sẻ | 2026-06-18 |
| T13 | Xây dựng trash, restore và xóa vĩnh viễn | 2026-06-19 |
| T14 | Xây dựng export CSV và export job/ZIP ở mức phù hợp | 2026-06-19 |
| T15 | Xây dựng profile và đổi mật khẩu | 2026-06-20 |
| T16 | Xây dựng quản lý user và metadata tệp cho Admin | 2026-06-21 |

### TUẦN 3 — LOGGING VÀ SINH DỮ LIỆU

| Mã | Công việc | Deadline |
| --- | --- | --- |
| T17 | Xây dựng request logging middleware | 2026-06-22 |
| T18 | Xây dựng trang quản lý log | 2026-06-23 |
| T19 | Xây dựng export log CSV | 2026-06-24 |
| T20 | Sinh dữ liệu normal | 2026-06-25 |
| T21 | Sinh dữ liệu Export Abuse | 2026-06-26 |
| T22 | Sinh dữ liệu Delete Abuse | 2026-06-27 |
| T23 | Sinh dữ liệu IDOR/BOLA Scan | 2026-06-28 |

### TUẦN 4 — XỬ LÝ DỮ LIỆU VÀ FEATURE ENGINEERING

| Mã | Công việc | Deadline |
| --- | --- | --- |
| T24 | Làm sạch và chuẩn hóa log | 2026-06-30 |
| T25 | Xây dựng feature engineering | 2026-07-03 |
| T26 | Chia train/validation/test và kiểm tra data leakage | 2026-07-05 |

### TUẦN 5 — MACHINE LEARNING VÀ TÍCH HỢP

| Mã | Công việc | Deadline |
| --- | --- | --- |
| T27 | Train Isolation Forest | 2026-07-07 |
| T28 | Đánh giá và tuning mô hình | 2026-07-10 |
| T29 | Tích hợp detection vào web | 2026-07-12 |

### TUẦN 6 — DASHBOARD, KIỂM THỬ VÀ HOÀN THIỆN

| Mã | Công việc | Deadline |
| --- | --- | --- |
| T30 | Xây dựng dashboard alerts | 2026-07-13 |
| T31 | Kiểm thử toàn hệ thống | 2026-07-15 |
| T32 | Hoàn thiện README | 2026-07-16 |
| T33 | Hoàn thiện báo cáo | 2026-07-16 |
| T34 | Làm slide và kịch bản demo | 2026-07-17 |
| T35 | Đóng gói và backup bản nộp | 2026-07-19 |

### 12.1. Cấu trúc board đề nghị

```text
Backlog → Doing → Testing → Done
```

Mỗi task cần có:

* Mã task và tiêu đề.
* Deadline.
* Nhãn tuần.
* Nhãn loại công việc: Web, Security, Logging, Data, ML, Documentation.
* Checklist nhỏ và tiêu chí Done.

---

## 13. Danh sách feature tối thiểu dự kiến

### 13.1. Hoạt động chung

* `request_count`
* `unique_endpoint_count`
* `unique_method_count`
* `session_duration_sec`
* `avg_inter_request_sec`
* `min_inter_request_sec`
* `burst_rate`
* `avg_response_time_ms`
* `error_rate`

### 13.2. Export Abuse

* `export_count`
* `export_ratio`
* `unique_export_job_count`
* `export_item_count_sum`
* `export_total_size_sum`
* `unique_exported_file_count`
* `time_to_first_export_sec`
* `export_denied_rate`

### 13.3. Delete Abuse

* `delete_count`
* `delete_ratio`
* `unique_deleted_file_count`
* `unique_affected_folder_count`
* `avg_inter_delete_sec`
* `time_to_first_delete_sec`
* `delete_permission_mismatch_rate`

### 13.4. IDOR/BOLA Scan

* `unique_resource_id_count`
* `unique_failed_resource_id_count`
* `resource_id_change_rate`
* `permission_none_rate`
* `authorization_denied_rate`
* `forbidden_count`
* `forbidden_rate`
* `not_found_count`
* `not_found_rate`
* `unique_resource_type_count`

Không bắt buộc giữ toàn bộ feature. Chỉ sử dụng feature có công thức rõ ràng, không chứa nhãn, không rò rỉ ground truth và có ý nghĩa trong phân tích hành vi.

---

## 14. Tiêu chí hoàn thành

### 14.1. Web và phân quyền

* [ ] Ứng dụng đăng nhập, đăng xuất và quản lý session được.
* [ ] Có hai vai trò User và Admin.
* [ ] Có quyền tệp OWNER và VIEWER.
* [ ] User tạo thư mục, upload, xem và download tệp được.
* [ ] Có đổi tên, di chuyển, tìm kiếm, lọc và phân trang.
* [ ] Có chia sẻ từng tệp; không chia sẻ thư mục.
* [ ] Có export, soft delete, thùng rác và khôi phục.
* [ ] Admin quản lý user và metadata tệp được.
* [ ] Request trái quyền không làm lộ metadata hoặc nội dung tệp.

### 14.2. Logging và dữ liệu

* [ ] Các request quan trọng được ghi structured log.
* [ ] Log có `resource_type`, `resource_id`, `permission` và `authorization_result`.
* [ ] Log không chứa password, cookie hoặc token nguyên bản.
* [ ] Admin có thể xem, lọc, phân trang và export log.
* [ ] Có dữ liệu normal và dữ liệu ba scenario.
* [ ] Có ground truth phục vụ đánh giá.

### 14.3. Machine Learning và cảnh báo

* [ ] Có pipeline tạo feature theo cửa sổ thời gian.
* [ ] Train set chủ yếu chứa dữ liệu normal.
* [ ] Huấn luyện và lưu được Isolation Forest.
* [ ] Hệ thống trả anomaly score và prediction.
* [ ] Chạy thử được Export Abuse, Delete Abuse và IDOR/BOLA Scan.
* [ ] Alert liên kết được feature và log gốc.
* [ ] Có Precision, Recall, F1-score, False Positive Rate và Confusion Matrix.
* [ ] Có detection rate theo từng scenario.

### 14.4. Tài liệu và đóng gói

* [ ] Có README hướng dẫn cài đặt và chạy.
* [ ] Có script seed/reset dữ liệu.
* [ ] Có báo cáo, slide và kịch bản demo.
* [ ] Có video demo dự phòng.
* [ ] Có backup source, dữ liệu mẫu và model.
* [ ] Hoàn thành trước hoặc trong ngày 19/07/2026.

---

## 15. Quy tắc kiểm soát phạm vi

Trước khi thêm chức năng mới, phải trả lời ba câu hỏi:

1. Chức năng này có trực tiếp phục vụ lưu trữ/chia sẻ tệp, structured logging hoặc một trong ba scenario không?
2. Chức năng này có thuộc M0 hoặc M1 không?
3. Nếu không làm chức năng này, luồng demo chính có bị mất không?

Nếu cả ba câu trả lời đều là “không”, chức năng đó không được đưa vào phiên bản chính.

Thứ tự ưu tiên khi bị trễ:

```text
Giữ M0 → hoàn thiện logging → giữ ba simulator → hoàn thiện ML tối thiểu
→ sau đó mới làm M1 còn thiếu → không làm M2
```

---

## 16. Ba điều cần xác nhận với giảng viên

1. Với ba scenario Export Abuse, Delete Abuse và IDOR/BOLA Scan, nên huấn luyện một Isolation Forest chung trên dữ liệu normal rồi dùng feature để gợi ý scenario, hay nên xây mô hình riêng cho từng scenario?
2. Các trường `user_id`, `session_id_hash`, `resource_type`, `resource_id`, `permission`, `authorization_result` và `status_code` đã đủ để chứng minh IDOR/BOLA Scan chưa, hay cần bổ sung trường nào khác?
3. Với phạm vi sáu tuần, chức năng export ZIP theo `export_job` có cần bắt buộc hay chỉ cần export CSV và log đầy đủ để thực hiện Export Abuse?

---

## 17. Kết quả cần đạt trong ngày cập nhật scope

* [ ] `docs/project_scope.md` đã mô tả rõ hệ thống lưu trữ và chia sẻ tài liệu trực tuyến.
* [ ] Không còn mô tả tài liệu như một bản ghi `title/content` dùng CRUD.
* [ ] Đã xác định User/Admin và quyền OWNER/VIEWER.
* [ ] Đã xác định không chia sẻ folder trong phiên bản chính.
* [ ] Chức năng đã được chia thành M0/M1/M2.
* [ ] Mỗi chức năng chính đã chỉ ra scenario liên quan.
* [ ] Ba scenario sử dụng rõ `file_id`, `folder_id`, `export_job_id` và `permission`.
* [ ] GitHub Project đã cập nhật đủ T01–T35 và deadline 19/07/2026.
* [ ] Phần “không làm” đã được ghi riêng để ngăn lan scope.
* [ ] Tên đề tài, web nghiệp vụ, chức năng và ba scenario không còn mâu thuẫn.
