"""マスタデータ保存 - 候補者情報をCSVに蓄積"""

import csv
import threading
from datetime import datetime
from pathlib import Path

from src.utils.loader import get_project_root

_csv_lock = threading.Lock()


def _get_master_path() -> Path:
    """マスタCSVのパスを返す"""
    root = get_project_root()
    master_dir = root / "data" / "master"
    master_dir.mkdir(parents=True, exist_ok=True)
    return master_dir / "candidates.csv"


def save_candidate_to_master(
    candidate: str = "",
    ca_person: str = "",
    summary: str = "",
) -> None:
    """候補者情報をマスタCSVに追記する。"""
    path = _get_master_path()
    file_exists = path.exists()

    headers = ["登録日時", "候補者", "担当者", "概要"]
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        candidate or "",
        ca_person or "",
        summary or "",
    ]

    with _csv_lock, open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)
