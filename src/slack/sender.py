"""Slack送信 - Bot API / Incoming Webhook 対応"""

import json
import os
import re
from pathlib import Path

from src.utils.loader import get_project_root


def _format_feedback_for_slack(text: str) -> str:
    """FBの視認性向上：項目間の空行・各項目内の改行を正規化"""
    result = text
    # 全体評価：スコアの直後に空行を確保
    result = re.sub(r"(### 全体評価：[\d\-]/10点)\s*", r"\1\n\n", result)
    # 各 ### 見出し（1.〜9.）の前に2行空けを確保
    result = re.sub(r"\n+(### \d+\.)", r"\n\n\n\1", result)
    # 見出しの直後にも改行を入れる
    result = re.sub(r"(### \d+\.[^\n]*)(\n)(?=[^\n])", r"\1\n\n", result)
    # 箇条書きが1行に複数詰まっている場合を分離（。・ や 。- のパターン）
    result = re.sub(r"([。])\s*([・\-]\s+)", r"\1\n\2", result)
    # ）や。の直後の ・ または ①②③ で改行（語句内の・は対象外）
    result = re.sub(r"([。）)])\s*([・·•①②③④⑤⑥⑦⑧⑨⑩])", r"\1\n\2", result)
    # 行中の「- 」も箇条書きとして改行
    result = re.sub(r"([。】])\s*(-\s+)", r"\1\n\2", result)
    # 箇条書きの各要素の後に改行を確保
    result = re.sub(r"(^[・\-]\s+[^\n]+)(\n)(?=[^・\-])", r"\1\n\n", result, flags=re.MULTILINE)
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


def _force_line_breaks(text: str) -> str:
    """最終チェック：・や①②③の前で確実に改行する"""
    result = text
    # 「・ 」（・+スペース）の前で改行＝箇条書きの区切り。語句内の「チャンス・定年」は・の直後に文字が来るので対象外
    result = re.sub(r"([^\n])([・·•]\s+)", r"\1\n\2", result)
    # ）や。の直後の ①②③ で改行
    result = re.sub(r"([。）)])\s*([①②③④⑤⑥⑦⑧⑨⑩])", r"\1\n\2", result)
    # 「〇〇した点・」「〇〇不足・」等、文末語の直後の ・ で改行
    result = re.sub(r"(点|不足|必要|ある|整理)\s*([・·•])\s*", r"\1\n\2 ", result)
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
    channel = (channel or os.environ.get("SLACK_CHANNEL") or "C0AELMP88Q6").strip()

    if not save_only:
        # 視認性向上のフォーマット調整 → Markdownをプレーンテキストに変換 → 改行強制
        formatted = _format_feedback_for_slack(text)
        plain_text = _markdown_to_plain(formatted)
        plain_text = _force_line_breaks(plain_text)
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
