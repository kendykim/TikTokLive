# TikTokLive Python Client and Local Web UI

An unofficial Python client and local dashboard for receiving real-time events
from TikTok LIVE streams. Connect with a creator's `@unique_id` and process
comments, likes, gifts, follows, shares, viewer counts, battles, and other
Webcast events.

This distribution is based on the original
[TikTokLive project](https://github.com/isaackogan/TikTokLive), created and
maintained by **Isaac Kogan**. The local Web UI, operating workflow,
configuration tools, updated examples, and multilingual source guides in this
distribution were added or revised by **Kendykim**. The original attribution
and existing license remain unchanged.

> [!WARNING]
> TikTokLive is an unofficial reverse-engineering project and is not affiliated
> with, endorsed by, or supported by TikTok. TikTok can change its internal
> endpoints at any time. Do not treat this project as a production SLA.

## Contents

- [Features](#features)
- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Environment configuration](#environment-configuration)
- [Run the Web UI](#run-the-web-ui)
- [Web UI API](#web-ui-api)
- [Use the Python client](#use-the-python-client)
- [Events and gift streaks](#events-and-gift-streaks)
- [Runnable examples](#runnable-examples)
- [Authenticated sessions](#authenticated-sessions)
- [Operating the application](#operating-the-application)
- [Troubleshooting](#troubleshooting)
- [Project layout](#project-layout)
- [Upstream documentation and community](#upstream-documentation-and-community)
- [License and credits](#license-and-credits)

## Features

### Upstream TikTokLive library

- Asynchronous TikTok LIVE WebSocket client for Python 3.10 and newer.
- Typed custom events and protocol-generated Webcast events.
- Real-time comments, gifts, likes, follows, shares, joins, viewer counts,
  subscriptions, polls, captions, battles, moderation events, and more.
- Optional HTTP and WebSocket proxy support.
- Optional authenticated TikTok session support.
- Helpers for room information, gift information, images, video data, and LIVE
  status checks.

### Kendykim distribution additions

- Local Flask dashboard at `http://127.0.0.1:5555`.
- Connect and disconnect controls with live connection status.
- Comment, like, and gift feed delivered with Server-Sent Events (SSE).
- A rolling history of the latest 500 events, including replay by event ID.
- Local JSON endpoints for status, event history, configuration, and guides.
- CORS headers for local applications and browser extensions.
- Safe `.env` editing: stored secrets are never returned to the browser.
- One root launcher, `start.py`, which installs only missing runtime packages
  before starting the Web UI.
- Shared `.env` configuration across runnable examples.
- Optional removal of comments created before the client connected.
- Built-in user-guide rendering and source guides in English, Vietnamese, and
  Chinese.

## How it works

The client follows this flow:

1. Read a TikTok username from `.env` or the Web UI.
2. Resolve the active LIVE room ID.
3. Request a signed WebSocket URL from the configured signing service.
4. Connect to the TikTok LIVE WebSocket.
5. Decode incoming Webcast messages into Python event objects.
6. Pass selected events to the local browser through SSE.

```text
TikTok LIVE WebSocket
        |
        v
TikTokLiveClient
        |
        v
CommentEvent / LikeEvent / GiftEvent
        |
        v
Flask event queue and 500-event history
        |
        +--> /api/stream (SSE) --> Web UI or browser extension
        |
        +--> /api/events (JSON replay)
```

A TikTok Developer API key or TikTok API secret is not required for an
ordinary public LIVE stream. `SIGN_API_KEY` is an optional key for the signing
service; it is not a TikTok Developer secret.

## Requirements

- Python 3.10 or newer.
- A stable Internet connection.
- A target TikTok account that is currently LIVE.
- PowerShell for the commands below, or an equivalent terminal.
- FFmpeg only when using the recording example.

Check the installed Python version:

```powershell
py --version
```

If `py` is unavailable but `python` works, replace `py` with `python` in the
commands below.

## Installation

From the project directory:

```powershell
cd D:\TikTokLive-master\TikTokLive-master
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
```

If PowerShell blocks virtual-environment activation, allow it for the current
PowerShell process only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

## Environment configuration

Configuration is stored in `.env` at the project root. It can be edited
manually or through **Settings (.env)** in the Web UI.

Recommended starting configuration:

```dotenv
TIKTOK_UNIQUE_ID=@tiktok_username
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

| Variable | Required | Purpose |
|---|---:|---|
| `TIKTOK_UNIQUE_ID` | Yes | Username of the creator who is LIVE. The leading `@` is optional. |
| `ONLY_NEW_COMMENTS` | No | When `true`, `examples/comments.py` ignores comments created before the connection time. |
| `LOG_LEVEL` | No | Client log level: `DEBUG`, `INFO`, `WARNING`, or `ERROR`. |
| `SIGN_API_URL` | No | Signing-service base URL. The configured default is Euler Stream. |
| `SIGN_API_KEY` | No | Optional signing-service key for the associated service limits. |
| `SIGN_SERVER_MESSAGE_DISABLED` | No | Controls display of messages returned by the signing service. |
| `SEND_DEPRECATION_WARNINGS` | No | Enables or disables client deprecation warnings. |
| `TIKTOK_SESSION_ID` | No | TikTok `sessionid` cookie for content that requires authentication. |
| `TIKTOK_TARGET_IDC` | No | TikTok data-center cookie paired with `TIKTOK_SESSION_ID`. |
| `WHITELIST_AUTHENTICATED_SESSION_ID_HOST` | No | Signing host allowed to receive authenticated session data. |

Do not commit or share a real `.env` file containing secrets. `.env` is already
listed in `.gitignore`.

## Run the Web UI

Activate the virtual environment and run the root entry point:

```powershell
cd D:\TikTokLive-master\TikTokLive-master
.\.venv\Scripts\Activate.ps1
py start.py
```

`start.py` checks the runtime dependencies declared in `pyproject.toml`,
installs only packages that are missing from the active Python environment,
and starts the Flask service. You can also use:

```powershell
python start.py
```

Open `http://127.0.0.1:5555` in a browser, then:

1. Expand **Settings (.env)**.
2. Enter the TikTok username, for example `@creator_name`.
3. Leave the signing API key and TikTok session fields blank for a normal
   public stream.
4. Select **Save settings**.
5. Select **Connect**.

After the connection succeeds, the feed displays:

- connection and disconnection messages;
- viewer nickname and text for comments;
- viewer nickname, event count, and reported total for likes;
- viewer nickname, gift name, and final quantity for gifts.

Use **Disconnect** to close the current LIVE connection gracefully.

### Secret handling in the UI

Password fields never display saved secret values. The UI reports only whether
a secret is configured. Leave a password field blank to preserve its current
value, enter a new value to replace it, or select **Clear saved value** and save
the settings to remove it.

### Built-in guide

The **User guide** dialog loads Markdown through `/api/guide`. English,
Vietnamese, and Chinese guide files are available in the repository, while
this README is the complete English reference for the distribution.

## Web UI API

The local service exposes the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serve the Web UI. |
| `POST` | `/api/connect` | Connect to the JSON `username`, or fall back to `TIKTOK_UNIQUE_ID`. |
| `POST` | `/api/disconnect` | Gracefully disconnect the current client. |
| `GET` | `/api/status` | Return connection status, username, error, and LIVE session ID. |
| `GET` | `/api/events?since=<id>` | Return buffered events newer than the supplied event ID. |
| `GET` | `/api/stream?since=<id>` | Open the SSE stream and optionally replay newer buffered events. |
| `GET` | `/api/config` | Return public settings and booleans indicating configured secrets. |
| `PUT` | `/api/config` | Update allowed `.env` values and explicitly clear selected secrets. |
| `GET` | `/api/guide?lang=en` | Render the selected Markdown guide (`en`, `vi`, or `zh`). |

The event payload has a monotonically increasing `id`, a `type`, and a Unix
timestamp in `ts`. Event-specific fields are included alongside them:

```json
{
  "id": 1720000000000,
  "type": "comment",
  "ts": 1720000000.0,
  "user": "Viewer name",
  "comment": "Hello"
}
```

The backend retains at most 500 events in memory. Clients can resume SSE with
the `since` query parameter or the `Last-Event-ID` header. `/api/events` can be
used for JSON polling or recovery. History is cleared when the Python process
stops and is not a persistent database.

API routes include permissive CORS headers for local extension integration.
The Flask service binds to `127.0.0.1`, so it is not exposed to other machines
unless the code or network configuration is changed.

## Use the Python client

Minimal example:

```python
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, ConnectEvent, GiftEvent, LikeEvent

client = TikTokLiveClient(unique_id="@creator_name")


@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent) -> None:
    print(f"Connected to @{event.unique_id}; room ID: {event.room_id}")


@client.on(CommentEvent)
async def on_comment(event: CommentEvent) -> None:
    print(f"COMMENT | {event.user.nickname}: {event.comment}")


@client.on(LikeEvent)
async def on_like(event: LikeEvent) -> None:
    print(f"LIKE | {event.user.nickname}: +{event.count}; total: {event.total}")


@client.on(GiftEvent)
async def on_gift(event: GiftEvent) -> None:
    if event.gift is None:
        return
    if event.gift.streakable and event.streaking:
        return
    print(f"GIFT | {event.user.nickname}: {event.repeat_count}x {event.gift.name}")


if __name__ == "__main__":
    client.run()
```

Listeners can also be registered manually:

```python
async def on_comment(event: CommentEvent) -> None:
    print(event.comment)

client.add_listener(CommentEvent, on_comment)
```

### Main client parameters

| Parameter | Required | Description |
|---|---:|---|
| `unique_id` | Yes | Broadcaster username, with or without `@`. |
| `web_proxy` | No | `httpx.Proxy` used for HTTP requests. |
| `ws_proxy` | No | Proxy used for the WebSocket connection. |
| `web_kwargs` | No | Extra arguments forwarded to the underlying HTTP client. |
| `ws_kwargs` | No | Extra arguments forwarded to the WebSocket client. |

### Main methods

| Method | Description |
|---|---|
| `run()` | Connect and block the main thread. Suitable for small scripts. |
| `connect()` | Asynchronously connect and block until the connection ends. |
| `start()` | Start asynchronously and return the client task. |
| `disconnect()` | Gracefully disconnect and process remaining events. |
| `add_listener()` | Register an asynchronous listener for an event type. |
| `is_live()` | Check whether the configured creator is currently LIVE. |

### Useful properties

| Property | Description |
|---|---|
| `room_id` | Current LIVE room ID. |
| `connected` | Whether the client is currently connected. |
| `web` | TikTok HTTP client and its available routes. |
| `logger` | Internal logger; use it to change the log level. |
| `room_info` | Room information when requested during connection. |
| `gift_info` | Gift metadata when requested during connection. |

## Events and gift streaks

Frequently used fields include:

```python
# CommentEvent
event.user.unique_id
event.user.nickname
event.comment

# LikeEvent
event.user.nickname
event.count
event.total

# GiftEvent
event.user.unique_id
event.user.nickname
event.gift.name
event.gift.diamond_count
event.repeat_count
event.gift.streakable
event.streaking
```

TikTok can combine several likes into one `LikeEvent`; one event does not
necessarily represent one like.

Streakable gifts generate intermediate events while the viewer continues
tapping. Adding every intermediate `repeat_count` produces duplicate totals.
Use this rule:

```python
if event.gift.streakable and event.streaking:
    return

quantity = event.repeat_count
```

This processes non-streak gifts immediately and streak gifts only after the
final event contains the complete quantity.

TikTokLive also exposes many other custom and protocol-generated events,
including `DisconnectEvent`, `LiveEndEvent`, `FollowEvent`, `ShareEvent`,
`JoinEvent`, `RoomUserSeqEvent`, `SubscribeEvent`, `PollEvent`, `CaptionEvent`,
and battle events. See the
[upstream event documentation](https://isaackogan.github.io/TikTokLive/TikTokLive.events.html)
for the complete schema available in the installed version.

## Runnable examples

All runnable examples read `TIKTOK_UNIQUE_ID` from the root `.env` file:

```powershell
python examples\comments.py
python examples\gifts.py
python examples\check_live.py
python examples\images.py
python examples\recording.py
python examples\proxying.py
python examples\logged_in.py
python examples\web_defaults.py
```

| Example | Purpose |
|---|---|
| `comments.py` | Print comments with timestamps and optionally ignore the initial backlog. |
| `gifts.py` | Receive gifts and handle streak completion. |
| `check_live.py` | Check LIVE status and connect when the creator starts streaming. |
| `images.py` | Download image data such as viewer avatars. |
| `recording.py` | Record LIVE video; requires a working FFmpeg installation. |
| `proxying.py` | Configure HTTP and WebSocket proxies. |
| `logged_in.py` | Connect with an authenticated TikTok session. |
| `web_defaults.py` | Customize global HTTP and WebSocket defaults. |

## Authenticated sessions

An authenticated session is not required for ordinary public streams. Use one
only when the target content requires login, such as some age-restricted rooms.

Set all related values together:

```dotenv
TIKTOK_SESSION_ID=sessionid_cookie_value
TIKTOK_TARGET_IDC=tt_target_idc_cookie_value
WHITELIST_AUTHENTICATED_SESSION_ID_HOST=api.eulerstream.com
```

The application rejects a configuration where only one of
`TIKTOK_SESSION_ID` and `TIKTOK_TARGET_IDC` is set.

> [!CAUTION]
> A TikTok `sessionid` cookie grants access to the associated account. Never
> publish it. Allow it to be sent only to a signing host you trust.

## Operating the application

### Start a session

1. Activate `.venv`.
2. Run `py start.py`.
3. Open `http://127.0.0.1:5555`.
4. Save the target username in **Settings (.env)**.
5. Select **Connect** and wait for the `Connected` state.

### Change creators

1. Select **Disconnect**.
2. Update `TIKTOK_UNIQUE_ID` in the settings.
3. Save the settings.
4. Select **Connect** again.

Starting a new connection also stops the previous client before creating the
new one.

### Stop the application

Select **Disconnect**, return to the terminal, and press `Ctrl+C`. Values saved
in `.env` remain available for the next launch. The in-memory event history
does not persist after shutdown.

### Logging and diagnostics

Set `LOG_LEVEL=DEBUG`, save the configuration, and reconnect when diagnosing a
connection problem. Return to `INFO` during normal operation to reduce output.
Do not paste logs publicly without checking them for usernames, cookies, API
keys, or signed URLs.

## Troubleshooting

### `User is offline` or `That user is not currently live`

- Confirm the spelling of the username.
- Confirm that the account is LIVE at the moment of connection.
- Try the username with a leading `@`.

### `TIKTOK_UNIQUE_ID is missing`

Set the root `.env` value or save it through the Web UI:

```dotenv
TIKTOK_UNIQUE_ID=@username
```

### Connected but no comments, likes, or gifts appear

- Wait for a new interaction after the connection completes.
- Confirm that the UI reports `Connected`.
- Set `LOG_LEVEL=DEBUG`, save, and reconnect.
- Check the firewall, proxy configuration, and Internet connection.
- Remember that `ONLY_NEW_COMMENTS=true` intentionally removes old comments
  delivered immediately after connecting.

### Signing-service or rate-limit error

- Verify `SIGN_API_URL=https://api.eulerstream.com`.
- Retry later if the service is limiting requests.
- Configure a valid Euler Stream `SIGN_API_KEY` if you have one.

### Session configuration error

Set both `TIKTOK_SESSION_ID` and `TIKTOK_TARGET_IDC`, or clear both. Verify that
`WHITELIST_AUTHENTICATED_SESSION_ID_HOST` names only the trusted signing host.

### The virtual environment points to a removed Python installation

Delete or rename the broken `.venv`, then recreate it:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

### The Web UI does not open

Confirm that the terminal contains a line similar to:

```text
Running on http://127.0.0.1:5555
```

If another application already uses port 5555, change `port=5555` at the end
of `examples/web-ui/service.py`, then use the new port in the browser and any
connected extension.

### PowerShell cannot activate `.venv`

Use a process-scoped execution policy, which resets when the terminal closes:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Project layout

```text
TikTokLive-master/
|-- TikTokLive/                 Core Python client, events, protocol, and routes
|-- examples/
|   |-- web-ui/                 Flask service and browser interface
|   |-- env_config.py           Shared example configuration
|   `-- *.py                    Runnable client examples
|-- scripts/
|   |-- ensure_dependencies.py  Installs missing runtime dependencies
|   `-- proto/                  Protocol generation tools
|-- tests/                      Automated tests
|-- start.py                    Local Web UI entry point
|-- pyproject.toml              Package metadata and dependencies
|-- .env                        Local configuration; do not publish secrets
`-- README.md                   This documentation
```

## Upstream documentation and community

- [Original source repository](https://github.com/isaackogan/TikTokLive)
- [Official upstream documentation](https://isaackogan.github.io/TikTokLive/)
- [Upstream examples](https://github.com/isaackogan/TikTokLive/tree/master/examples)
- [Upstream issue tracker](https://github.com/isaackogan/TikTokLive/issues)
- [TikTokLive Discord community](https://discord.gg/e2XwPNTBBr)
- [Euler Stream production WebSocket API](https://www.eulerstream.com/websockets)

For alternative languages, see
[TikTok-Live-Connector](https://github.com/zerodytrash/TikTok-Live-Connector)
for Node.js,
[TikTok-Live-Java](https://github.com/jwdeveloper/TikTok-Live-Java) for Java,
[TikTokLiveSharp](https://github.com/frankvHoof93/TikTokLiveSharp) for C#,
[gotiktoklive](https://github.com/steampoweredtaco/gotiktoklive) for Go, and
[TikTokLiveRust](https://github.com/jwdeveloper/TikTokLiveRust) for Rust.

## License and credits

This project is distributed under the modified AGPL license in
[LICENSE](LICENSE). Review the full license before distributing, modifying, or
offering the software as a service.

- **Isaac Kogan** — creator, primary upstream maintainer, and reverse
  engineering. [GitHub](https://github.com/isaackogan)
- **Zerody** — creator of the Node.js library and early TikTok LIVE scraping
  work. [GitHub](https://github.com/zerodytrash)
- **Kendykim** — local Web UI, operation workflow, configuration, updated
  examples, and documentation for this modified distribution.

See the upstream
[contributors list](https://github.com/isaackogan/TikTokLive/contributors) for
everyone who has contributed to the original project.
