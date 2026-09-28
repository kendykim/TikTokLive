from env_config import get_session, get_unique_id
from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent

client: TikTokLiveClient = TikTokLiveClient(
    unique_id=get_unique_id()
)


@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    client.logger.info(f"Connected to @{event.unique_id}!")


if __name__ == '__main__':
    # Enable download info
    client.logger.setLevel(LogLevel.INFO.value)

    # Set the login session ID token BEFORE connecting. Both the
    # `sessionid` cookie and the `tt-target-idc` cookie (data-center hint)
    # are required — you can read both off your browser's TikTok cookies.
    session = get_session()
    if not session:
        raise RuntimeError(
            "logged_in.py requires TIKTOK_SESSION_ID and TIKTOK_TARGET_IDC in .env."
        )
    client.web.set_session(*session)

    # Connect
    client.run()
