import os
from datetime import datetime

from env_config import get_session, get_unique_id
from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, CommentEvent

client: TikTokLiveClient = TikTokLiveClient(
    unique_id=get_unique_id()
)

# Authentication is optional for public LIVE streams. If one session value is
# configured, require the matching data-centre value as well.
session = get_session()
if session:
    client.web.set_session(*session)

# If True, comments TikTok delivers as backlog (posted before this script
# connected) are dropped — only comments posted from here on are printed.
# TikTok still bursts a batch of recent comments right after connecting
# (this isn't something `process_connect_events` filters out), so we
# compare each comment's own timestamp against our connect time instead.
ONLY_NEW_COMMENTS: bool = os.getenv("ONLY_NEW_COMMENTS", "true").lower() in {"1", "true", "yes", "on"}
connected_at_ms: int = 0


@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    global connected_at_ms
    connected_at_ms = int(datetime.now().timestamp() * 1000)
    client.logger.info(f"Connected to @{event.unique_id}!")


@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    if ONLY_NEW_COMMENTS and event.common.create_time < connected_at_ms:
        return

    timestamp: str = datetime.fromtimestamp(event.common.create_time / 1000).strftime("%H:%M:%S")
    print(f"[{timestamp}] {event.user.nickname}-> {event.comment}")


if __name__ == '__main__':
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(LogLevel, log_level_name, LogLevel.INFO)
    client.logger.setLevel(log_level.value)

    # Connect
    client.run()
