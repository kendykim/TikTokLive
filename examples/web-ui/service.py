"""
Minimal web UI example.

A Flask backend that connects a TikTokLiveClient to a livestream and
streams Comment/Gift/Like events to the browser over Server-Sent Events
(SSE), paired with a static index.html that renders them as a live feed.

Run:
    py start.py

Then open http://localhost:5555 and enter a "@username" to connect.
"""
import asyncio
from collections import deque
import json
import os
import queue
import threading
import time
from pathlib import Path
from typing import Optional

from flask import Flask, Response, jsonify, request, send_from_directory
from dotenv import dotenv_values, load_dotenv, set_key

try:
    from markdown import markdown
except ModuleNotFoundError as ex:
    raise SystemExit(
        "Missing Python dependency 'markdown'. Activate the project's virtual environment, "
        "then run: python -m pip install -e ."
    ) from ex

from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.client.errors import UserOfflineError
from TikTokLive.events import CommentEvent, ConnectEvent, DisconnectEvent, GiftEvent, LikeEvent

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
GUIDE_FILES = {
    "vi": PROJECT_ROOT / "tailieucachsudung.md",
    "en": PROJECT_ROOT / "tailieucachsudung.en.md",
    "zh": PROJECT_ROOT / "tailieucachsudung.zh.md",
}
PUBLIC_ENV_KEYS = {
    "TIKTOK_UNIQUE_ID",
    "ONLY_NEW_COMMENTS",
    "LOG_LEVEL",
    "SIGN_API_URL",
    "SIGN_SERVER_MESSAGE_DISABLED",
    "SEND_DEPRECATION_WARNINGS",
    "WHITELIST_AUTHENTICATED_SESSION_ID_HOST",
}
SECRET_ENV_KEYS = {"SIGN_API_KEY", "TIKTOK_SESSION_ID", "TIKTOK_TARGET_IDC"}

load_dotenv(ENV_PATH)
app = Flask(__name__, static_folder=None)


@app.after_request
def allow_extension_api_requests(response: Response):
    if request.path.startswith("/api/"):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
        response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

_subscribers: set["queue.Queue[dict]"] = set()
_subscribers_lock = threading.Lock()
_event_history: deque[dict] = deque(maxlen=500)
_event_sequence: int = 0
_client: Optional[TikTokLiveClient] = None
_thread: Optional[threading.Thread] = None
_lock = threading.Lock()
_connection_state: str = "disconnected"
_connection_username: str = ""
_connection_error: str = ""
_live_session_id: str = ""


def _emit(event_type: str, **payload) -> None:
    global _event_sequence
    with _subscribers_lock:
        _event_sequence = max(_event_sequence + 1, time.time_ns() // 1_000_000)
        message = {"id": _event_sequence, "type": event_type, "ts": time.time(), **payload}
        _event_history.append(message)
        subscribers = tuple(_subscribers)
    for subscriber in subscribers:
        subscriber.put(message)


def _build_client(username: str) -> TikTokLiveClient:
    client = TikTokLiveClient(unique_id=username)

    session_id = os.getenv("TIKTOK_SESSION_ID", "").strip()
    target_idc = os.getenv("TIKTOK_TARGET_IDC", "").strip()
    if bool(session_id) != bool(target_idc):
        raise ValueError("Set both TIKTOK_SESSION_ID and TIKTOK_TARGET_IDC, or clear both.")
    if session_id and target_idc:
        client.web.set_session(session_id, target_idc)

    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        global _connection_state, _connection_username, _connection_error, _live_session_id
        _connection_state = "connected"
        _connection_username = event.unique_id
        _connection_error = ""
        _live_session_id = f"{event.unique_id}:{event.room_id}"
        _emit("connect", username=event.unique_id, session_id=_live_session_id)

    @client.on(DisconnectEvent)
    async def on_disconnect(_: DisconnectEvent):
        global _connection_state
        _connection_state = "disconnected"
        _emit("disconnect")

    @client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        _emit("comment", user=event.user.nickname, comment=event.comment)

    @client.on(GiftEvent)
    async def on_gift(event: GiftEvent):
        if event.gift is None:
            return
        # Wait for a streakable gift's streak to finish before showing it,
        # otherwise every repeat in the streak prints its own line.
        if event.gift.streakable and event.streaking:
            return

        viewer_name = "Người xem"
        viewer_username = ""
        if event.user is not None:
            viewer_name = event.user.nickname or event.user.unique_id or viewer_name
            viewer_username = event.user.unique_id or ""

        _emit(
            "gift",
            user=viewer_name,
            username=viewer_username,
            gift=event.gift.name,
            count=event.repeat_count,
        )

    @client.on(LikeEvent)
    async def on_like(event: LikeEvent):
        _emit("like", user=event.user.nickname, count=event.count, total=event.total)

    return client


def _run_client(client: TikTokLiveClient) -> None:
    global _connection_state, _connection_error
    try:
        client.run()
    except UserOfflineError:
        _connection_state = "error"
        _connection_error = "That user is not currently live."
        _emit("error", message=_connection_error)
    except Exception as ex:
        _connection_state = "error"
        _connection_error = str(ex)
        _emit("error", message=_connection_error)


def _stop_current_client() -> None:
    global _client, _thread, _connection_state

    if _client is None:
        return

    # client.run() blocks inside an event loop owned by the background
    # thread, so disconnecting from the Flask request thread has to be
    # scheduled onto that same loop rather than awaited directly here.
    asyncio.run_coroutine_threadsafe(_client.disconnect(), _client._asyncio_loop)
    _thread.join(timeout=5)
    _client = None
    _thread = None
    _connection_state = "disconnected"


@app.post("/api/connect")
def connect():
    global _client, _thread, _connection_state, _connection_username, _connection_error

    username = (request.get_json(silent=True) or {}).get("username", "").strip()
    username = username or os.getenv("TIKTOK_UNIQUE_ID", "").strip()
    if not username:
        return jsonify({"error": "username is required"}), 400

    with _lock:
        _stop_current_client()
        try:
            _client = _build_client(username)
        except ValueError as ex:
            return jsonify({"error": str(ex)}), 400
        _connection_state = "connecting"
        _connection_username = username.lstrip("@")
        _connection_error = ""
        _thread = threading.Thread(target=_run_client, args=(_client,), daemon=True)
        _thread.start()

    return jsonify({"status": "connecting", "username": username})


@app.post("/api/disconnect")
def disconnect():
    with _lock:
        _stop_current_client()

    return jsonify({"status": "disconnected"})


@app.get("/api/status")
def connection_status():
    response = jsonify({
        "status": _connection_state,
        "username": _connection_username,
        "error": _connection_error,
        "session_id": _live_session_id,
    })
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/api/events")
def events_since():
    try:
        since_id = int(request.args.get("since", "0"))
    except (TypeError, ValueError):
        return jsonify({"error": "since must be an integer"}), 400

    with _subscribers_lock:
        events = [event for event in _event_history if event["id"] > since_id]
        latest_id = _event_sequence
    return jsonify({"events": events, "latest_id": latest_id})


@app.get("/api/config")
def get_config():
    values = dotenv_values(ENV_PATH)
    return jsonify({
        "values": {key: values.get(key, "") or "" for key in sorted(PUBLIC_ENV_KEYS)},
        "secretConfigured": {
            key: bool(values.get(key, "")) for key in sorted(SECRET_ENV_KEYS)
        },
    })


@app.get("/api/guide")
def get_guide():
    language = request.args.get("lang", "en").lower()
    guide_path = GUIDE_FILES.get(language, GUIDE_FILES["en"])
    try:
        source = guide_path.read_text(encoding="utf-8")
        rendered = markdown(
            source,
            extensions=["fenced_code", "tables", "sane_lists", "toc"],
            output_format="html5",
        )
        return Response(rendered, mimetype="text/html")
    except OSError:
        return jsonify({"error": "Guide file is unavailable."}), 404


@app.put("/api/config")
def update_config():
    payload = request.get_json(silent=True) or {}
    values = payload.get("values", {})
    clear_secrets = set(payload.get("clearSecrets", []))

    if not isinstance(values, dict) or not clear_secrets <= SECRET_ENV_KEYS:
        return jsonify({"error": "Invalid configuration payload."}), 400

    unknown_keys = set(values) - PUBLIC_ENV_KEYS - SECRET_ENV_KEYS
    if unknown_keys:
        return jsonify({"error": f"Unsupported variables: {', '.join(sorted(unknown_keys))}"}), 400

    ENV_PATH.touch(exist_ok=True)
    for key, raw_value in values.items():
        value = str(raw_value).strip()
        # Blank password fields preserve existing secrets.
        if key in SECRET_ENV_KEYS and not value:
            continue
        set_key(str(ENV_PATH), key, value, quote_mode="never")
        os.environ[key] = value

    for key in clear_secrets:
        set_key(str(ENV_PATH), key, "", quote_mode="never")
        os.environ.pop(key, None)

    return jsonify({"status": "saved"})


@app.get("/api/stream")
def stream():
    subscriber: "queue.Queue[dict]" = queue.Queue()
    with _subscribers_lock:
        query_since = request.args.get("since", "0")
        header_since = request.headers.get("Last-Event-ID", "0")
        try:
            since_id = max(int(query_since), int(header_since))
        except (TypeError, ValueError):
            since_id = 0
        replay = [event for event in _event_history if event["id"] > since_id] if since_id else []
        _subscribers.add(subscriber)

    def generate():
        try:
            # An initial SSE comment flushes headers and confirms the connection.
            yield ": connected\n\n"
            for event in replay:
                yield f"id: {event['id']}\ndata: {json.dumps(event)}\n\n"
            while True:
                event = subscriber.get()
                yield f"id: {event['id']}\ndata: {json.dumps(event)}\n\n"
        finally:
            with _subscribers_lock:
                _subscribers.discard(subscriber)

    response = Response(generate(), mimetype="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@app.get("/")
def index():
    return send_from_directory(Path(__file__).parent, "index.html")


@app.get("/assets/logo.png")
def logo():
    return send_from_directory(Path(__file__).parent, "logo.png")


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5555,
        debug=False,
        threaded=True,
        use_reloader=False,
    )
