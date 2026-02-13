#!/usr/bin/env python3
"""
営業FBエージェント - Slackアプリ

Slack で /fb と入力するとモーダルが開き、書き起こしを貼り付けて送信すると
FBを生成して #dk_ca_fb に投稿する。

使い方:
  python -m src.slack_app

環境変数:
  SLACK_BOT_TOKEN        - Bot User OAuth Token (xoxb-...)
  SLACK_SIGNING_SECRET   - Signing Secret
  SLACK_APP_TOKEN        - Socket Mode 用 (xapp-...)
  ANTHROPIC_API_KEY または OPENAI_API_KEY
  SLACK_CHANNEL          - FB送信先 (デフォルト: #dk_ca_fb)
"""

import os
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
) -> None:
    """FB生成してSlackに投稿（バックグラウンド実行）"""
    from src.agent.generator import build_prompt, generate_feedback
    from src.slack.sender import _format_feedback_for_slack, _markdown_to_plain

    token = os.environ.get("SLACK_BOT_TOKEN")
    client = __import__("slack_sdk").WebClient(token=token)

    try:
        prompt = build_prompt(transcript)
        feedback = generate_feedback(prompt, transcript=transcript)

        formatted = _format_feedback_for_slack(feedback)
        plain_text = _markdown_to_plain(formatted)

        # #dk_ca_fb に投稿
        channel = os.environ.get("SLACK_CHANNEL", "#dk_ca_fb")
        client.chat_postMessage(channel=channel, text=plain_text)

        # 元のチャンネルに完了通知（ephemeral）
        if channel_id and user_id:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=f"FBを {channel} に送信しました。",
            )
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
                            "text": "初回面談の書き起こしを貼り付けてください。FBが生成され、#dk_ca_fb に送信されます。",
                        },
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

        values = view.get("state", {}).get("values", {})
        transcript_block = values.get("transcript_block", {})
        transcript_input = transcript_block.get("transcript_input", {})
        transcript = transcript_input.get("value", "").strip()

        if not transcript:
            return

        import json
        metadata = json.loads(view.get("private_metadata", "{}"))
        channel_id = metadata.get("channel_id", "")
        user_id = metadata.get("user_id", body.get("user", {}).get("id", ""))

        thread = threading.Thread(
            target=_run_fb_generation_and_post,
            args=(transcript, channel_id, user_id),
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
