"""Shared environment configuration for runnable examples."""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def get_unique_id() -> str:
    """Return the configured TikTok username or fail with a useful message."""
    unique_id = os.getenv("TIKTOK_UNIQUE_ID", "").strip()
    if not unique_id:
        raise RuntimeError("TIKTOK_UNIQUE_ID is missing. Set it in the project .env file.")
    return unique_id


def get_session() -> tuple[str, str] | None:
    """Return optional TikTok authentication cookies from the environment."""
    session_id = os.getenv("TIKTOK_SESSION_ID", "").strip()
    target_idc = os.getenv("TIKTOK_TARGET_IDC", "").strip()
    if bool(session_id) != bool(target_idc):
        raise RuntimeError("Set both TIKTOK_SESSION_ID and TIKTOK_TARGET_IDC, or leave both blank.")
    return (session_id, target_idc) if session_id else None
