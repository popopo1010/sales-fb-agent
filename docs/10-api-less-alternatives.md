# APIを使わない／最小限にする方法

## 1. 現在の設計でAPIが必要な箇所

| 箇所 | 役割 | 使用API | 必須？ |
|------|------|---------|--------|
| **FB生成** | 書き起こしからFBを自動生成 | OpenAI / Anthropic など | 生成を自動化するなら必要 |
| **Slack送信** | FBを #dk_ca_初回面談fb に投稿 | Slack Web API または Incoming Webhook | 自動投稿するなら必要 |

→ **完全にAPIを使わない場合**は、いずれも「手動」で代替する。

---

## 2. APIを使わない方法の選択肢

### パターンA：完全APIレス（手動運用）

| 処理 | 代替方法 | 手順 |
|------|----------|------|
| FB生成 | **Cursor チャット** | 書き起こしをCursorに貼り、`@reference/pss` `@reference/operations` で参照を指定し、FB生成を依頼する |
| Slack送信 | **手動コピペ** | 生成されたFBをコピーし、#dk_ca_初回面談fb に手動で貼り付ける |

**メリット：** APIキー・Slackアプリ・スクリプト不要  
**デメリット：** 毎回手動でコピペが必要

---

### パターンB：ローカルLLM＋手動Slack（FB生成だけ自動化）

| 処理 | 代替方法 | 備考 |
|------|----------|------|
| FB生成 | **Ollama（ローカルLLM）** | PC上でLLMを動かす。外部APIキー不要 |
| Slack送信 | 手動コピペ | 同上 |

**メリット：** 外部APIキー不要、データはローカルに残る  
**デメリット：** Ollamaのインストール・設定が必要、Slackは手動

---

### パターンC：ローカルLLM＋Incoming Webhook（半自動）

| 処理 | 代替方法 | 備考 |
|------|----------|------|
| FB生成 | **Ollama（ローカルLLM）** | 外部APIキー不要 |
| Slack送信 | **Incoming Webhook** | Bot Token・OAuth不要。URL1つでPOSTするだけ |

**メリット：** 外部APIキー不要、Slackへの投稿も自動化できる  
**デメリット：** Incoming Webhook のURL設定は必要（HTTP POSTなので技術的にはAPIだが、設定はシンプル）

---

## 3. 「APIを使わない」の定義による整理

| 意味 | 該当する方法 |
|------|--------------|
| **外部の有料API（OpenAI等）を使わない** | パターンB, C（Ollama利用） |
| **Slack Bot Token・OAuthを設定したくない** | Incoming Webhook（URLのみ） |
| **一切のHTTPアクセスも避けたい** | パターンA, B（Slackは手動コピペ） |

---

## 4. 推奨：「Cursor＋手動コピペ」（完全APIレス）

**前提：** Cursorを使っている場合、FB生成はCursorのAIで代替できる。

### 手順

1. **書き起こしを用意**  
   初回面談の書き起こしを `.txt` または `.md` で保存

2. **Cursorチャットで依頼**  
   例：
   ```
   以下の書き起こしを、@reference/pss と @reference/operations の
   PSS・オペレーションマニュアルに沿って評価し、
   良い点・改善点・ニーズの整理・意思決定6カテゴリ・障壁・総評・残論点（裏のニーズ深掘り＋具体的言い回し）の形式でフィードバックを出してください。

   [書き起こしの内容を貼り付け or ファイルを@指定]
   ```

3. **出力をコピーして #dk_ca_初回面談fb に貼り付け**

**必要なもの：** Cursor、PSS・OPSの参照ドキュメントのみ  
**不要なもの：** APIキー、Slackアプリ、Bot Token、OAuth、Incoming Webhook

---

## 5. Slack だけ自動化したい場合：Incoming Webhook

FB生成は Cursor で行い、Slackへの投稿だけ自動化する場合の選択肢。

### Incoming Webhook の特徴

- Slackアプリの作成・OAuthは不要
- チャンネルごとに「Webhook URL」を発行するだけ
- そのURLにPOSTするだけでメッセージが投稿される
- 設定は「URLを1つ覚える」だけ

### 設定手順（概要）

1. https://api.slack.com/apps で「Create New App」→「From scratch」
2. 「Incoming Webhooks」をオンにする
3. 「Add New Webhook to Workspace」をクリック
4. #dk_ca_初回面談fb を選択して許可
5. 発行された Webhook URL をコピー（`https://hooks.slack.com/services/...`）

### 送信例（curl）

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"フィードバック本文"}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

FB本文を `text` に入れてPOSTすれば、#dk_ca_初回面談fb に投稿される。

---

## 6. まとめ

| やりたいこと | 方法 | APIの使用 |
|--------------|------|-----------|
| 完全にAPIを使いたくない | CursorでFB生成 → 手動でSlackにコピペ | なし |
| FB生成だけ自動化したい | Ollama（ローカルLLM） | なし（ローカルのみ） |
| Slack投稿も自動化したい | Incoming Webhook | あり（URLへのPOSTのみ） |
| 従来どおりフル自動 | OpenAI API + Slack Web API | あり |

**「何らかのAPIを使わずにやりたい」** の厳密な解釈なら、**パターンA（Cursor＋手動コピペ）** が対応する。
