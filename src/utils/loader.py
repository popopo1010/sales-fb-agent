"""参照ドキュメント・書き起こしの読み込みユーティリティ"""

import os
from pathlib import Path


def get_project_root() -> Path:
    """プロジェクトルート（sales-fb-agent/）を取得"""
    return Path(__file__).resolve().parent.parent.parent


def load_reference_docs(base_path: str | Path) -> str:
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


def load_transcript(file_path: str | Path) -> str:
    """書き起こしファイルを読み込む"""
    path = Path(file_path)
    if not path.is_absolute():
        path = get_project_root() / path

    if not path.exists():
        raise FileNotFoundError(f"書き起こしファイルが見つかりません: {path}")

    return path.read_text(encoding="utf-8")
