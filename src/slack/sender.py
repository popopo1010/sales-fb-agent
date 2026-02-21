"""Slack送信 - Bot API / Incoming Webhook 対応"""

import json
import logging
import os
from pathlib import Path

from src.config import DEFAULT_SLACK_CHANNEL
from src.slack.formatting import format_feedback_to_plain
from src.utils.loader import get_project_root

logger = logging.getLogger(__name__)


def send_feedback(
    text: str,
    channel: str | None = None,
    save_path: str | Path | None = None,
    save_only: bool = False,
) -> bool:
    """
    FBをSlackに送信する。
    save_only=True の場合はSlack送信をスキップし、ファイルに保存する。
    SLACK_WEBHOOK_URL があれば Webhook、SLACK_BOT_TOKEN があれば Bot API を使用。
    どちらもなければ save_path に保存（指定がなければ data/feedback/ に保存）。
    """
    channel = (channel or os.environ.get("SLACK_CHANNEL") or DEFAULT_SLACK_CHANNEL).strip()

    if not save_only:
        plain_text = format_feedback_to_plain(text)
        # Incoming Webhook
        webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
        if webhook_url:
            return _send_via_webhook(webhook_url, plain_text)

        # Bot Token
        token = os.environ.get("SLACK_BOT_TOKEN")
        if token:
            return _send_via_api(token, plain_text, channel)

    # フォールバック: ファイルに保存
    root = get_project_root()
    if save_path is None:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        save_path = root / "data" / "feedback" / f"fb_{timestamp}.md"
    else:
        save_path = Path(save_path)
        if not save_path.is_absolute():
            save_path = root / save_path

    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(text, encoding="utf-8")
    logger.info("Slack未設定のため、FBをファイルに保存しました: %s", save_path)
    return True


def _send_via_webhook(webhook_url: str, text: str) -> bool:
    """Incoming Webhook で送信"""
    import urllib.request

    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status == 200
    except Exception as e:
        logger.error("Slack Webhook 送信失敗: %s", e)
        return False


def _send_via_api(token: str, text: str, channel: str) -> bool:
    """Slack Bot API で送信"""
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    client = WebClient(token=token)
    try:
        client.chat_postMessage(channel=channel, text=text)
        return True
    except SlackApiError as e:
        logger.error("Slack API 送信失敗: %s", e.response.get("error", e))
        return False
