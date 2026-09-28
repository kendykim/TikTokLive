# TikTokLive 使用指南

本指南介绍如何运行应用，并接收 TikTok LIVE 观众发送的评论、点赞和礼物事件。

> TikTokLive 是非官方客户端。目标账号必须正在直播，运行应用的电脑也必须能够访问互联网。

## 1. 工作原理

1. 应用从 `.env` 或 Web UI 读取 TikTok 用户名。
2. 查找当前直播间的 `room_id`。
3. 获取已签名的 WebSocket 地址。
4. 连接 TikTok LIVE 并解析实时消息。
5. 通过 Server-Sent Events（SSE）把 `CommentEvent`、`LikeEvent` 和 `GiftEvent` 发送到浏览器。

读取公开直播不需要 TikTok Developer API key 或 TikTok API secret。`SIGN_API_KEY` 是可选的 Euler Stream 密钥，并不是 TikTok 密钥。

## 2. 安装

需要 Python 3.10 或更高版本，以及可用的互联网连接。

```powershell
cd D:\TikTokLive-master\TikTokLive-master
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
```

如果 PowerShell 阻止激活虚拟环境：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. `.env` 配置

编辑 `D:\TikTokLive-master\TikTokLive-master\.env`，也可以在 Web UI 的 **Settings (.env)** 中修改。

```dotenv
TIKTOK_UNIQUE_ID=@tiktok_username
ONLY_NEW_COMMENTS=true
LOG_LEVEL=INFO
SIGN_API_URL=https://api.eulerstream.com
SIGN_API_KEY=
TIKTOK_SESSION_ID=
TIKTOK_TARGET_IDC=
WHITELIST_AUTHENTICATED_SESSION_ID_HOST=
```

通常只需要设置 `TIKTOK_UNIQUE_ID`。公开直播无需填写 API key 或 TikTok session。不要分享包含真实密钥的 `.env` 文件。

## 4. 运行 Web UI

```powershell
cd D:\TikTokLive-master\TikTokLive-master
.\.venv\Scripts\Activate.ps1
py start.py
```

打开 `http://127.0.0.1:5555`，选择语言，输入 TikTok 用户名，然后点击 **连接**。停止服务器前先点击 **断开连接**，再按 `Ctrl+C`。

使用项目根目录中的 Python 启动文件检查缺少的依赖并启动服务器：

```powershell
cd D:\TikTokLive-master\TikTokLive-master
.\.venv\Scripts\Activate.ps1
py start.py
```

如果系统没有 `py` 启动器，请使用 `python start.py`。

事件列表会显示：

- 评论：观众昵称和评论内容。
- 点赞：观众昵称、本次事件的点赞数和 TikTok 返回的总数。
- 礼物：观众昵称、礼物名称和数量。

## 5. 运行命令行示例

```powershell
python examples\comments.py
python examples\gifts.py
python examples\check_live.py
python examples\images.py
python examples\recording.py
```

所有示例都使用 `.env` 中的 `TIKTOK_UNIQUE_ID`。录制直播还需要安装 FFmpeg。

## 6. 处理事件

```python
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent, LikeEvent

client = TikTokLiveClient(unique_id="@username")

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    print(event.user.nickname, event.comment)

@client.on(LikeEvent)
async def on_like(event: LikeEvent):
    print(event.user.nickname, event.count, event.total)

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    if event.gift.streakable and event.streaking:
        return
    print(event.user.nickname, event.gift.name, event.repeat_count)

client.run()
```

TikTok 可能把多次点赞合并到一个 `LikeEvent` 中，因此不能认为一个事件只代表一个赞。

可连击的礼物在观众持续点击时会产生多个中间事件。当 `event.gift.streakable` 和 `event.streaking` 都为 true 时，应忽略该事件。最后一个事件包含完整的 `repeat_count`，这样可以避免重复计数。

## 7. 可选的 TikTok Session

普通公开直播不需要 session。只有必须登录才能访问的内容才需要同时填写：

```dotenv
TIKTOK_SESSION_ID=sessionid_cookie
TIKTOK_TARGET_IDC=tt_target_idc_cookie
WHITELIST_AUTHENTICATED_SESSION_ID_HOST=api.eulerstream.com
```

`sessionid` cookie 可访问 TikTok 账号。只允许你信任的签名服务器接收它。

## 8. 常见问题

- **用户未直播：**检查用户名，并确认账号当前正在直播。
- **没有事件：**等待新的互动，确认界面显示已连接，并尝试设置 `LOG_LEVEL=DEBUG`。
- **签名或限流错误：**检查 `SIGN_API_URL`，稍后重试，或配置有效的 Euler Stream key。
- **虚拟环境损坏：**重新创建 `.venv`，再运行 `pip install -e .`。
- **无法打开 Web UI：**确认终端显示 `Running on http://127.0.0.1:5555`，并检查 5555 端口是否被占用。
