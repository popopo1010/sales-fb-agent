"""営業FBエージェント - Slack /fb スラッシュコマンド

使い方: python -m src.slack_app
"""

from .main import main

__all__ = ["main"]

if __name__ == "__main__":
    main()
