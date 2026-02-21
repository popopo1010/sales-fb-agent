"""Slack /fb モーダルのブロック定義とパース"""

from __future__ import annotations

from .models import CandidateData


def get_modal_blocks() -> list[dict]:
    """モーダルの blocks を返す（書き起こし・候補者名・担当者名のみ）"""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "初回面談の書き起こしを貼り付けてください。FBが生成され、#dk_ca_初回面談fb に送信されます。担当者（あなた）へのメンションと候補者名が自動で付きます。",
            },
        },
        {
            "type": "input",
            "block_id": "transcript_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "transcript_input",
                "multiline": True,
                "placeholder": {"type": "plain_text", "text": "あ、もしもしー、〇〇様のお電話で..."},
            },
            "label": {"type": "plain_text", "text": "書き起こし"},
        },
        {
            "type": "input",
            "block_id": "candidate_name_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "candidate_name_input",
                "placeholder": {"type": "plain_text", "text": "例: 山田太郎"},
            },
            "label": {"type": "plain_text", "text": "候補者名（任意）"},
            "optional": True,
        },
        {
            "type": "input",
            "block_id": "ca_person_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "ca_person_input",
                "placeholder": {"type": "plain_text", "text": "例: 山田"},
            },
            "label": {"type": "plain_text", "text": "担当者名（任意）"},
            "optional": True,
        },
    ]


def parse_modal_values(view: dict) -> CandidateData:
    """モーダルの values から CandidateData を取得"""
    state = view.get("state") or {}
    values = state.get("values") or {}

    def _get_val(block_id: str, action_id: str) -> str:
        block = values.get(block_id) or {}
        elem = block.get(action_id) or {}
        v = elem.get("value")
        return v.strip() if isinstance(v, str) else ""

    return CandidateData(
        transcript=_get_val("transcript_block", "transcript_input"),
        candidate_name=_get_val("candidate_name_block", "candidate_name_input"),
        ca_person=_get_val("ca_person_block", "ca_person_input"),
    )
