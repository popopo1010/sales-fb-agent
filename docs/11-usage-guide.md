# 営業FBエージェント 使い方ガイド

メンバー全員が使えるよう、手順をまとめました。

---

## 1. 書き起こしを貼り付ける場所

**書き起こしファイルをこのフォルダに置いてください：**

```
sales-fb-agent/data/transcripts/raw/
```

### 手順

1. 面談の音声を文字起こしする（Whisper、ChatGPT、など）
2. テキストを `.txt` または `.md` ファイルに保存
3. ファイル名の例: `20250213_田中様_山田.txt`
4. `data/transcripts/raw/` フォルダに保存（またはコピー）

### ファイル形式の例

```
CA: もしもし、〇〇さんでお間違いないでしょうか？
候補者: はい、そうです。
CA: 電気工事の求人を検索いただいた件で...
（以下、書き起こし）
```

---

## 2. 初回セットアップ（一度だけ）

### 2.1 プロジェクトを開く

```bash
cd sales-fb-agent
# または Cursor / VS Code で sales-fb-agent フォルダを開く
```

### 2.2 環境構築

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2.3 設定ファイルの作成

1. `.env.example` をコピーして `.env` を作成
2. `.env` を開き、以下を設定：

```env
# OpenAI API キー（必須）
OPENAI_API_KEY=sk-あなたのAPIキー

# Slack Webhook（送信先: #dk_ca_fb）
# チーム管理者から共有されたURLを貼り付ける
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/xxx/xxx
```

**Slack Webhook URL の共有：**  
チーム管理者が `.env` の `SLACK_WEBHOOK_URL` の値をメンバーに共有してください（Slack DM、社内Wiki、1Password 等）。  
※ Webhook URL は #dk_ca_fb への投稿権限を含むため、外部に漏れないよう注意してください。

---

## 3. 実行方法

### パターンA：Slack に送信する（通常）

```bash
cd sales-fb-agent
source .venv/bin/activate  # Windows: .venv\Scripts\activate

python src/main.py data/transcripts/raw/書き起こしファイル名.txt
```

 → FB が #dk_ca_fb に投稿されます。

### パターンB：いったん出力だけ確認したい

```bash
python src/main.py -o data/transcripts/raw/書き起こしファイル名.txt
```

 → ターミナルに FB が表示されます。Slack には送信されません。

### パターンC：Slack に送らずファイルに保存

```bash
python src/main.py --no-slack data/transcripts/raw/書き起こしファイル名.txt
```

 → `data/feedback/` に FB が保存されます。

---

## 4. 一覧：どこに何を置くか

| 置くもの | 場所 |
|----------|------|
| **書き起こし** | `data/transcripts/raw/` |
| **APIキー・Webhook** | `.env` ファイル（プロジェクト直下） |
| **FB履歴（自動保存）** | `data/feedback/` |

---

## 5. よくある質問

**Q: 書き起こしはどこに貼る？**  
A: `data/transcripts/raw/` に `.txt` ファイルとして保存してください。

**Q: 他のメンバーが使うには？**  
A: 1) プロジェクトを共有 2) 各自で `.venv` を構築 3) `.env` に APIキーと Webhook を設定

**Q: Webhook URL はどこで共有する？**  
A: チーム管理者が Slack や 1Password で共有。`.env` は Git に含まれないので、直接コピーして渡すことも可能です。

---

## 6. 動作確認

```bash
# Slack連携だけテスト
python scripts/test_slack.py

# 一連の流れをテスト（書き起こし→FB→Slack）
python scripts/test_full_flow.py
```

## 7. まとめ

```
1. 書き起こしを data/transcripts/raw/ に保存
2. .env に ANTHROPIC_API_KEY（または OPENAI_API_KEY）を設定
3. python src/main.py data/transcripts/raw/ファイル名.txt を実行
4. #dk_ca_fb で FB を確認
```

**補足:** Anthropic API のクレジット不足時は、[console.anthropic.com](https://console.anthropic.com) でクレジットを追加してください。
