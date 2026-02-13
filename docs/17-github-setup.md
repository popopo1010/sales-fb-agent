# GitHub 連携手順

リポジトリを GitHub に push し、Railway などで自動デプロイするための手順です。

---

## 前提

- Git は初期化済み（`git init` 済み）
- 初回コミット済み

---

## 1. GitHub でリポジトリを作成

1. https://github.com にログイン
2. **+** → **New repository**
3. リポジトリ名（例: `sales-fb-agent`）
4. **Private** または **Public** を選択
5. **README とかは追加しない**（既にローカルにコードがあるため）
6. **Create repository** をクリック

---

## 2. リモートを追加して push

作成後、GitHub に表示されるコマンドを実行。または以下を実行：

```bash
cd /Users/ikeobook15/work/sales-fb-agent

# リモートを追加（URL は自分のリポジトリに合わせて変更）
git remote add origin https://github.com/あなたのユーザー名/sales-fb-agent.git

# main ブランチを push
git push -u origin main
```

**SSH を使う場合：**

```bash
git remote add origin git@github.com:あなたのユーザー名/sales-fb-agent.git
git push -u origin main
```

---

## 3. 以降の開発フロー

```bash
# 変更を追加
git add .

# コミット
git commit -m "feat: 〇〇を追加"

# push（GitHub に反映）
git push
```

---

## 4. Railway との連携

GitHub に push した後、Railway で：

1. **New Project** → **Deploy from GitHub repo**
2. `sales-fb-agent` を選択
3. 以降、`git push` するたびに自動デプロイされる

詳細は [docs/16-railway-deploy.md](16-railway-deploy.md) を参照。

---

## 注意

- `.env` は `.gitignore` で除外済み。**トークンは GitHub に push されない**
- 機密の参照ドキュメントは必要に応じて `.gitignore` に追加
