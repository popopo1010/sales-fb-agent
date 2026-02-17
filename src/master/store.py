"""マスタデータ保存 - 候補者情報をCSVに蓄積"""

import csv
from datetime import datetime
from pathlib import Path


def _get_master_path() -> Path:
    """マスタCSVのパスを返す"""
    root = Path(__file__).resolve().parent.parent.parent
    master_dir = root / "data" / "master"
    master_dir.mkdir(parents=True, exist_ok=True)
    return master_dir / "candidates.csv"


def save_candidate_to_master(
    candidate: str,
    ca_person: str = "",
    summary: str = "",
    qualifications: str = "",
    experience: str = "",
    age: str = "",
    desired_salary: str = "",
    prefecture: str = "",
    commute_time: str = "",
    business_trip_ok: str = "",
    family_structure: str = "",
    needs: str = "",
    specific_needs: str = "",
    why_important: str = "",
    needs_background: str = "",
    needs_priority: str = "",
    barriers: str = "",
) -> None:
    """候補者情報をマスタCSVに追記する。"""
    path = _get_master_path()
    file_exists = path.exists()

    headers = [
        "登録日時", "候補者", "CA担当者", "概要",
        "保有資格", "経験", "年齢", "希望年収",
        "都道府県", "通勤時間", "出張OKか", "家族構成",
        "ニーズ", "具体的なニーズ", "なぜ重要か", "ニーズが重要に至った背景",
        "ニーズの優先順位", "進める上での障壁",
    ]
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        candidate or "",
        ca_person or "",
        summary or "",
        qualifications or "",
        experience or "",
        age or "",
        desired_salary or "",
        prefecture or "",
        commute_time or "",
        business_trip_ok or "",
        family_structure or "",
        needs or "",
        specific_needs or "",
        why_important or "",
        needs_background or "",
        needs_priority or "",
        barriers or "",
    ]

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)
