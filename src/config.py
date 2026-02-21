"""共通設定定数"""

import logging

# Slack デフォルトチャンネル（#dk_ca_初回面談fb）
DEFAULT_SLACK_CHANNEL = "C0AELMP88Q6"

# LLM モデルのデフォルト値（環境変数で上書き可能）
DEFAULT_OPENAI_MODEL = "gpt-4o"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-20250514"


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="[%(levelname)s] %(message)s",
    )
