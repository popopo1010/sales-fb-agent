"""共通設定定数"""

from __future__ import annotations

import logging
import os

# Slack デフォルトチャンネル（#dk_ca_初回面談fb）
DEFAULT_SLACK_CHANNEL = "C0AELMP88Q6"


def get_slack_channel(override: str | None = None) -> str:
    """Slackチャンネルを解決: 引数 > 環境変数 > デフォルト"""
    return (override or os.environ.get("SLACK_CHANNEL") or DEFAULT_SLACK_CHANNEL).strip()


# LLM モデルのデフォルト値（環境変数で上書き可能）
DEFAULT_OPENAI_MODEL = "gpt-4o"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-20250514"


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="[%(levelname)s] %(message)s",
    )
