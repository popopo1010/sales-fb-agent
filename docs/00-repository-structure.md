# リポジトリストラクチャ

## 概要

営業FB（フィードバック）エージェントのプロジェクト構成を定義する。

## ディレクトリ構成

```
sales-fb-agent/
├── docs/                          # プロジェクトドキュメント
│   ├── 00-repository-structure.md
│   ├── 01-usage-definition.md
│   ├── ...
│   ├── 15-slack-app-install.md
│   ├── 16-railway-deploy.md        # Railway デプロイ
│   └── 17-github-setup.md         # GitHub 連携
│
├── reference/                     # 参照ドキュメント
│   ├── pss/                       # PSSマニュアル
│   │   ├── pss-sales-scheme.md
│   │   └── 【PSS】テキスト.pdf
│   └── operations/                # オペレーションマニュアル
│       ├── operation-manual.md
│       └── salary-market.md      # 年収相場（資格・経験別）
│
├── data/                          # データ
│   ├── transcripts/raw/           # 書き起こし（入力）
│   ├── feedback/                  # FB履歴
│   └── examples/                  # サンプル
│
├── src/                           # ソースコード
│   ├── main.py                    # CLI エントリポイント
│   ├── slack_app.py               # Slack /fb スラッシュコマンド（Bolt）
│   ├── agent/                     # FB生成
│   ├── slack/                     # Slack送信
│   └── utils/                     # 読み込みユーティリティ
│
├── config/                        # 設定
│   ├── fb_format.md               # FB出力形式の単一ソース（★必読）
│   ├── slack-app-manifest.yaml    # Slackアプリマニフェスト
│   └── prompts/                   # プロンプトテンプレート
│       ├── fb_generation.txt
│       └── cursor-hand-prompt.md
│
├── scripts/                       # テスト・診断スクリプト
│   ├── verify_slack.py            # Slack連携検証
│   ├── diagnose_api.py            # API診断
│   ├── run_all_tests.py           # 全検証
│   └── test_full_flow.py          # 一連の流れテスト
│
├── .cursor/rules/                 # Cursor ルール
├── tests/
├── logs/
│
├── .env.example
├── .gitignore
├── requirements.txt
├── run.sh
├── Procfile                       # Railway / Heroku 用
├── runtime.txt                    # Python バージョン指定
└── README.md
```

## 主要ファイル

| ファイル | 役割 |
|----------|------|
| `src/main.py` | CLI エントリポイント（書き起こしファイル→FB→Slack） |
| `src/slack_app.py` | Slack /fb スラッシュコマンド（モーダルで候補者名・書き起こし入力→担当メンション＋FB生成） |
| `src/agent/generator.py` | FB生成（OpenAI/Anthropic + フォールバック） |
| `src/slack/sender.py` | Slack送信（Webhook/Bot API） |
| `config/fb_format.md` | FB出力形式の単一ソース（★） |
| `config/prompts/fb_generation.txt` | プロンプトテンプレート |
| `config/slack-app-manifest.yaml` | Slackアプリ作成用マニフェスト |
| `Procfile` | Railway 等の起動コマンド |

## 実行入口

| 用途 | コマンド |
|------|----------|
| CLI（ファイル指定） | `python src/main.py data/transcripts/raw/書き起こし.txt` |
| Slack /fb コマンド | `python -m src.slack_app` |

## 命名規則

- 書き起こし: `YYYYMMDD_顧客名_担当者.txt`
- 出力FB: `fb_YYYYMMDD_HHMM.md`（フォールバック時）
