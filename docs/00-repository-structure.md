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
│   └── 12-production-checklist.md
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
│   ├── main.py                    # エントリポイント
│   ├── agent/                     # FB生成
│   ├── slack/                     # Slack送信
│   └── utils/                     # 読み込みユーティリティ
│
├── config/                        # 設定
│   ├── fb_format.md               # FB出力形式の単一ソース（★必読）
│   └── prompts/                  # プロンプトテンプレート
│       └── fb_generation.txt
├── scripts/                       # テスト・診断スクリプト
│   ├── verify_slack.py            # Slack連携検証
│   ├── diagnose_api.py            # API診断
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
└── README.md
```

## 主要ファイル

| ファイル | 役割 |
|----------|------|
| `src/main.py` | CLI エントリポイント |
| `src/agent/generator.py` | FB生成（OpenAI/Anthropic + フォールバック） |
| `src/slack/sender.py` | Slack送信（Webhook/Bot API） |
| `config/fb_format.md` | FB出力形式の単一ソース（★） |
| `config/prompts/fb_generation.txt` | プロンプトテンプレート |

## 命名規則

- 書き起こし: `YYYYMMDD_顧客名_担当者.txt`
- 出力FB: `fb_YYYYMMDD_HHMM.md`（フォールバック時）
