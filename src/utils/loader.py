"""参照ドキュメント・書き起こしの読み込みユーティリティ"""

import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


def load_env() -> None:
    """プロジェクトルートの .env を読み込む"""
    root = get_project_root()
    env_path = root / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            logger.debug("python-dotenv 未インストール。システム環境変数を使用します。")


def get_project_root() -> Path:
    """プロジェクトルート（sales-fb-agent/）を取得"""
    return Path(__file__).resolve().parent.parent.parent


def load_reference_docs(base_path: Union[str, Path]) -> str:
    """参照ドキュメント（.md, .txt）を再帰的に読み込み、結合して返す"""
    root = get_project_root()
    path = root / base_path if not isinstance(base_path, Path) else base_path

    if not path.exists():
        return ""

    content = []
    for root_dir, _, files in os.walk(path):
        for f in sorted(files):
            if f.startswith("."):
                continue
            if f.endswith((".md", ".txt")):
                file_path = Path(root_dir) / f
                try:
                    text = file_path.read_text(encoding="utf-8")
                    content.append(f"## {file_path.name}\n\n{text}")
                except Exception as e:
                    content.append(f"## {file_path.name}\n\n(読み込みエラー: {e})")

    return "\n\n".join(content)


def load_transcript(file_path: Union[str, Path]) -> str:
    """書き起こしファイルを読み込む"""
    path = Path(file_path)
    if not path.is_absolute():
        path = get_project_root() / path

    if not path.exists():
        raise FileNotFoundError(f"書き起こしファイルが見つかりません: {path}")

    return path.read_text(encoding="utf-8")


def save_feedback_to_file(
    feedback: str,
    candidate_name: str = "",
    save_path: Optional[Union[str, Path]] = None,
) -> Path:
    """FBを data/feedback/ に保存。candidate_name があればファイル名に含める。"""
    root = get_project_root()
    if save_path is not None:
        path = Path(save_path)
        if not path.is_absolute():
            path = root / path
    else:
        feedback_dir = root / "data" / "feedback"
        feedback_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        if candidate_name:
            safe_name = re.sub(
                r"[^\w\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]", "_", candidate_name
            )[:30]
            path = feedback_dir / f"fb_{safe_name}_{timestamp}.md"
        else:
            path = feedback_dir / f"fb_{timestamp}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(feedback, encoding="utf-8")
    return path
