# デプロイ設計

## 1. デプロイ方式の選択肢

| 方式 | 概要 | 想定ユース |
|------|------|------------|
| **ローカル実行** | 開発マシンでCLI/Slackアプリ実行 | 開発・テスト |
| **Railway** | Git push で自動デプロイ | 全員が /fb 利用（推奨） |
| **Xserver / 自宅PC** | 共有サーバー or 自宅で常駐 | コスト最小 |
| **Cron / タスクスケジューラ** | 定期実行・手動起動 | ファイル一括処理（要 --input-dir 実装） |

本プロジェクトでは **ローカル + Railway** を推奨。Slack /fb は Socket Mode で常時接続が必要。

---

## 2. ローカルデプロイ

### 2.1 環境構築

```bash
cd sales-fb-agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env を編集してAPIキー・Slackトークンを設定
```

### 2.2 実行方法

```bash
# CLI: 単体実行
python src/main.py data/transcripts/raw/書き起こし.txt

# 出力のみ
python src/main.py -o data/transcripts/raw/書き起こし.txt

# Slack 送信せず data/feedback/ に保存
python src/main.py --no-slack data/transcripts/raw/書き起こし.txt

# Slack /fb コマンド用（常時起動）
python -m src.slack_app
```

※ 一括実行（--input-dir）は未実装。

---

## 3. Railway デプロイ（Slack /fb 全員利用）

Git push で自動デプロイ。詳細は [docs/16-railway-deploy.md](16-railway-deploy.md)。

- **Start Command**: `python -m src.slack_app`
- **Variables**: SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_SIGNING_SECRET, ANTHROPIC_API_KEY

---

## 4. 環境変数一覧

| 変数名 | 必須 | 説明 |
|--------|------|------|
| `ANTHROPIC_API_KEY` | いずれか | Anthropic API キー |
| `OPENAI_API_KEY` | いずれか | OpenAI API キー |
| `SLACK_WEBHOOK_URL` | CLI用 | Incoming Webhook（#dk_ca_fb） |
| `SLACK_BOT_TOKEN` | /fb用 | Bot OAuth Token (xoxb-...) |
| `SLACK_APP_TOKEN` | /fb用 | App-Level Token (xapp-...) Socket Mode |
| `SLACK_SIGNING_SECRET` | /fb用 | Signing Secret |
| `SLACK_CHANNEL` | いずれか | 送信先（例: #dk_ca_fb） |

---

## 5. セキュリティ

- `.env` は `.gitignore` に追加済み
- APIキー・トークンは環境変数のみで管理
- 書き起こしは社内ネットワーク内で扱う

---

## 6. デプロイチェックリスト

- [x] Python 仮想環境の構築
- [x] requirements.txt のインストール
- [x] .env の設定（APIキー・Slackトークン）
- [x] reference/pss/ に PSSマニュアルを格納
- [x] reference/operations/ にオペレーションマニュアルを格納
- [x] サンプル書き起こしでE2Eテスト
- [x] Slack 送信先の確認
- [ ] Railway 等へのデプロイ（任意）
