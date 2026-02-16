# Slack連携デプロイガイド

メンバー全員がSlackから `/fb` コマンドでFB生成を使えるようにする手順です。

## 概要

| 方式 | 説明 | 難易度 |
|------|------|--------|
| **Socket Mode** | アプリがSlackに接続。公開URL不要。 | 中 |
| **HTTP + クラウド** | Cloud Run等にデプロイ。常時稼働。 | 高 |

まずは **Socket Mode** でローカル/サーバーから起動する方法を推奨します。

---

## 1. Slackアプリの作成

1. https://api.slack.com/apps にアクセス
2. **Create New App** → **From scratch**
3. アプリ名（例: `営業FBエージェント`）、ワークスペースを選択

### 1.1 Socket Mode を有効化

1. 左メニュー **Socket Mode** をクリック
2. **Enable Socket Mode** をオン
3. **App-Level Tokens** で **Generate Token and Scope** をクリック
4. トークン名（例: `connections`）を入力
5. スコープに `connections:write` を追加して生成
6. **xapp-1-...** のトークンをコピー → **SLACK_APP_TOKEN** として保存

### 1.2 Bot Token の取得

1. 左メニュー **OAuth & Permissions**
2. **Bot Token Scopes** に以下を追加:
   - `chat:write` … チャンネルに投稿
   - `chat:write.public` … 未参加チャンネルにも投稿可能
   - `commands` … スラッシュコマンド
3. **Install to Workspace** でワークスペースにインストール
4. **xoxb-...** のトークンをコピー → **SLACK_BOT_TOKEN** として保存

### 1.3 Signing Secret の取得

1. 左メニュー **Basic Information**
2. **Signing Secret** の **Show** をクリック
3. 値をコピー → **SLACK_SIGNING_SECRET** として保存

### 1.4 スラッシュコマンドの追加

1. 左メニュー **Slash Commands** → **Create New Command**
2. 以下を設定:
   - **Command**: `/fb`
   - **Short Description**: 営業FB生成
   - **Usage Hint**: 書き起こしを貼り付けてFBを生成
3. **Save**

### 1.5 チャンネルへの招待

1. Slackで **#dk_ca_初回面談fb** チャンネルを開く
2. `/invite @営業FBエージェント` でBotを招待

---

## 2. 環境変数の設定

`.env` に以下を追加:

```env
# Slack（既存）
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
SLACK_CHANNEL=C0AELMP88Q6

# Slackアプリ（追加）
SLACK_BOT_TOKEN=xoxb-xxxx
SLACK_SIGNING_SECRET=xxxx
SLACK_APP_TOKEN=xapp-1-xxxx

# LLM
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 3. 起動方法

### 3.1 ローカルで起動（開発・テスト）

```bash
cd sales-fb-agent
source .venv/bin/activate
pip install -r requirements.txt
python -m src.slack_app
```

起動後、Slackの任意のチャンネルで `/fb` と入力するとモーダルが開きます。

### 3.2 常時稼働（メンバー全員が使えるようにする）

アプリを **24時間稼働** させる必要があります。

| 方法 | 说明 |
|------|------|
| **社内サーバー** | 本番サーバーで `python -m src.slack_app` を systemd や supervisor で常駐 |
| **Cloud Run** | Socket Mode は長時間接続のため、Cloud Run Jobs は不向き。**Compute Engine** や **GCE** で常駐 |
| **Railway** | Git push で自動デプロイ。詳細は [docs/16-railway-deploy.md](16-railway-deploy.md) |
| **AWS EC2 / Lightsail** | 小インスタンスで常駐 |

**例: systemd で常駐（Ubuntu）**

```ini
# /etc/systemd/system/sales-fb-slack.service
[Unit]
Description=営業FB Slackアプリ
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/sales-fb-agent
Environment="PATH=/path/to/sales-fb-agent/.venv/bin"
ExecStart=/path/to/sales-fb-agent/.venv/bin/python -m src.slack_app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable sales-fb-slack
sudo systemctl start sales-fb-slack
```

---

## 4. 使い方（メンバー向け）

1. 任意のチャンネルで `/fb` と入力
2. モーダルが開く
3. **候補者名**（任意）と**初回面談の書き起こし**を入力
4. **FBを生成** をクリック
5. 数十秒後、#dk_ca_初回面談fb にFBが投稿される（担当者へのメンション＋候補者名が自動で付く）
6. 完了通知がそのチャンネルに表示される

---

## 5. トラブルシューティング

| 症状 | 対策 |
|------|------|
| `/fb` が表示されない | アプリをワークスペースにインストールし、チャンネルに招待しているか確認 |
| モーダルが開かない | SLACK_APP_TOKEN が正しいか、Socket Mode が有効か確認 |
| FBが投稿されない | SLACK_BOT_TOKEN、#dk_ca_初回面談fb への招待、ANTHROPIC_API_KEY を確認 |
| アプリが落ちる | ログを確認。API のレート制限やクレジット不足の可能性 |

---

## 6. 参考: HTTP モード（オプション）

Socket Mode ではなく、公開URLでHTTP リクエストを受け取る方式もあります。Cloud Run 等にデプロイする場合に利用します。

- 別途 `slack_app_http.py` のようなエントリーポイントを作成
- `RequestVerification` のミドルウェアで署名検証
- Slack の Event Subscriptions の Request URL にデプロイ先URLを設定

詳細は [Slack Bolt for Python](https://slack.dev/bolt-python/concepts#http) を参照してください。
