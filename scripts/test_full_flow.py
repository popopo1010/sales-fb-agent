#!/usr/bin/env python3
"""一連の流れテスト（書き起こし → FB形式 → Slack送信）

※ LLM API のクレジット不足時は、サンプルFBを送信してSlack連携を確認します。
"""

import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from dotenv import load_dotenv
load_dotenv(root / ".env")

from src.utils.loader import load_transcript
from src.slack.sender import send_feedback


def create_sample_fb(transcript: str) -> str:
    """LLMが使えない場合のサンプルFB（テスト用）"""
    return f"""## 面談FB（テスト送信）

※ これはSlack連携テスト用のサンプルです。APIキーにクレジットが入れば、PSS・OPSに基づいた正式なFBが生成されます。

### 1. 良い点
- （テストのため省略）

### 2. 改善点
- （テストのため省略）

### 3. ニーズの整理
- **ニーズ**: 書き起こしが短いため詳細は不明
- **具体的なニーズ**: -
- **なぜそのニーズが重要なのか**: -
- **そのニーズが重要に至った背景**: -

### 4. 意思決定の6カテゴリで重要になりそうな項目
- （テストのため省略）

### 5. 年収相場との整合性・許容アプローチ
- （テストのため省略）

### 6. 障壁になりそうなポイント
- （テストのため省略）

### 7. 総評・アドバイス
- 本メッセージはSlack連携の動作確認用です。書き起こしは正常に読み込まれました。

### 8. 残論点（裏のニーズ深掘りに特化）
- **深掘りすべきテーマ**: -
- **具体的な質問フレーズ（言い回し）**: -
"""


def main():
    transcript_path = root / "data" / "transcripts" / "raw" / "test_slack_20250213.txt"
    if not transcript_path.exists():
        print(f"[ERROR] 書き起こしが見つかりません: {transcript_path}")
        return 1

    print("[1/3] 書き起こしを読み込み中...")
    transcript = load_transcript(transcript_path)
    print(f"      → {len(transcript)} 文字読み込みました")

    print("[2/3] FB生成（サンプルを使用・APIクレジット不足のため）...")
    fb = create_sample_fb(transcript)

    print("[3/3] Slack に送信中...")
    if send_feedback(fb):
        print("[OK] 一連の流れが正常に完了しました。")
        print("     #dk_ca_fb でFBを確認してください。")
        return 0

    print("[ERROR] Slack 送信に失敗しました。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
