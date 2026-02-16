# Slackアプリのインストール手順

`/fb` コマンドを使うために、ワークスペースにアプリをインストールします。

---

## 方法A: マニフェストから作成（推奨・一括設定）

アプリがまだない場合、マニフェストで一括作成できます。

### 手順

1. https://api.slack.com/apps にアクセス
2. **「Create New App」** → **「From a manifest」** を選択
3. ワークスペースを選んで **「Next」**
4. **「YAML」** を選択し、以下の内容を貼り付け（または `config/slack-app-manifest.yaml` をコピー）:

```yaml
display_information:
  name: 営業FBエージェント
  description: "初回面談の書き起こしからFBを生成し #dk_ca_初回面談fb に送信"

features:
  bot_user:
    display_name: 営業FBエージェント
    always_online: false
  slash_commands:
    - command: /fb
      description: 営業FB生成
      usage_hint: 書き起こしを貼り付けてFBを生成
      should_escape: false

oauth_config:
  scopes:
    bot:
      - chat:write
      - chat:write.public
      - commands

settings:
  socket_mode_enabled: true
  org_deploy_enabled: false
  interactivity:
    is_enabled: true
```

5. **「Next」** → **「Create」** でアプリを作成
6. **「Install to Workspace」** をクリックしてワークスペースにインストール
7. **Socket Mode** で App-Level Token を生成（`connections:write` スコープ）→ `SLACK_APP_TOKEN` として `.env` に保存
8. **OAuth & Permissions** から `xoxb-...` を `.env` の `SLACK_BOT_TOKEN` に保存
9. **Basic Information** の Signing Secret を `.env` の `SLACK_SIGNING_SECRET` に保存

---

## 方法B: 既存アプリをインストール

アプリがすでにある場合:

1. https://api.slack.com/apps にアクセス
2. **作成したアプリ**（例: 営業FBエージェント）をクリック
3. 左メニュー **「Install App」** をクリック
4. **「Install to Workspace」** ボタンをクリック
5. 許可画面で **「許可する」** をクリック

---

## チャンネルに招待（任意）

1. Slack で **#dk_ca_初回面談fb** を開く
2. `/invite @営業FBエージェント` と入力して送信

---

## 動作確認

1. 任意のチャンネルで `/fb` と入力
2. モーダルが開けばインストール成功

※ **アプリを起動していないと `/fb` は動きません**  
`python -m src.slack_app` を実行した状態で使ってください。
