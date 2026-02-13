# 営業FBエージェント 使い方（メンバー向け）

初回面談の書き起こしからFBを生成し、#dk_ca_fb に送信するツールです。

---

## シェア用（Slackにコピペ）

```
【営業FBエージェントの使い方】

1. チャンネルで /fb と入力
2. モーダルに書き起こしを貼り付け
3. 「FBを生成」をクリック
4. 数十秒後、#dk_ca_fb にFBが投稿されます

※ファイルから実行する場合:
  cd sales-fb-agent && source .venv/bin/activate
  python src/main.py data/transcripts/raw/書き起こし.txt
```

---

## 使い方（Slack）

1. 任意のチャンネルで **`/fb`** と入力
2. モーダルが開いたら、**書き起こしを貼り付け**
3. **「FBを生成」** をクリック
4. 数十秒後、#dk_ca_fb にFBが投稿される

> ⚠️ `/fb` が使えるかは、管理者がアプリを起動しているかによります。使えない場合は管理者に連絡してください。

---

## 使い方（CLI・ファイルから）

書き起こしを `.txt` ファイルで持っている場合：

```bash
cd sales-fb-agent
source .venv/bin/activate
python src/main.py data/transcripts/raw/書き起こし.txt
```

書き起こしは `data/transcripts/raw/` に置いてください。

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

- **FBが投稿されない** → APIキーやSlack設定を確認。管理者に連絡
- **内容を変えたい** → `config/fb_format.md` を編集（管理者向け）
