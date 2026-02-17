# テスト

## 実行方法

```bash
# 全検証（環境・参照・Slack・API・本番フロー）
python scripts/run_all_tests.py

# 個別
python scripts/verify_slack.py    # Slack連携
python scripts/diagnose_api.py    # API診断
python scripts/test_full_flow.py  # 一連の流れ
python scripts/test_slack.py      # Slack送信
```

## 構成

- `scripts/` に検証・テストスクリプトを配置
- `tests/` はユニットテスト用（将来拡張）
