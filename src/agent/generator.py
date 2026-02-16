"""FB生成エージェント - プロンプト構築・LLM連携"""

import os
import time
from pathlib import Path

from src.utils.loader import get_project_root, load_reference_docs


def build_prompt(
    transcript: str,
    pss_dir: str = "reference/pss",
    ops_dir: str = "reference/operations",
) -> str:
    """プロンプトテンプレートに書き起こしと参照を埋めて構築"""
    root = get_project_root()
    pss_content = load_reference_docs(root / pss_dir)
    ops_content = load_reference_docs(root / ops_dir)

    fb_format_path = root / "config" / "fb_format.md"
    fb_format = fb_format_path.read_text(encoding="utf-8") if fb_format_path.exists() else ""

    template_path = root / "config" / "prompts" / "fb_generation.txt"
    template = template_path.read_text(encoding="utf-8")

    return template.format(
        pss_content=pss_content,
        ops_content=ops_content,
        transcript=transcript,
        fb_format=fb_format,
    )


def generate_feedback(prompt: str, transcript: str = "") -> str:
    """LLMを使ってFBを生成（OpenAI / Anthropic 対応）。
    API失敗時はフォールバックFBを返す。429レート制限時は待機してリトライ。"""
    last_error = None
    for attempt in range(3):  # 初回 + リトライ2回
        try:
            if os.environ.get("OPENAI_API_KEY"):
                return _generate_openai(prompt)
            if os.environ.get("ANTHROPIC_API_KEY"):
                return _generate_anthropic(prompt)

            raise ValueError(
                "OPENAI_API_KEY または ANTHROPIC_API_KEY を環境変数に設定してください。"
            )
        except Exception as e:
            last_error = e
            error_msg = str(e)
            # 429 レート制限: 65秒待機してリトライ
            if attempt < 2 and ("429" in error_msg or "rate_limit" in error_msg.lower()):
                time.sleep(65)
                continue
            if (
                "credit" in error_msg.lower()
                or "balance" in error_msg.lower()
                or "400" in error_msg
                or "404" in error_msg
                or "not_found" in error_msg.lower()
            ):
                return _generate_fallback_feedback(transcript, error_msg)
            raise last_error


def _generate_fallback_feedback(transcript: str, error_reason: str = "") -> str:
    """API失敗時（クレジット不足・モデル未対応等）のフォールバックFB"""
    return """### 全体評価：-/10点

・ API呼び出しに失敗したため、スコアは算出されていません
・ クレジット・モデル設定を確認し、再実行してください

### 1. 良い点
- （API利用後に再評価）

### 2. 改善点
- （API利用後に再評価）

### 3. ニーズの整理
- **ニーズ**: 要確認
- **転職ニーズの優先順位**: 要確認
- **深掘りレベル**: Lv1（API利用後に再評価）

### 4. 意思決定の6カテゴリで重要になりそうな項目
- （API利用後に再評価）

### 5. 年収相場との整合性・許容アプローチ
- （API利用後に再評価）

### 6. 障壁になりそうなポイント
- （API利用後に再評価）

### 7. 総評・アドバイス
- APIクレジット追加後に再実行してください。

### 8. 残論点（裏のニーズ深掘りに特化）
- **深掘りすべきテーマ**: -
- **具体的な質問フレーズ**: -

### 9. Zoho アトラクト・ストーリーコピー用
◼︎コアニーズ
（API利用後に再評価）

◼︎訴求
（API利用後に再評価）

◼︎受諾ストーリー
（API利用後に再評価）

◼︎障壁
（API利用後に再評価）
"""


def _generate_openai(prompt: str) -> str:
    """OpenAI API でFB生成"""
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content


def _generate_anthropic(prompt: str) -> str:
    """Anthropic API でFB生成"""
    from anthropic import Anthropic

    client = Anthropic()
    response = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
