"""Slack送信 - Bot API / Incoming Webhook 対応"""

import json
import os
import re
from pathlib import Path

from src.utils.loader import get_project_root


def _format_feedback_for_slack(text: str) -> str:
    """FBの視認性向上：項目間の空行・各項目内の改行を正規化"""
    result = text
    # 各 ### 見出し（1.〜9.）の前に空行を確保（連続空行でない限り）
    result = re.sub(r"(?<!\n\n)(\n)(### \d+\.)", r"\n\n\2", result)
    # 箇条書きが1行に複数詰まっている場合を分離（。・ や 。- のパターン）
    result = re.sub(r"([。])\s*([・\-]\s+)", r"\1\n\2", result)
    return result.strip()


def _markdown_to_plain(text: str) -> str:
    """Markdownをプレーンテキストに変換（Slackでマークダウン表示されないように）"""
    result = text
    # ### 見出し → 見出し
    result = re.sub(r"^#{1,6}\s*", "", result, flags=re.MULTILINE)
    # **太字** / __太字__ → 太字
    result = re.sub(r"\*\*(.+?)\*\*", r"\1", result)
    result = re.sub(r"__(.+?)__", r"\1", result)
    result = re.sub(r"\*(.+?)\*", r"\1", result)
    result = re.sub(r"_(.+?)_", r"\1", result)
    # - 箇条書き を ・ に統一（行頭のみ）
    result = re.sub(r"^[\-\*]\s+", "・ ", result, flags=re.MULTILINE)
    return result


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
    channel = channel or os.environ.get("SLACK_CHANNEL", "#dk_ca_fb")

    if not save_only:
        # 視認性向上のフォーマット調整 → Markdownをプレーンテキストに変換
        formatted = _format_feedback_for_slack(text)
        plain_text = _markdown_to_plain(formatted)
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
    print(f"[INFO] Slack未設定のため、FBをファイルに保存しました: {save_path}")
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
        print(f"[ERROR] Slack Webhook 送信失敗: {e}")
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
        print(f"[ERROR] Slack API 送信失敗: {e.response.get('error', e)}")
        return False
