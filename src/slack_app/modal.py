"""Slack /fb モーダルのブロック定義とパース"""

from .models import CandidateData

# モーダル入力ブロック定義: (block_id, action_id, label, placeholder, multiline)
_MODAL_FIELDS = [
    ("candidate_name_block", "candidate_name_input", "候補者名（任意）", "例: 山田太郎", False),
    ("ca_person_block", "ca_person_input", "CA担当者（任意・マスタに保存）", "例: 山田", False),
    ("qualifications_block", "qualifications_input", "保有資格（任意・マスタに保存）", "例: 一級建築士、宅建", False),
    ("experience_block", "experience_input", "経験（任意・マスタに保存）", "例: 建築設計5年、施工管理3年", False),
    ("age_block", "age_input", "年齢（任意・マスタに保存）", "例: 35歳", False),
    ("desired_salary_block", "desired_salary_input", "希望年収（任意・マスタに保存）", "例: 600万円", False),
    ("proposed_company_block", "proposed_company_input", "提案法人（任意・マスタに保存）", "例: 〇〇建設", False),
    ("appeal_to_needs_block", "appeal_to_needs_input", "ニーズへの訴求（任意・マスタに保存）", "ニーズに対して提案法人をどう訴求しているか", True),
    ("current_evaluation_block", "current_evaluation_input", "現在の評価（任意・マスタに保存）", "例: 候補者関心度高、次回面談調整中", True),
]


def get_modal_blocks() -> list[dict]:
    """モーダルの blocks を返す"""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "初回面談の書き起こしを貼り付けてください。FBが生成され、#dk_ca_初回面談fb に送信されます。担当者（あなた）へのメンションと候補者名が自動で付きます。",
            },
        },
    ]
    for block_id, action_id, label, placeholder, multiline in _MODAL_FIELDS:
        elem = {
            "type": "plain_text_input",
            "action_id": action_id,
            "placeholder": {"type": "plain_text", "text": placeholder},
        }
        if multiline:
            elem["multiline"] = True
        blocks.append({
            "type": "input",
            "block_id": block_id,
            "element": elem,
            "label": {"type": "plain_text", "text": label},
            "optional": True,
        })
    blocks.append({
        "type": "input",
        "block_id": "transcript_block",
        "element": {
            "type": "plain_text_input",
            "action_id": "transcript_input",
            "multiline": True,
            "placeholder": {"type": "plain_text", "text": "あ、もしもしー、〇〇様のお電話で..."},
        },
        "label": {"type": "plain_text", "text": "書き起こし"},
    })
    return blocks


def parse_modal_values(view: dict) -> CandidateData:
    """モーダルの values から CandidateData を取得"""
    state = view.get("state") or {}
    values = state.get("values") or {}

    def _get_val(block_id: str, action_id: str) -> str:
        block = values.get(block_id) or {}
        elem = block.get(action_id) or {}
        v = elem.get("value")
        return v.strip() if isinstance(v, str) else ""

    transcript = _get_val("transcript_block", "transcript_input")
    candidate_name = _get_val("candidate_name_block", "candidate_name_input")
    ca_person = _get_val("ca_person_block", "ca_person_input")
    qualifications = _get_val("qualifications_block", "qualifications_input")
    experience = _get_val("experience_block", "experience_input")
    age = _get_val("age_block", "age_input")
    desired_salary = _get_val("desired_salary_block", "desired_salary_input")
    proposed_company = _get_val("proposed_company_block", "proposed_company_input")
    appeal_to_needs = _get_val("appeal_to_needs_block", "appeal_to_needs_input")
    current_evaluation = _get_val("current_evaluation_block", "current_evaluation_input")

    return CandidateData(
        transcript=transcript,
        candidate_name=candidate_name,
        ca_person=ca_person,
        qualifications=qualifications,
        experience=experience,
        age=age,
        desired_salary=desired_salary,
        proposed_company=proposed_company,
        appeal_to_needs=appeal_to_needs,
        current_evaluation=current_evaluation,
    )
