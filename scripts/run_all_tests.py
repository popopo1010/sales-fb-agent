#!/usr/bin/env python3
"""
全検証テスト実行スクリプト

1. 環境変数・参照ドキュメントの確認
2. 書き起こし読み込みの確認
3. Slack連携の確認
4. API接続の確認
5. 本番フロー（FB生成→Slack送信）の確認
"""

import os
import sys

import bootstrap
from src.utils.loader import load_reference_docs, load_transcript

ROOT = bootstrap._ROOT
TRANSCRIPT_PATH = ROOT / "data" / "transcripts" / "raw" / "test_slack_20250213.txt"
results = []


def _run(name: str, fn) -> bool:
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


def _check_env():
    if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("ANTHROPIC_API_KEY または OPENAI_API_KEY が設定されていません")
    if not os.environ.get("SLACK_WEBHOOK_URL"):
        raise ValueError("SLACK_WEBHOOK_URL が設定されていません")


def _check_refs():
    pss = load_reference_docs(ROOT / "reference/pss")
    ops = load_reference_docs(ROOT / "reference/operations")
    fb_format = (ROOT / "config" / "fb_format.md").read_text(encoding="utf-8")
    if len(pss) < 1000:
        raise ValueError("PSSが読み込めていません")
    if len(ops) < 1000:
        raise ValueError("OPSが読み込めていません")
    if "### 8. 残論点" not in fb_format or "深掘りレベル" not in fb_format or "転職ニーズの優先順位" not in fb_format:
        raise ValueError("config/fb_format.md が正しく読み込めていません")


def _check_transcript():
    t = load_transcript(TRANSCRIPT_PATH)
    if len(t) < 10:
        raise ValueError("書き起こしが短すぎます")


def _check_slack():
    import json
    import urllib.request

    url = os.environ.get("SLACK_WEBHOOK_URL")
    payload = json.dumps({"text": "【検証テスト】営業FBエージェント - 全テスト実行中"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as res:
        if res.status != 200:
            raise ValueError(f"Slack レスポンス: {res.status}")


def _check_full_flow():
    from src.agent.generator import build_prompt, generate_feedback
    from src.slack.sender import send_feedback

    transcript = load_transcript(TRANSCRIPT_PATH)
    prompt = build_prompt(transcript)
    feedback = generate_feedback(prompt, transcript=transcript)
    if "フォールバック" in feedback and os.environ.get("ANTHROPIC_API_KEY"):
        raise ValueError("APIがフォールバックになっています。モデル・クレジットを確認してください")
    if not send_feedback(feedback):
        raise ValueError("Slack送信に失敗しました")


def run_tests():
    print("=" * 55)
    print("営業FBエージェント 検証テスト")
    print("=" * 55)

    print("\n[1/5] 環境変数確認")
    _run("環境変数", _check_env)

    print("\n[2/5] 参照ドキュメント・設定確認")
    _run("PSS・OPS・fb_format読み込み", _check_refs)

    print("\n[3/5] 書き起こし読み込み確認")
    _run("書き起こし読み込み", _check_transcript)

    print("\n[4/5] Slack連携確認")
    _run("Slack Webhook送信", _check_slack)

    print("\n[5/5] 本番フロー確認")
    _run("FB生成→Slack送信", _check_full_flow)

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
