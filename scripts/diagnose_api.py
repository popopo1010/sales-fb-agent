#!/usr/bin/env python3
"""
Anthropic API 診断スクリプト
クレジット・モデル・接続の状態を確認する
"""

import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from dotenv import load_dotenv
load_dotenv(root / ".env")


def main():
    print("=" * 50)
    print("Anthropic API 診断")
    print("=" * 50)

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("[ERROR] ANTHROPIC_API_KEY が設定されていません")
        return 1

    print(f"[1] API キー: {key[:20]}...{key[-4:]} (設定済み)")

    # 利用可能なモデル一覧を取得
    print("\n[2] 利用可能なモデル一覧を取得中...")
    try:
        from anthropic import Anthropic
        client = Anthropic()
        models = client.models.list()
        print(f"    取得できました: {len(models.data)} 件")
        for m in models.data[:10]:
            print(f"      - {m.id}")
        if len(models.data) > 10:
            print(f"      ... 他 {len(models.data) - 10} 件")
    except Exception as e:
        print(f"    [ERROR] モデル一覧取得失敗: {e}")
        return 1

    # 簡単なAPI呼び出しを試行
    print("\n[3] テストAPI呼び出し（短いプロンプト）...")
    model_to_try = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    print(f"    使用モデル: {model_to_try}")

    try:
        response = client.messages.create(
            model=model_to_try,
            max_tokens=50,
            messages=[{"role": "user", "content": "「OK」とだけ返答してください。"}],
        )
        text = response.content[0].text
        print(f"    [OK] 成功！レスポンス: {repr(text[:50])}")
        return 0
    except Exception as e:
        print(f"    [ERROR] API呼び出し失敗:")
        print(f"    種別: {type(e).__name__}")
        print(f"    内容: {e}")
        if hasattr(e, "response"):
            print(f"    レスポンス: {e.response}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
