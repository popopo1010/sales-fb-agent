#!/usr/bin/env python3
"""
営業FBエージェント - メインエントリポイント

初回面談の書き起こしからFBを生成し、Slack #dk_ca_初回面談fb に送信する。
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# プロジェクトルートを sys.path に追加（直接実行時のimport解決用）
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.utils.loader import load_env
load_env()

from src.config import setup_logging
setup_logging()

logger = logging.getLogger(__name__)

from src.agent.generator import build_prompt, generate_feedback
from src.slack.sender import send_feedback
from src.utils.loader import load_transcript


def run(
    input_path: str,
    channel: Optional[str] = None,
    output_only: bool = False,
    no_slack: bool = False,
) -> int:
    """
    書き起こしからFBを生成し、Slackに送信する。

    Args:
        input_path: 書き起こしファイルのパス
        channel: Slackチャンネル（未指定時は環境変数 SLACK_CHANNEL または #dk_ca_初回面談fb）
        output_only: True の場合、FBを標準出力に表示するのみ（Slack送信しない）
        no_slack: True の場合、Slackに送信せず data/feedback/ に保存

    Returns:
        終了コード（0: 成功, 1: エラー）
    """
    try:
        transcript = load_transcript(input_path)
    except FileNotFoundError as e:
        logger.error("%s", e)
        return 1

    logger.info("プロンプト構築中...")
    prompt = build_prompt(transcript)

    logger.info("FB生成中...")
    try:
        feedback = generate_feedback(prompt, transcript=transcript)
    except ValueError as e:
        logger.error("%s", e)
        logger.error("ヒント: .env ファイルを作成し、OPENAI_API_KEY を設定してください。")
        return 1
    except Exception as e:
        logger.error("LLM呼び出し失敗: %s", e)
        return 1

    if "フォールバック" in feedback:
        logger.info("APIクレジット不足のため、フォールバックFBで送信します。")

    if output_only:
        print("\n" + "=" * 60 + "\n")
        print(feedback)
        return 0

    if no_slack:
        send_feedback(feedback, save_only=True)
        return 0

    if send_feedback(feedback, channel=channel):
        logger.info("FBをSlackに送信しました。")
        return 0

    return 1


def main():
    parser = argparse.ArgumentParser(
        description="営業FBエージェント - 初回面談の書き起こしからFBを生成しSlackに送信"
    )
    parser.add_argument(
        "input",
        help="書き起こしファイルのパス",
    )
    parser.add_argument(
        "-c", "--channel",
        default=None,
        help="Slackチャンネル（例: #dk_ca_初回面談fb）。未指定時は環境変数 SLACK_CHANNEL を使用",
    )
    parser.add_argument(
        "-o", "--output-only",
        action="store_true",
        help="FBを標準出力に表示するのみ（Slack送信しない）",
    )
    parser.add_argument(
        "--no-slack",
        action="store_true",
        help="Slackに送信せず、data/feedback/ に保存",
    )

    args = parser.parse_args()

    exit_code = run(
        input_path=args.input,
        channel=args.channel,
        output_only=args.output_only,
        no_slack=args.no_slack,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
