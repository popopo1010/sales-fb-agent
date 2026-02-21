#!/usr/bin/env python3
"""
Slack連携の動作検証スクリプト

実行後、#dk_ca_初回面談fb に以下のメッセージが表示されればOKです：
---
【動作確認】営業FBエージェント
スクリプトは正常に動作しています。
もしこのメッセージが見えていれば、Slack連携は成功しています。
---
"""

import json
import os
import sys

import bootstrap


def main():
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url:
        print("[ERROR] SLACK_WEBHOOK_URL が設定されていません")
        print("        .env ファイルを確認し、SLACK_WEBHOOK_URL を設定してください。")
        return 1

    print("[1] .env 読み込み: OK")
    print(f"[2] Webhook URL: {url[:50]}...")

    message = """【動作確認】営業FBエージェント

スクリプトは正常に動作しています。
もしこのメッセージが見えていれば、Slack連携は成功しています。"""

    import urllib.request

    payload = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            body = res.read().decode()
            print(f"[3] Slack レスポンス: {res.status} {body or '(OK)'}")

            if res.status == 200:
                print("")
                print("=" * 50)
                print("【成功】#dk_ca_初回面談fb を確認してください。")
                print("        上記のメッセージが表示されていればOKです。")
                print("=" * 50)
                return 0
            else:
                print(f"[ERROR] 予期しないステータス: {res.status}")
                return 1
    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP エラー: {e.code} {e.reason}")
        print(f"        レスポンス: {e.read().decode()}")
        return 1
    except Exception as e:
        print(f"[ERROR] 送信失敗: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
