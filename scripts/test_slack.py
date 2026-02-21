#!/usr/bin/env python3
"""Slack連携テスト - Webhook にテストメッセージを送信"""

import json
import os
import sys

import bootstrap

def test_slack_webhook():
    """Webhook でテストメッセージを送信"""
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url:
        print("[ERROR] SLACK_WEBHOOK_URL が .env に設定されていません")
        return False

    import urllib.request

    message = """【営業FBエージェント】Slack連携テスト

✅ このメッセージが表示されていれば、#dk_ca_初回面談fb への送信は正常に動作しています。

テスト日時: 2025-02-13
"""

    payload = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            if res.status == 200:
                print("[OK] Slack にテストメッセージを送信しました。")
                print("     #dk_ca_初回面談fb チャンネルを確認してください。")
                return True
            else:
                print(f"[ERROR] 予期しないレスポンス: {res.status}")
                return False
    except Exception as e:
        print(f"[ERROR] Slack 送信失敗: {e}")
        return False


if __name__ == "__main__":
    success = test_slack_webhook()
    sys.exit(0 if success else 1)
