# 人材紹介初回面談 営業FBエージェント

人材紹介における初回面談の書き起こしを入力とし、PSSとオペレーションマニュアルに沿ってフィードバックを生成し、#dk_ca_fb に送信するシステムです。

## クイックスタート

```bash
cd sales-fb-agent
source .venv/bin/activate
python src/main.py data/transcripts/raw/書き起こし.txt
```

## どこに何を置くか

| 置くもの | 場所 |
|----------|------|
| **書き起こし** | `data/transcripts/raw/` に `.txt` で保存 |
| **APIキー・Webhook** | `.env` ファイル（プロジェクト直下） |

## 環境構築

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env を編集: ANTHROPIC_API_KEY, SLACK_WEBHOOK_URL
```

## 実行

```bash
# Slackに送信
python src/main.py data/transcripts/raw/書き起こし.txt

# 出力のみ
python src/main.py -o data/transcripts/raw/書き起こし.txt

# Slack送信せず data/feedback/ に保存
python src/main.py --no-slack data/transcripts/raw/書き起こし.txt
```

## 検証テスト

```bash
# 全検証（環境・参照・Slack・API・本番フロー）
python scripts/run_all_tests.py

# 個別
python scripts/verify_slack.py    # Slack連携
python scripts/diagnose_api.py    # API診断
```

## 必要な環境変数

| 変数 | 説明 |
|------|------|
| `ANTHROPIC_API_KEY` | Anthropic API キー |
| `SLACK_WEBHOOK_URL` | Incoming Webhook（#dk_ca_fb） |
| `ANTHROPIC_MODEL` | 省略可。デフォルト: claude-sonnet-4-20250514 |

## ディレクトリ構成

```
sales-fb-agent/
├── config/            # 設定
│   ├── fb_format.md   # FB出力形式の単一ソース（★形式変更時はここを編集）
│   └── prompts/      # プロンプト
├── reference/         # PSS・OPSマニュアル
├── data/              # 書き起こし・FB
├── src/               # ソースコード
├── scripts/           # 検証・診断
├── docs/              # ドキュメント
└── README.md
```

## Slack から使う（全員向け）

```bash
python -m src.slack_app
```

起動後、任意のチャンネルで `/fb` と入力するとモーダルが開き、書き起こしを貼り付けてFBを生成できます。
詳細は [Slack連携デプロイガイド](docs/13-slack-deployment-guide.md) を参照。**Railway で Git push するだけでデプロイ**する手順は [docs/16-railway-deploy.md](docs/16-railway-deploy.md)。

## ドキュメント

- [使い方ガイド](docs/11-usage-guide.md)
- [Slack連携（全員利用）](docs/13-slack-deployment-guide.md)
- [本番チェックリスト](docs/12-production-checklist.md)
