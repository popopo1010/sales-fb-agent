"""FB生成・Slack投稿・マスタ保存"""

import os
import re
from slack_sdk import WebClient

from .models import CandidateData

DEFAULT_CHANNEL = "C0AELMP88Q6"
CHUNK_SIZE = 2900


def _escape_mrkdwn(text: str) -> str:
    """mrkdwnで < > & をエスケープ"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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
    from src.agent.generator import build_prompt, generate_feedback, generate_transcript_summary
    from src.slack.sender import _format_feedback_for_slack, _markdown_to_plain, _force_line_breaks
    from src.master.store import save_candidate_to_master

    token = os.environ.get("SLACK_BOT_TOKEN")
    client = WebClient(token=token)
    channel = (os.environ.get("SLACK_CHANNEL") or DEFAULT_CHANNEL).strip()

    try:
        prompt = build_prompt(data.transcript)
        feedback = generate_feedback(prompt, transcript=data.transcript)

        formatted = _format_feedback_for_slack(feedback)
        plain_text = _markdown_to_plain(formatted)
        plain_text = _force_line_breaks(plain_text)

        header_parts = [f"<@{user_id}>"]
        if data.candidate_name:
            header_parts.append(f"候補者: {data.candidate_name}")
        header_mrkdwn = " ".join(header_parts)
        full_text = header_mrkdwn + "\n\n" + plain_text

        blocks = _build_slack_blocks(header_mrkdwn, plain_text)
        client.chat_postMessage(channel=channel, text=full_text, blocks=blocks)

        if channel_id and user_id:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=f"FBを <#{channel}> に送信しました。チャンネルで内容をご確認ください。",
            )

        try:
            summary = generate_transcript_summary(data.transcript)
            save_candidate_to_master(summary=summary, **data.to_master_kwargs())
        except Exception:
            pass
    except Exception as e:
        if channel_id and user_id:
            try:
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text=f"FB生成中にエラーが発生しました: {str(e)}",
                )
            except Exception:
                pass
