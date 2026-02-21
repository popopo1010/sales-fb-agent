"""FB生成・Slack投稿・マスタ保存"""

import logging
import os
import re
from datetime import datetime
from pathlib import Path

from slack_sdk import WebClient

from src.config import DEFAULT_SLACK_CHANNEL
from src.slack.formatting import format_feedback_to_plain
from src.utils.loader import get_project_root
from .models import CandidateData

logger = logging.getLogger(__name__)

CHUNK_SIZE = 2900


def _escape_mrkdwn(text: str) -> str:
    """mrkdwnで < > & をエスケープ"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _save_fb_to_file(feedback: str, candidate_name: str) -> Path | None:
    """FB本文を data/feedback/ に保存。候補者名を含むファイル名で保存。"""
    root = get_project_root()
    feedback_dir = root / "data" / "feedback"
    feedback_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^\w\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]", "_", candidate_name or "unknown")[:30]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    path = feedback_dir / f"fb_{safe_name}_{timestamp}.md"
    path.write_text(feedback, encoding="utf-8")
    return path


def _post_ephemeral(client: WebClient, channel_id: str, user_id: str, channel: str, text: str) -> None:
    """ユーザーにのみ表示されるメッセージを送信"""
    if client and channel_id and user_id:
        try:
            client.chat_postEphemeral(channel=channel_id, user=user_id, text=text)
        except Exception:
            logger.warning("ephemeral送信に失敗", exc_info=True)


def _save_fb_and_master(data: CandidateData, feedback: str) -> None:
    """FBをファイル保存し、マスタに追記"""
    try:
        _save_fb_to_file(feedback, data.candidate_name or "")
    except Exception:
        logger.warning("FB保存に失敗", exc_info=True)
    try:
        from src.agent.generator import generate_transcript_summary
        from src.master.store import save_candidate_to_master

        summary = generate_transcript_summary(data.transcript)
        save_candidate_to_master(summary=summary, **data.to_master_kwargs())
    except Exception:
        logger.warning("マスタ保存に失敗", exc_info=True)


def _build_slack_blocks(header_mrkdwn: str, plain_text: str) -> list[dict]:
    """FB本文をSlack blocksに変換"""
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": header_mrkdwn}}]
    sections = re.split(r"\n\n+(?=\d+\.\s*)", plain_text)
    content_added = False
    for i, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue
        content_added = True
        for j in range(0, len(section), CHUNK_SIZE):
            chunk = section[j : j + CHUNK_SIZE]
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": _escape_mrkdwn(chunk)}})
        if i < len(sections) - 1:
            blocks.append({"type": "divider"})
    if not content_added and plain_text:
        for j in range(0, len(plain_text), CHUNK_SIZE):
            chunk = plain_text[j : j + CHUNK_SIZE]
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": _escape_mrkdwn(chunk)}})
    return blocks


def run_fb_generation_and_post(data: CandidateData, channel_id: str, user_id: str) -> None:
    """FB生成→Slack投稿→マスタ保存"""
    from src.agent.generator import build_prompt, generate_feedback

    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        logger.error("SLACK_BOT_TOKEN が設定されていないため、FB投稿できません")
        return
    client = WebClient(token=token)
    channel = (os.environ.get("SLACK_CHANNEL") or DEFAULT_SLACK_CHANNEL).strip()

    try:
        prompt = build_prompt(data.transcript)
        feedback = generate_feedback(prompt, transcript=data.transcript)
        plain_text = format_feedback_to_plain(feedback)

        header_parts = [f"<@{user_id}>"]
        if data.candidate_name:
            header_parts.append(f"候補者: {data.candidate_name}")
        header_mrkdwn = " ".join(header_parts)
        full_text = header_mrkdwn + "\n\n" + plain_text

        blocks = _build_slack_blocks(header_mrkdwn, plain_text)
        client.chat_postMessage(channel=channel, text=full_text, blocks=blocks)

        _post_ephemeral(client, channel_id, user_id, channel, f"FBを <#{channel}> に送信しました。チャンネルで内容をご確認ください。")

        _save_fb_and_master(data, feedback)
    except Exception as e:
        _post_ephemeral(client, channel_id, user_id, channel, f"FB生成中にエラーが発生しました: {str(e)}")
