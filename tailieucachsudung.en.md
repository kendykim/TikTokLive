# TikTokLive User Guide

This guide explains how to run the application and receive comments, likes, and gifts from viewers during a TikTok LIVE session.

> TikTokLive is an unofficial client. The target account must be LIVE and the computer running the application must have Internet access.

## 1. How it works

1. The application reads the TikTok username from `.env` or the Web UI.
2. It resolves the active LIVE room ID.
3. It obtains a signed WebSocket address.
4. It connects to TikTok LIVE and decodes incoming messages.
5. `CommentEvent`, `LikeEvent`, and `GiftEvent` are sent to the browser through Server-Sent Events (SSE).

No TikTok Developer API key or TikTok API secret is required for public LIVE streams. `SIGN_API_KEY` is an optional Euler Stream key, not a TikTok secret.

## 2. Installation

Requirements: Python 3.10 or newer and an Internet connection.

```powershell
cd D:\TikTokLive-master\TikTokLive-master
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. Environment configuration

Edit `D:\TikTokLive-master\TikTokLive-master\.env`, or use **Settings (.env)** in the Web UI.

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

Only `TIKTOK_UNIQUE_ID` is normally required. Leave the API key and TikTok session fields blank for public streams. Never share a real `.env` containing secrets.

## 4. Run the Web UI

```powershell
cd D:\TikTokLive-master\TikTokLive-master
.\.venv\Scripts\Activate.ps1
py start.py
```

Open `http://127.0.0.1:5555`, select a language, enter the TikTok username, and click **Connect**. Use **Disconnect** before stopping the server with `Ctrl+C`.

Use the root Python entry point to check missing dependencies and start the server:

```powershell
cd D:\TikTokLive-master\TikTokLive-master
.\.venv\Scripts\Activate.ps1
py start.py
```

If the `py` launcher is unavailable, use `python start.py`.

The feed displays:

- Comments: viewer nickname and message.
- Likes: viewer nickname, likes in the current event, and the reported total.
- Gifts: viewer nickname, gift name, and quantity.

## 5. Run terminal examples

```powershell
python examples\comments.py
python examples\gifts.py
python examples\check_live.py
python examples\images.py
python examples\recording.py
```

All examples use `TIKTOK_UNIQUE_ID` from `.env`. Recording also requires FFmpeg.

## 6. Event handling

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

TikTok may combine multiple likes into one `LikeEvent`; do not assume one event equals one like.

Streakable gifts generate intermediate events while the viewer keeps tapping. Ignore events where both `event.gift.streakable` and `event.streaking` are true. The final event contains the complete `repeat_count`, preventing duplicate counting.

## 7. Optional TikTok session

A session is not required for ordinary public LIVE streams. For content that requires login, set all three values:

```dotenv
TIKTOK_SESSION_ID=sessionid_cookie
TIKTOK_TARGET_IDC=tt_target_idc_cookie
WHITELIST_AUTHENTICATED_SESSION_ID_HOST=api.eulerstream.com
```

The `sessionid` cookie grants access to the TikTok account. Only send it to a signing host you trust.

## 8. Troubleshooting

- **User offline:** verify the username and confirm the account is currently LIVE.
- **No events:** wait for new interactions, confirm the UI says Connected, and try `LOG_LEVEL=DEBUG`.
- **Signing/rate-limit error:** verify `SIGN_API_URL`, retry later, or configure a valid Euler Stream key.
- **Broken virtual environment:** recreate `.venv` and run `pip install -e .` again.
- **Web UI unavailable:** confirm the terminal shows `Running on http://127.0.0.1:5555` and that port 5555 is free.
