# 詳細メモ

## 1. プロジェクト概要の要約

- **目的**: 人材紹介の初回面談の書き起こしを入力とし、PSSとオペレーションマニュアルに沿ったFBを自動生成し、Slackに送信する
- **業界**: 人材紹介（スタッフィング・リクルーティング）
- **入力**: 初回面談の書き起こし（テキスト）
- **出力**: 営業FB（Slack投稿）
- **参照**: PSS営業スキーム、オペレーションマニュアル

---

## 2. PSSマニュアルの格納場所（重要）

### 推奨パス

```
reference/pss/
```

### 格納すべきファイル例

| ファイル名 | 内容 |
|------------|------|
| `pss-sales-scheme.md` | PSS営業スキームのメインドキュメント |
| `evaluation-criteria.md` | 評価基準・チェック項目（任意） |
| `flow.md` | 面談フロー・ステップ（任意） |

### オペレーションマニュアル

```
reference/operations/
```

| ファイル名 | 内容 |
|------------|------|
| `operation-manual.md` | オペレーションマニュアル本体 |

### 注意点

- Markdown形式を推奨（AIが読みやすい）
- ファイル名に日本語も可（`pss-営業スキーム.md` 等）
- 機密性が高い場合は `.gitignore` に追加し、社内リポジトリで管理

---

## 3. 書き起こしの形式

想定される形式の例:

- **逐語録**: 「候補者: ～」「担当: ～」のような発言者ごとの形式
- **議事録**: 要約・箇条書き
- **時間軸付き**: 「00:05 ～」「10:30 ～」のようなタイムスタンプ付き

プロンプト側で「該当箇所」を指摘しやすくするため、可能であれば時間軸付きの形式を推奨。

---

## 4. FBの出力形式

**config/fb_format.md** を参照（8項目の単一ソース）。

- 良い点・改善点・ニーズの整理・意思決定6カテゴリ・年収相場との整合性・障壁・総評・残論点
- 形式変更時は config/fb_format.md のみを編集すればよい

Slack では Markdown の一部が mrkdwn として解釈されるため、送信時にプレーンテキストへ変換している。

---

## 5. Slack 設定の流れ

1. https://api.slack.com/apps でアプリを作成
2. OAuth & Permissions で `chat:write` を付与
3. Bot Token を取得
4. 対象チャンネルに Bot を招待: `/invite @アプリ名`
5. 環境変数 `SLACK_BOT_TOKEN`, `SLACK_CHANNEL` を設定

---

## 6. 今後の検討事項

- [ ] Cursor エージェントとしても実行可能にする（ドキュメントを参照してFB生成）
- [ ] Web UI で書き起こしをアップロードし、FBを取得
- [ ] FBの履歴をDBに保存し、検索・分析
- [ ] 音声ファイルを直接投入し、文字起こし→FBまで一括処理

---

## 7. ドキュメント一覧

| ドキュメント | パス |
|--------------|------|
| リポジトリストラクチャ | docs/00-repository-structure.md |
| 使用定義書 | docs/01-usage-definition.md |
| 要件定義 | docs/02-requirements.md |
| ユースケース | docs/03-use-cases.md |
| アーキテクチャ設計 | docs/04-architecture.md |
| タスクバックログ | docs/05-task-backlog.md |
| 実装ガイド | docs/06-implementation-guide.md |
| デプロイ設計 | docs/07-deployment-design.md |
| 運用ガイド | docs/08-operations-guide.md |
| 詳細メモ | docs/09-detailed-notes.md |
