#!/usr/bin/env python3
"""
全検証テスト実行スクリプト

以下のテストを順次実行し、問題がないか確認する。
1. 環境変数・参照ドキュメントの確認
2. 書き起こし読み込みの確認
3. Slack連携の確認
4. API接続の確認
5. 本番フロー（FB生成→Slack送信）の確認
"""

import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from dotenv import load_dotenv
load_dotenv(root / ".env")

# テスト結果
results = []


def test(name: str, fn):
    """テスト実行"""
    try:
        fn()
        results.append((name, True, None))
        print(f"  [OK] {name}")
        return True
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"  [NG] {name}: {e}")
        return False


def run_tests():
    print("=" * 55)
    print("営業FBエージェント 検証テスト")
    print("=" * 55)

    # 1. 環境変数
    print("\n[1/5] 環境変数確認")
    def check_env():
        if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY または OPENAI_API_KEY が設定されていません")
        if not os.environ.get("SLACK_WEBHOOK_URL"):
            raise ValueError("SLACK_WEBHOOK_URL が設定されていません")
    test("環境変数", check_env)

    # 2. 参照ドキュメント・設定
    print("\n[2/5] 参照ドキュメント・設定確認")
    def check_refs():
        from src.utils.loader import load_reference_docs
        pss = load_reference_docs(root / "reference/pss")
        ops = load_reference_docs(root / "reference/operations")
        fb_format = (root / "config" / "fb_format.md").read_text(encoding="utf-8")
        if len(pss) < 1000:
            raise ValueError("PSSが読み込めていません")
        if len(ops) < 1000:
            raise ValueError("OPSが読み込めていません")
        if "### 8. 残論点" not in fb_format:
            raise ValueError("config/fb_format.md が正しく読み込めていません")
    test("PSS・OPS・fb_format読み込み", check_refs)

    # 3. 書き起こし読み込み
    print("\n[3/5] 書き起こし読み込み確認")
    transcript_path = root / "data" / "transcripts" / "raw" / "test_slack_20250213.txt"
    def check_transcript():
        from src.utils.loader import load_transcript
        t = load_transcript(transcript_path)
        if len(t) < 10:
            raise ValueError("書き起こしが短すぎます")
    test("書き起こし読み込み", check_transcript)

    # 4. Slack連携
    print("\n[4/5] Slack連携確認")
    def check_slack():
        import urllib.request
        import json
        url = os.environ.get("SLACK_WEBHOOK_URL")
        payload = json.dumps({"text": "【検証テスト】営業FBエージェント - 全テスト実行中"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as res:
            if res.status != 200:
                raise ValueError(f"Slack レスポンス: {res.status}")
    test("Slack Webhook送信", check_slack)

    # 5. 本番フロー
    print("\n[5/5] 本番フロー確認")
    def check_full_flow():
        from src.agent.generator import build_prompt, generate_feedback
        from src.slack.sender import send_feedback
        from src.utils.loader import load_transcript

        transcript = load_transcript(transcript_path)
        prompt = build_prompt(transcript)
        feedback = generate_feedback(prompt, transcript=transcript)
        if "フォールバック" in feedback and os.environ.get("ANTHROPIC_API_KEY"):
            raise ValueError("APIがフォールバックになっています。モデル・クレジットを確認してください")
        if not send_feedback(feedback):
            raise ValueError("Slack送信に失敗しました")
    test("FB生成→Slack送信", check_full_flow)

    # 結果サマリ
    print("\n" + "=" * 55)
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    if passed == total:
        print(f"【成功】全 {total} 件のテストがパスしました。")
        return 0
    else:
        print(f"【失敗】{total - passed} 件のテストが失敗しました。")
        for name, ok, err in results:
            if not ok:
                print(f"  - {name}: {err}")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
