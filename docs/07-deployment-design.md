# デプロイ設計

## 1. デプロイ方式の選択肢

| 方式 | 概要 | 想定ユース |
|------|------|------------|
| **ローカル実行** | 開発マシンでCLI実行 | 開発・小規模利用 |
| **Cron / タスクスケジューラ** | 定期実行・手動起動 | 中規模・社内利用 |
| **サーバーレス (Lambda / Cloud Functions)** | イベント駆動 | 大規模・自動化 |
| **コンテナ (Docker)** | 可搬性の高い実行環境 | 複数環境・CI |

本プロジェクトでは、まず **ローカル + Cron** を想定し、必要に応じて拡張する。

---

## 2. ローカルデプロイ

### 2.1 環境構築

```bash
cd sales-fb-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env を編集してAPIキー・Slackトークンを設定
```

### 2.2 実行方法

```bash
# 単体実行
python src/main.py --input data/transcripts/sample.txt

# 一括実行
python src/main.py --input-dir data/transcripts/
```

---

## 3. Cron による定期実行（オプション）

### 3.1 概要

指定ディレクトリに新しい書き起こしが配置されたら処理する、または日次で一括処理する。

### 3.2 crontab 例

```cron
# 毎日 9:00 に data/transcripts/ 内の未処理ファイルを処理
0 9 * * * cd /path/to/sales-fb-agent && ./venv/bin/python src/main.py --input-dir data/transcripts/ >> logs/cron.log 2>&1
```

### 3.3 前提

- 書き起こし配置のルール（例: `processed/` に移動して重複防止）を決めておく
- ログディレクトリ `logs/` を作成しておく

---

## 4. 環境変数一覧

| 変数名 | 必須 | 説明 |
|--------|------|------|
| `OPENAI_API_KEY` | いずれか | OpenAI API キー |
| `ANTHROPIC_API_KEY` | いずれか | Anthropic API キー |
| `SLACK_BOT_TOKEN` | 必須 | Slack Bot OAuth Token |
| `SLACK_CHANNEL` | いずれか | 送信先チャンネル（例: #sales-fb） |
| `SLACK_USER_ID` | いずれか | DM送信先ユーザーID |

---

## 5. セキュリティ

- `.env` は `.gitignore` に追加
- APIキー・トークンは環境変数のみで管理（コードにハードコードしない）
- 書き起こしは社内ネットワーク内で扱う

---

## 6. 将来の拡張（サーバーレス）

- S3 に書き起こしが配置されたら Lambda を起動
- Lambda 内で FB 生成 → Slack 送信
- VPC 内で実行する場合は NAT 経由で API 呼び出し

---

## 7. デプロイチェックリスト

- [ ] Python 仮想環境の構築
- [ ] requirements.txt のインストール
- [ ] .env の設定（APIキー・Slackトークン）
- [ ] reference/pss/ に PSSマニュアルを格納
- [ ] reference/operations/ にオペレーションマニュアルを格納
- [ ] サンプル書き起こしでE2Eテスト
- [ ] Slack 送信先の確認
