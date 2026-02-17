#!/usr/bin/env python3
"""
営業FBエージェント - Slackアプリ

Slack で /fb と入力するとモーダルが開く。候補者名（任意）と書き起こしを入力して送信すると、
担当者へのメンション＋候補者名付きでFBを生成し #dk_ca_初回面談fb に投稿する。

使い方:
  python -m src.slack_app

環境変数:
  SLACK_BOT_TOKEN        - Bot User OAuth Token (xoxb-...)
  SLACK_SIGNING_SECRET   - Signing Secret
  SLACK_APP_TOKEN        - Socket Mode 用 (xapp-...)
  ANTHROPIC_API_KEY または OPENAI_API_KEY
  SLACK_CHANNEL          - FB送信先 (デフォルト: C0AELMP88Q6)
"""

import os
import re
import sys
import threading
from pathlib import Path

# プロジェクトルートをパスに追加
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

_env_path = _project_root / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


def _escape_mrkdwn(text: str) -> str:
    """mrkdwnで < > & をエスケープ（改行は維持）"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _parse_modal_values(view: dict) -> tuple[str, str, str, str, str]:
    """モーダルの values から transcript, candidate_name, qualifications, experience, age を安全に取得。"""
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

    return transcript, candidate_name, ca_person, qualifications, experience, age, desired_salary


def _create_app() -> App:
    """App インスタンスを生成（環境変数チェック付き）"""
    token = os.environ.get("SLACK_BOT_TOKEN")
    signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
    if not token or not signing_secret:
        raise ValueError(
            "SLACK_BOT_TOKEN と SLACK_SIGNING_SECRET を .env に設定してください。"
        )
    return App(token=token, signing_secret=signing_secret)


def _run_fb_generation_and_post(
    transcript: str,
    channel_id: str,
    user_id: str,
    candidate_name: str = "",
    ca_person: str = "",
    qualifications: str = "",
    experience: str = "",
    age: str = "",
    desired_salary: str = "",
) -> None:
    """FB生成してSlackに投稿（バックグラウンド実行）"""
    from src.agent.generator import build_prompt, generate_feedback
    from src.slack.sender import _format_feedback_for_slack, _markdown_to_plain, _force_line_breaks

    token = os.environ.get("SLACK_BOT_TOKEN")
    client = __import__("slack_sdk").WebClient(token=token)

    try:
        prompt = build_prompt(transcript)
        feedback = generate_feedback(prompt, transcript=transcript)

        formatted = _format_feedback_for_slack(feedback)
        plain_text = _markdown_to_plain(formatted)
        plain_text = _force_line_breaks(plain_text)

        # ヘッダー: CAメンション + 候補者名（blocksのmrkdwnでメンションを有効化）
        header_parts = [f"<@{user_id}>"]
        if candidate_name:
            header_parts.append(f"候補者: {candidate_name}")
        header_mrkdwn = " ".join(header_parts)

        # FB送信先に投稿（blocksでメンションを確実に有効化）
        channel = (os.environ.get("SLACK_CHANNEL") or "C0AELMP88Q6").strip()
        if not channel:
            raise ValueError("SLACK_CHANNEL が .env に設定されていません。チャンネルID（例: C0AELMP88Q6）を設定してください。")
        full_text = header_mrkdwn + "\n\n" + plain_text  # 通知用フォールバック

        blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": header_mrkdwn}},
        ]
        # FB本文を項目ごとに分割し、区切り線で視認性向上（Slack 3000文字/block制限あり）
        sections = re.split(r"\n\n+(?=\d+\.\s*)", plain_text)
        chunk_size = 2900
        content_blocks_added = False
        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue
            content_blocks_added = True
            # 長い項目は文字数で分割（mrkdwn使用＝改行が反映される。plain_textは改行非対応）
            for j in range(0, len(section), chunk_size):
                chunk = section[j : j + chunk_size]
                blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": _escape_mrkdwn(chunk)}})
            # 項目間に区切り線を追加（最後の項目の後は不要）
            if i < len(sections) - 1:
                blocks.append({"type": "divider"})
        # フォールバック: セクション分割で本文が入らなかった場合は全文を1ブロックで
        if not content_blocks_added and plain_text:
            for j in range(0, len(plain_text), chunk_size):
                chunk = plain_text[j : j + chunk_size]
                blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": _escape_mrkdwn(chunk)}})

        client.chat_postMessage(channel=channel, text=full_text, blocks=blocks)

        # 元のチャンネルに完了通知（ephemeral）- チャンネルへのリンク付きで内容の場所を明示
        if channel_id and user_id:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=f"FBを <#{channel}> に送信しました。チャンネルで内容をご確認ください。",
            )

        # マスタに候補者情報を保存（概要は書き起こしからLLMで生成）
        try:
            from src.agent.generator import generate_transcript_summary
            from src.master.store import save_candidate_to_master
            summary = generate_transcript_summary(transcript)
            save_candidate_to_master(
                candidate=candidate_name,
                ca_person=ca_person,
                summary=summary,
                qualifications=qualifications,
                experience=experience,
                age=age,
                desired_salary=desired_salary,
            )
        except Exception:
            pass  # マスタ保存失敗はFB投稿に影響させない
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


def _build_app() -> App:
    """ルート付きのAppを構築"""
    app = _create_app()

    @app.command("/fb")
    def handle_fb_command(ack, body, client, logger):
        """ /fb でモーダルを開く """
        ack()

        import json
        channel_id = body.get("channel_id", "")
        private_metadata = json.dumps({"channel_id": channel_id, "user_id": body.get("user_id", "")})

        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "private_metadata": private_metadata,
                "type": "modal",
                "callback_id": "fb_submit",
                "title": {"type": "plain_text", "text": "営業FB生成"},
                "submit": {"type": "plain_text", "text": "FBを生成"},
                "close": {"type": "plain_text", "text": "キャンセル"},
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "初回面談の書き起こしを貼り付けてください。FBが生成され、#dk_ca_初回面談fb に送信されます。担当者（あなた）へのメンションと候補者名が自動で付きます。",
                        },
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
                        "label": {"type": "plain_text", "text": "CA担当者（任意・マスタに保存）"},
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "qualifications_block",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "qualifications_input",
                            "placeholder": {"type": "plain_text", "text": "例: 一級建築士、宅建"},
                        },
                        "label": {"type": "plain_text", "text": "保有資格（任意・マスタに保存）"},
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "experience_block",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "experience_input",
                            "placeholder": {"type": "plain_text", "text": "例: 建築設計5年、施工管理3年"},
                        },
                        "label": {"type": "plain_text", "text": "経験（任意・マスタに保存）"},
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "age_block",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "age_input",
                            "placeholder": {"type": "plain_text", "text": "例: 35歳"},
                        },
                        "label": {"type": "plain_text", "text": "年齢（任意・マスタに保存）"},
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "desired_salary_block",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "desired_salary_input",
                            "placeholder": {"type": "plain_text", "text": "例: 600万円"},
                        },
                        "label": {"type": "plain_text", "text": "希望年収（任意・マスタに保存）"},
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "transcript_block",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "transcript_input",
                            "multiline": True,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "あ、もしもしー、〇〇様のお電話で...",
                            },
                        },
                        "label": {"type": "plain_text", "text": "書き起こし"},
                    },
                ],
            },
        )

    @app.view("fb_submit")
    def handle_fb_submission(ack, body, view, client, logger):
        """ モーダル送信時: 即座にackし、バックグラウンドでFB生成 """
        ack()

        transcript, candidate_name, ca_person, qualifications, experience, age, desired_salary = _parse_modal_values(view)
        if not transcript:
            return

        import json
        metadata = json.loads(view.get("private_metadata") or "{}")
        channel_id = metadata.get("channel_id") or ""
        user_id = metadata.get("user_id") or (body.get("user") or {}).get("id") or ""

        thread = threading.Thread(
            target=_run_fb_generation_and_post,
            args=(transcript, channel_id, user_id),
            kwargs={
                "candidate_name": candidate_name,
                "ca_person": ca_person,
                "qualifications": qualifications,
                "experience": experience,
                "age": age,
                "desired_salary": desired_salary,
            },
        )
        thread.daemon = True
        thread.start()

        logger.info("FB生成をバックグラウンドで開始しました")

    return app


def main():
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token:
        print(
            "[ERROR] SLACK_APP_TOKEN (xapp-...) が設定されていません。\n"
            "Socket Mode を使うには api.slack.com でアプリを作成し、"
            "Socket Mode を有効にして App-Level Token を取得してください。\n"
            "手順は docs/13-slack-deployment-guide.md を参照してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        app = _build_app()
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    handler = SocketModeHandler(app, app_token)
    print("[INFO] Slack アプリを起動しました。チャンネルで /fb を試してください。")
    handler.start()


if __name__ == "__main__":
    main()
