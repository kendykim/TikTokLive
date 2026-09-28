# Hướng dẫn sử dụng TikTokLive

Tài liệu này hướng dẫn cài đặt và vận hành ứng dụng để nhận sự kiện bình luận, thả tim và quà tặng từ người xem trong một phiên TikTok LIVE.

> TikTokLive là thư viện không chính thức. Ứng dụng chỉ nhận được sự kiện khi tài khoản mục tiêu đang phát LIVE và máy chạy ứng dụng có kết nối Internet.

## 1. Ứng dụng hoạt động như thế nào?

Luồng hoạt động chính:

1. Đọc tên tài khoản TikTok từ `.env` hoặc từ ô username trên Web UI.
2. Tìm `room_id` của phiên LIVE đang hoạt động.
3. Lấy địa chỉ WebSocket đã được ký từ signing service.
4. Mở kết nối WebSocket tới TikTok LIVE.
5. Chuyển dữ liệu nhận được thành các event Python.
6. Web UI chuyển event sang trình duyệt bằng Server-Sent Events (SSE).

Ứng dụng hiện xử lý ba event chính:

- `CommentEvent`: người xem gửi bình luận.
- `LikeEvent`: người xem thả tim.
- `GiftEvent`: người xem gửi quà tặng.

Không cần TikTok Developer API key hoặc TikTok API secret để đọc một LIVE công khai. `SIGN_API_KEY` trong `.env` là khóa tùy chọn của Euler Stream, không phải secret key của TikTok.

## 2. Yêu cầu hệ thống

- Python 3.10 trở lên.
- Windows PowerShell hoặc terminal tương đương.
- Internet ổn định.
- Tài khoản TikTok mục tiêu đang phát LIVE.

Kiểm tra Python:

```powershell
py --version
```

Nếu lệnh không hoạt động, hãy cài Python và bật tùy chọn `Add Python to PATH` trong trình cài đặt.

## 3. Cài đặt dự án

Mở PowerShell và chạy:

```powershell
cd D:\TikTokLive-master\TikTokLive-master

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e .
```

Nếu PowerShell chặn kích hoạt môi trường ảo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 4. Cấu hình `.env`

File cấu hình nằm tại:

```text
D:\TikTokLive-master\TikTokLive-master\.env
```

Cấu hình tối thiểu:

```dotenv
TIKTOK_UNIQUE_ID=@ten_tai_khoan_tiktok
ONLY_NEW_COMMENTS=true
LOG_LEVEL=INFO

SIGN_API_URL=https://api.eulerstream.com
SIGN_API_KEY=

SIGN_SERVER_MESSAGE_DISABLED=false
SEND_DEPRECATION_WARNINGS=true

TIKTOK_SESSION_ID=
TIKTOK_TARGET_IDC=
WHITELIST_AUTHENTICATED_SESSION_ID_HOST=
```

Ý nghĩa các biến:

| Biến | Bắt buộc | Ý nghĩa |
|---|---:|---|
| `TIKTOK_UNIQUE_ID` | Có | Username của người đang LIVE, có thể có hoặc không có ký tự `@`. |
| `ONLY_NEW_COMMENTS` | Không | `true` để ví dụ `comments.py` bỏ qua comment cũ nhận ngay khi vừa kết nối. |
| `LOG_LEVEL` | Không | Mức log: `DEBUG`, `INFO`, `WARNING` hoặc `ERROR`. |
| `SIGN_API_URL` | Không | Signing service; mặc định là Euler Stream. |
| `SIGN_API_KEY` | Không | API key tùy chọn của Euler Stream để dùng hạn mức tương ứng. |
| `TIKTOK_SESSION_ID` | Không | Cookie đăng nhập TikTok; không cần cho LIVE công khai. |
| `TIKTOK_TARGET_IDC` | Không | Data-center cookie đi kèm `TIKTOK_SESSION_ID`. |
| `WHITELIST_AUTHENTICATED_SESSION_ID_HOST` | Không | Host được phép nhận session, ví dụ `api.eulerstream.com`. |

Không đưa `.env` có secret thật cho người khác. Dự án đã khai báo `.env` trong `.gitignore`.

## 5. Chạy bằng Web UI

Khởi động server:

```powershell
cd D:\TikTokLive-master\TikTokLive-master
.\.venv\Scripts\Activate.ps1
py start.py
```

Mở trình duyệt tại:

```text
http://127.0.0.1:5555
```

### Khởi động bằng Python

Ứng dụng có một điểm khởi động duy nhất ở thư mục gốc:

```powershell
cd D:\TikTokLive-master\TikTokLive-master
.\.venv\Scripts\Activate.ps1
py start.py
```

`start.py` kiểm tra dependency trước khi mở server. Nó chỉ gọi `pip install` cho những package còn thiếu, ví dụ chỉ cài `markdown` nếu các package khác đã có.

Nếu lệnh `py` không có nhưng `python` hoạt động, dùng:

```powershell
python start.py
```

### Cấu hình trên giao diện

1. Mở mục **Settings (.env)**.
2. Nhập `TikTok username`, ví dụ `@ten_tai_khoan`.
3. Để trống Sign API key và TikTok session nếu chỉ đọc LIVE công khai.
4. Bấm **Save .env**.
5. Bấm **Connect**.

Sau khi kết nối thành công, feed sẽ hiển thị:

- `Connected to @username`: đã kết nối với phòng LIVE.
- Comment: nickname và nội dung bình luận.
- Gift: nickname, tên quà và số lượng.
- Like: nickname, số tim trong event và tổng số tim TikTok báo về.

Bấm **Disconnect** để đóng kết nối hiện tại.

Các ô password không hiển thị lại secret đã lưu. Giao diện chỉ báo secret đã được cấu hình. Nhập giá trị mới để thay thế, hoặc chọn `Clear saved value` rồi lưu để xóa.

## 6. Chạy từng ví dụ bằng terminal

Đọc comment:

```powershell
python examples\comments.py
```

Đọc quà tặng:

```powershell
python examples\gifts.py
```

Kiểm tra LIVE và tự kết nối khi tài khoản bắt đầu LIVE:

```powershell
python examples\check_live.py
```

Tải avatar người gửi comment:

```powershell
python examples\images.py
```

Ghi hình LIVE (máy cần có FFmpeg hoạt động):

```powershell
python examples\recording.py
```

Tất cả các ví dụ trên dùng chung `TIKTOK_UNIQUE_ID` trong `.env`.

## 7. Cách nhận comment, tim và gift trong Python

Mẫu listener cơ bản:

```python
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, ConnectEvent, GiftEvent, LikeEvent

client = TikTokLiveClient(unique_id="@ten_tai_khoan")


@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Đã kết nối @{event.unique_id}, room ID: {event.room_id}")


@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    print(f"COMMENT | {event.user.nickname}: {event.comment}")


@client.on(LikeEvent)
async def on_like(event: LikeEvent):
    print(
        f"LIKE | {event.user.nickname}: "
        f"+{event.count} tim, tổng TikTok báo về: {event.total}"
    )


@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    # Gift dạng streak phát nhiều event trung gian. Chỉ xử lý event cuối
    # để không tính trùng toàn bộ chuỗi quà.
    if event.gift.streakable and event.streaking:
        return

    print(
        f"GIFT | {event.user.nickname}: "
        f"{event.repeat_count}x {event.gift.name}"
    )


client.run()
```

### CommentEvent

Các trường thường dùng:

```python
event.user.unique_id   # username TikTok
event.user.nickname    # tên hiển thị
event.comment          # nội dung bình luận
```

### LikeEvent

Các trường thường dùng:

```python
event.user.nickname
event.count            # số lượt tim trong event hiện tại
event.total            # tổng lượt tim TikTok gửi kèm event
```

TikTok có thể gộp nhiều lượt thả tim vào một event, vì vậy không nên giả định mỗi `LikeEvent` luôn tương ứng với đúng một tim.

### GiftEvent và gift streak

Các trường thường dùng:

```python
event.user.unique_id
event.user.nickname
event.gift.name
event.gift.diamond_count
event.repeat_count
event.gift.streakable
event.streaking
```

Một số gift cho phép người xem bấm liên tục thành chuỗi. TikTok gửi nhiều event trong lúc chuỗi vẫn tiếp diễn và tăng dần `repeat_count`. Nếu cộng mọi event, tổng quà sẽ bị đếm trùng.

Quy tắc xử lý an toàn:

```python
if event.gift.streakable and event.streaking:
    return

# Chỉ chạy với gift không streak hoặc event cuối của chuỗi.
quantity = event.repeat_count
```

## 8. Luồng dữ liệu của Web UI

Backend trong `examples/web-ui/service.py` đăng ký các event listener. Khi nhận event, backend đưa dữ liệu vào queue. Endpoint `/api/stream` phát queue tới trình duyệt bằng SSE, sau đó JavaScript thêm event mới vào feed.

```text
TikTok WebSocket
      ↓
TikTokLiveClient
      ↓
CommentEvent / LikeEvent / GiftEvent
      ↓
Queue của Flask
      ↓
/api/stream (SSE)
      ↓
Web UI
```

API cấu hình của Web UI:

- `GET /api/config`: đọc các biến cấu hình không nhạy cảm và trạng thái secret.
- `PUT /api/config`: lưu các biến được phép vào `.env`.
- `POST /api/connect`: kết nối tài khoản được nhập trên giao diện hoặc `TIKTOK_UNIQUE_ID`.
- `POST /api/disconnect`: ngắt kết nối.
- `GET /api/stream`: nhận luồng event SSE.

## 9. Khi nào cần TikTok session?

Không cần session khi đọc LIVE công khai thông thường.

Session chỉ nên dùng khi thật sự cần truy cập nội dung yêu cầu đăng nhập, chẳng hạn phòng bị giới hạn độ tuổi. Khi dùng session, phải điền đủ:

```dotenv
TIKTOK_SESSION_ID=gia_tri_cookie_sessionid
TIKTOK_TARGET_IDC=gia_tri_cookie_tt_target_idc
WHITELIST_AUTHENTICATED_SESSION_ID_HOST=api.eulerstream.com
```

`sessionid` có quyền truy cập tài khoản TikTok. Không gửi nó cho người khác và chỉ cho phép signing host mà bạn tin tưởng.

## 10. Lỗi thường gặp

### `User is offline` hoặc `That user is not currently live`

- Kiểm tra username có đúng không.
- Tài khoản phải đang phát LIVE tại thời điểm kết nối.
- Thử nhập username có ký tự `@`.

### `TIKTOK_UNIQUE_ID is missing`

Mở `.env` và điền:

```dotenv
TIKTOK_UNIQUE_ID=@username
```

### Không nhận được comment, tim hoặc gift

- Đảm bảo Web UI đã báo `Connected`.
- Đợi một tương tác mới sau thời điểm kết nối.
- Đặt `LOG_LEVEL=DEBUG`, lưu cấu hình và kết nối lại để xem log chi tiết.
- Kiểm tra firewall, proxy và kết nối Internet.

### Lỗi signing service hoặc rate limit

- Kiểm tra `SIGN_API_URL=https://api.eulerstream.com`.
- Thử lại sau nếu dịch vụ đang giới hạn request.
- Có thể nhập Euler Stream `SIGN_API_KEY` nếu bạn có khóa hợp lệ.

### `.venv` trỏ tới Python đã bị xóa

Xóa hoặc đổi tên môi trường ảo cũ, sau đó tạo lại:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

### Web UI không mở được

Kiểm tra terminal có dòng tương tự:

```text
Running on http://127.0.0.1:5555
```

Nếu cổng 5555 đang được ứng dụng khác sử dụng, đổi giá trị `port=5555` trong `service.py` sang một cổng khác, ví dụ `port=5556`.

## 11. Dừng ứng dụng

Trên Web UI, bấm **Disconnect** trước. Sau đó quay lại PowerShell và nhấn:

```text
Ctrl + C
```

Khi mở lại ứng dụng, cấu hình đã lưu trong `.env` vẫn được sử dụng.
