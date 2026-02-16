# Railway デプロイ手順（/fb を全員が使えるようにする）

Git push で自動デプロイし、Slack の `/fb` コマンドをメンバー全員がいつでも使えるようにする手順です。

---

## 前提

- GitHub にリポジトリがあること
- Slack アプリは作成済み（`SLACK_BOT_TOKEN`、`SLACK_APP_TOKEN`、`SLACK_SIGNING_SECRET` を取得済み）
- ローカルで `/fb` が動作していること

---

## 1. Railway を使う理由

| 項目 | 説明 |
|------|------|
| **Git 連携** | push するだけで自動デプロイ |
| **Socket Mode 対応** | Web サーバー不要。常時接続のワーカーとして動作 |
| **無料枠** | 月 $5 分のクレジット。軽い用途なら十分 |
| **環境変数** | `.env` 相当の設定を Web 画面で管理 |

※無料枠では一定時間でスリープする場合あり。常時稼働が必要なら有料プラン（$5/月〜）を検討。

---

## 2. Railway プロジェクトの作成

1. https://railway.app にアクセス
2. **Login** → GitHub でログイン
3. **New Project** をクリック
4. **Deploy from GitHub repo** を選択
5. リポジトリ `sales-fb-agent` を選択（なければ「Configure GitHub App」で権限を付与）
6. リポジトリが選択されると自動でビルドが開始される

---

## 3. 起動コマンドの設定

Railway はデフォルトで `web` プロセスを探すが、このアプリは Web サーバーを持たない。**起動コマンドを明示**する。

1. デプロイされたサービスをクリック
2. **Settings** タブを開く
3. **Build** セクションで:
   - **Builder**: Nixpacks（デフォルト）
   - **Build Command**: （空でOK。`pip install -r requirements.txt` は自動実行される）
4. **Deploy** セクションで:
   - **Start Command**: `python -m src.slack_app`
   - または **Custom Start Command** を有効にして上記を入力

※`Procfile` に `worker: python -m src.slack_app` を書いている場合、Railway が `worker` を検出しないことがある。その場合は **Start Command** で直接指定する。

---

## 4. 環境変数の設定

1. サービス画面で **Variables** タブを開く
2. **+ New Variable** で以下を追加（`.env` と同じ値）:

| 変数名 | 値 | 備考 |
|--------|-----|------|
| `SLACK_BOT_TOKEN` | `xoxb-...` | OAuth & Permissions から |
| `SLACK_APP_TOKEN` | `xapp-1-...` | Socket Mode → App-Level Tokens |
| `SLACK_SIGNING_SECRET` | （英数字） | Basic Information から |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Claude API |
| `SLACK_CHANNEL` | `C0AELMP88Q6` | チャンネルID（推奨）。省略時はこちらがデフォルト |

※`SLACK_WEBHOOK_URL` は `/fb` には不要だが、他機能で使うなら追加。

---

## 5. デプロイの確認

1. **Deployments** タブで最新のデプロイを選択
2. **View Logs** でログを確認
3. 次のメッセージが出ていれば成功:

   ```
   [INFO] Slack アプリを起動しました。チャンネルで /fb を試してください。
   ```

4. Slack で `/fb` を実行し、モーダルが開くことを確認

---

## 6. 自動デプロイ（Git push 連携）

デフォルトで **main ブランチへの push** で自動デプロイされる。

```
git add .
git commit -m "feat: Railway デプロイ設定追加"
git push origin main
```

Railway のダッシュボードで新しいデプロイが開始され、数分で反映される。

---

## 7. トラブルシューティング

| 症状 | 対策 |
|------|------|
| ビルドが失敗する | `runtime.txt` で `python-3.11` を指定。Python 3.14 は Railway で未対応の可能性 |
| 起動直後に落ちる | **Variables** で全環境変数が正しく設定されているか確認 |
| `/fb` が dispatch_failed | ログでエラー確認。多くの場合 `SLACK_APP_TOKEN` 未設定 |
| 一定時間で停止する | 無料枠のスリープ。有料プランへアップグレード |

---

## 8. 参考リンク

- [Railway Docs - Build and Start Commands](https://docs.railway.com/reference/build-and-start-commands)
- [Slack Bolt for Python - Socket Mode](https://slack.dev/bolt-python/concepts#socket-mode)
