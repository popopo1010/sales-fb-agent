# 営業FBエージェント メンバー向け指示書

初回面談の書き起こしからFBを自動生成し、#dk_ca_初回面談fb に送信するツールです。**各自のPCでローカル実行**します。

**前提**: Python 3.11 以上

---

## 管理者が記入する項目（共有前に確認）

| 項目 | 状態 |
|------|------|
| リポジトリURL | ✓ 済（`https://github.com/popopo1010/sales-fb-agent.git`） |
| 管理者の連絡先 | **メンバーに .env を渡す際の連絡先を決めておく**（Slack DM、#dk_ca_初回面談fb など） |

---

## 管理者が最初にやること（1回だけ）

1. **Git リポジトリを共有**
   - リポジトリURL: `https://github.com/popopo1010/sales-fb-agent.git`
   - メンバーに上記 URL を共有

2. **`.env` の値をメンバーに渡す**
   - `.env` ファイルは Git に含まれないため、別途共有が必要
   - 1Password・Slack DM・社内Wiki など、安全な方法で以下を渡す:
     - `ANTHROPIC_API_KEY`
     - `SLACK_WEBHOOK_URL`
     - `SLACK_BOT_TOKEN`（/fb を使う場合）
     - `SLACK_APP_TOKEN`（/fb を使う場合）
     - `SLACK_SIGNING_SECRET`（/fb を使う場合）
   - または `.env.example` をコピーしたテンプレートに値を記入し、暗号化して共有

---

## メンバーへの共有用（Slackにコピペ）

```
【営業FBエージェントの使い方】

■ 初回セットアップ（1回だけ）
1. リポジトリをクローン: git clone https://github.com/popopo1010/sales-fb-agent.git
2. cd sales-fb-agent
3. python -m venv .venv && source .venv/bin/activate
4. pip install -r requirements.txt
5. cp .env.example .env して、管理者から受け取った値で .env を編集

■ 使い方（ファイルから）
・書き起こしを .txt で data/transcripts/raw/ に置く
・python src/main.py data/transcripts/raw/書き起こし.txt

■ 使い方（Slack /fb コマンド）
・ターミナルで python -m src.slack_app を起動しておく
・チャンネルで /fb と入力 → モーダルに書き起こしを入力

※.env の値は管理者に連絡して受け取ってください。
```

---

## メンバー向け 詳細手順

### 1. 初回セットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/popopo1010/sales-fb-agent.git
cd sales-fb-agent

# 2. 仮想環境を作成・有効化
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. 依存関係をインストール
pip install -r requirements.txt

# 4. 環境変数を設定
cp .env.example .env
# .env を編集（管理者から受け取った API キー・Slack の値を入力）
```

> `.env` の値は管理者に連絡して受け取ってください。Git には含まれません。

---

### 2. 使い方（ファイルから・推奨）

書き起こしを `.txt` ファイルで持っている場合：

```bash
cd sales-fb-agent
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 書き起こしを data/transcripts/raw/ に置いて実行
python src/main.py data/transcripts/raw/書き起こし.txt
```

FB が #dk_ca_初回面談fb に自動投稿されます。

---

### 3. 使い方（Slack /fb コマンド）

Slack の `/fb` を使う場合、**自分のPCでアプリを起動**しておく必要があります。

```bash
cd sales-fb-agent
source .venv/bin/activate
python -m src.slack_app
```

起動後、任意のチャンネルで `/fb` と入力するとモーダルが開きます。候補者名（任意）と書き起こしを入力して送信すると、#dk_ca_初回面談fb にFBが投稿されます。

> ターミナルを閉じると `/fb` は使えなくなります。使うときだけ起動してください。

---

## 出力されるFBの内容

- 良い点
- 改善点
- ニーズの整理
- 意思決定6カテゴリで重要になりそうな項目
- 年収相場との整合性・許容アプローチ
- 障壁になりそうなポイント
- 総評・アドバイス
- 残論点（裏のニーズ深掘り）

---

## 困ったときは

| 症状 | 対応 |
|------|------|
| `.env` がない | 管理者に連絡して API キー・Slack の値を受け取る |
| `ModuleNotFoundError` | `pip install -r requirements.txt` を実行 |
| FBが投稿されない | `.env` の値が正しいか確認。管理者に連絡 |
| `/fb` が反応しない | ターミナルで `python -m src.slack_app` が起動しているか確認 |
| 出力形式を変えたい | 管理者に依頼（`config/fb_format.md` の編集） |

---

## 関連ドキュメント

- [メンバー向けクイックスタート](14-member-quickstart.md)
- [使い方ガイド](11-usage-guide.md)
