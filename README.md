# 人材紹介初回面談 営業FBエージェント

人材紹介における初回面談の書き起こしを入力とし、PSSとオペレーションマニュアルに沿ってフィードバックを生成し、#dk_ca_初回面談fb に送信するシステムです。

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
| **マスタ（候補者情報）** | `data/master/candidates.csv`（/fb で自動追記） |

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
| `SLACK_WEBHOOK_URL` | Incoming Webhook（#dk_ca_初回面談fb） |
| `ANTHROPIC_MODEL` | 省略可。デフォルト: claude-sonnet-4-20250514 |

**Slack /fb コマンド用（追加）**: `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `SLACK_SIGNING_SECRET`

## ディレクトリ構成

```
sales-fb-agent/
├── config/            # 設定（fb_format.md, prompts/）
├── reference/         # PSS・OPS・ドメイン参照
├── data/              # 書き起こし・FB・マスタ
│   ├── transcripts/raw/  # 書き起こし
│   ├── feedback/        # FB履歴
│   └── master/          # 候補者マスタ（candidates.csv）
├── src/               # ソースコード（main, slack_app, agent, slack, master）
├── scripts/           # 検証・セットアップ
├── docs/              # ドキュメント
└── README.md
```

詳細は [docs/00-repository-structure.md](docs/00-repository-structure.md) を参照。

## Slack から使う（/fb コマンド）

各自のPCで以下を実行すると、Slack の `/fb` が使えます。

```bash
python -m src.slack_app
```

起動後、任意のチャンネルで `/fb` と入力するとモーダルが開きます。候補者名（任意）と書き起こしを入力して送信すると、**担当者へのメンション＋候補者名**付きで #dk_ca_初回面談fb にFBが投稿されます。

> メンバーへの共有方法は [メンバー向け指示書](docs/18-member-instructions.md) を参照。常時稼働させたい場合は [Railway デプロイ](docs/16-railway-deploy.md) も選択肢。

## ドキュメント

- [**メンバー向け指示書**](docs/18-member-instructions.md)（管理者の初期設定＋メンバーへの共有用）
- [メンバー向け使い方](docs/14-member-quickstart.md)（/fb の使い方・シェア用）
- [Slack連携（全員利用）](docs/13-slack-deployment-guide.md)
- [Railway デプロイ](docs/16-railway-deploy.md)
- [使い方ガイド](docs/11-usage-guide.md)
- [本番チェックリスト](docs/12-production-checklist.md)
