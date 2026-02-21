"""FB生成エージェント - プロンプト構築・LLM連携"""

import logging
import os
import time

from src.config import DEFAULT_ANTHROPIC_MODEL, DEFAULT_OPENAI_MODEL
from src.utils.loader import get_project_root, load_reference_docs

logger = logging.getLogger(__name__)


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


def _call_llm(prompt: str, *, max_tokens: int = 4096, temperature: float = 0.3) -> str:
    """LLM呼び出し（OpenAI/Anthropic自動選択）"""
    if os.environ.get("OPENAI_API_KEY"):
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (response.choices[0].message.content or "").strip()

    if os.environ.get("ANTHROPIC_API_KEY"):
        from anthropic import Anthropic

        client = Anthropic()
        response = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL),
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return (response.content[0].text or "").strip()

    raise ValueError(
        "OPENAI_API_KEY または ANTHROPIC_API_KEY を環境変数に設定してください。"
    )


def generate_feedback(prompt: str, transcript: str = "") -> str:
    """LLMを使ってFBを生成（OpenAI / Anthropic 対応）。
    API失敗時はフォールバックFBを返す。429レート制限時は待機してリトライ。"""
    last_error = None
    for attempt in range(3):  # 初回 + リトライ2回
        try:
            return _call_llm(prompt)
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


def generate_transcript_summary(transcript: str) -> str:
    """書き起こしからトーク内容の概要を生成（マスタ用）。
    API失敗時は空文字を返す。"""
    if not transcript or len(transcript.strip()) < 50:
        return ""
    prompt = (
        "以下の初回面談の書き起こしを、200〜400文字で概要にまとめてください。\n"
        "候補者のニーズ、転職理由・背景、意思決定のポイントを整理して記載してください。\n\n"
        "【書き起こし】\n"
    )
    prompt += transcript[:8000]  # 長い場合は先頭を優先
    try:
        return _call_llm(prompt, max_tokens=500)
    except Exception:
        logger.warning("概要生成に失敗", exc_info=True)
        return ""
