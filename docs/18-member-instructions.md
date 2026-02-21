# 営業FBエージェント メンバー向け指示書

初回面談の書き起こしからFBを自動生成し、#dk_ca_初回面談fb に送信するツールです。**各自のPCでローカル実行**します。

**前提**: Python 3.11 以上

---

## ★ 推奨: パッケージで渡す（メンバーは編集不要）

メンバーが `.env` を編集せず、最初から使える形で渡す方法です。

### 管理者の手順

```bash
cd sales-fb-agent
./scripts/create_member_package.sh
zip -r member-package.zip member-package
```

`member-package.zip` を Slack DM 等でメンバーに送る。

### メンバーの手順

1. zip を解凍
2. 解凍したフォルダ内でターミナルを開く
3. `chmod +x setup_member.sh && ./setup_member.sh` を実行
4. 完了メッセージに表示される起動コマンドを実行

**メンバーは .env を編集する必要はありません。** 最初から設定済みです。

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

## 既存メンバー向け：アップデート手順

すでに使っているメンバーが最新版に更新する場合：

```bash
# 1. プロジェクトフォルダへ移動（まだの場合）
cd sales-fb-agent   # または cd ~/work/sales-fb-agent 等、クローン先のパス

# 2. 最新版を取得
git pull

# 3. 仮想環境を有効化（.venv がない場合は下記「仮想環境がない場合」を参照）
source .venv/bin/activate

# 4. 依存関係を更新
pip install -r requirements.txt
```

**仮想環境の有効化**（`.venv` か `venv` のどちらかがあるはず）:
```bash
# .venv がある場合
source .venv/bin/activate

# venv がある場合（.venv がないとき）
source venv/bin/activate
```
`ls -la` で `.venv` または `venv` フォルダがあるか確認してください。

`.env` はそのままでOKです。変更があれば管理者から連絡があります。

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
・チャンネルで /fb と入力 → モーダルに書き起こし・候補者名（任意）・担当者名（任意）を入力

※.env の値は管理者に連絡して受け取ってください。

■ 既に使っている人：アップデート手順
  1. cd sales-fb-agent（プロジェクトのパスへ）
  2. git pull
  3. source .venv/bin/activate または source venv/bin/activate
  4. pip install -r requirements.txt
  （.env はそのままでOK）
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
cd sales-fb-agent   # または cd ~/work/sales-fb-agent 等、クローン先のパス
source .venv/bin/activate
python3 -m src.slack_app
```

起動後、任意のチャンネルで `/fb` と入力するとモーダルが開きます。書き起こし・候補者名（任意）・担当者名（任意）を入力して送信すると、#dk_ca_初回面談fb にFBが投稿されます。

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
| `.venv/bin/activate がない` | `source venv/bin/activate` を試す。どちらもなければ `python3 -m venv .venv` で作成 |
| `unsupported operand type(s) for \|` | `git pull` で最新版を取得。解消しない場合は Python 3.9 以上を確認 |
| FBが投稿されない | `.env` の値が正しいか確認。管理者に連絡 |
| `/fb` が反応しない | ターミナルで `python -m src.slack_app` が起動しているか確認 |
| 「Slack になかなか接続できません」 | アプリ未起動の可能性。`python -m src.slack_app` を起動してから `/fb` を実行。SLACK_APP_TOKEN が正しいか確認 |
| 候補者名を空で送信してエラー | 修正済み。再発したら管理者に連絡 |
| 出力形式を変えたい | 管理者に依頼（`config/fb_format.md` の編集） |

---

## 関連ドキュメント

- [メンバー向けクイックスタート](14-member-quickstart.md)
- [使い方ガイド](11-usage-guide.md)
