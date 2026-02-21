"""Slack Bolt アプリのエントリポイント"""

import json
import logging
import os
import sys
import threading
from pathlib import Path

# プロジェクトルートを sys.path に追加（直接実行時のimport解決用）
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.utils.loader import load_env
load_env()

from src.config import setup_logging
setup_logging()

logger = logging.getLogger(__name__)

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .modal import get_modal_blocks, parse_modal_values
from .poster import run_fb_generation_and_post


def _create_app() -> App:
    token = os.environ.get("SLACK_BOT_TOKEN")
    signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
    if not token or not signing_secret:
        raise ValueError("SLACK_BOT_TOKEN と SLACK_SIGNING_SECRET を .env に設定してください。")
    return App(token=token, signing_secret=signing_secret)


def _build_app() -> App:
    app = _create_app()

    @app.command("/fb")
    def handle_fb_command(ack, body, client, logger):
        ack()
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
                "blocks": get_modal_blocks(),
            },
        )

    @app.view("fb_submit")
    def handle_fb_submission(ack, body, view, client, logger):
        ack()
        data = parse_modal_values(view)
        if not data.transcript:
            return

        metadata = json.loads(view.get("private_metadata") or "{}")
        channel_id = metadata.get("channel_id") or ""
        user_id = metadata.get("user_id") or (body.get("user") or {}).get("id") or ""

        thread = threading.Thread(
            target=run_fb_generation_and_post,
            args=(data, channel_id, user_id),
        )
        thread.daemon = True
        thread.start()
        logger.info("FB生成をバックグラウンドで開始しました")

    return app


def main() -> None:
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token:
        logger.error(
            "SLACK_APP_TOKEN (xapp-...) が設定されていません。\n"
            "Socket Mode を使うには api.slack.com でアプリを作成し、"
            "Socket Mode を有効にして App-Level Token を取得してください。\n"
            "手順は docs/13-slack-deployment-guide.md を参照してください。"
        )
        sys.exit(1)

    try:
        app = _build_app()
    except ValueError as e:
        logger.error("%s", e)
        sys.exit(1)

    handler = SocketModeHandler(app, app_token)
    logger.info("Slack アプリを起動しました。チャンネルで /fb を試してください。")
    handler.start()
