# 本番実装チェックリスト

## 1. 事前確認（スクリプトが正しく動くか）

### 一括検証（推奨）

```bash
cd sales-fb-agent
source .venv/bin/activate
python scripts/run_all_tests.py
```

全5項目を一括で検証する。

### Step 1: Slack連携の検証

```bash
python scripts/verify_slack.py
```

**期待結果:** `【成功】#dk_ca_初回面談fb を確認してください。` と表示され、#dk_ca_初回面談fb にメッセージが投稿される。

**失敗した場合:**
- `.env` に `SLACK_WEBHOOK_URL` が正しく設定されているか確認
- Webhook URL が #dk_ca_初回面談fb 用か確認

---

### Step 1.5: API診断（LLMが動かない場合）

```bash
python scripts/diagnose_api.py
```

モデル一覧の取得・テスト呼び出しを行う。404エラー時はモデル名を確認。

---

### Step 2: 書き起こし読み込みの検証

```bash
python -c "
from src.utils.loader import load_transcript
t = load_transcript('data/transcripts/raw/test_slack_20250213.txt')
print(f'OK: {len(t)} 文字読み込み')
"
```

**期待結果:** `OK: 189 文字読み込み` などと表示される。

---

### Step 3: 一連の流れ（LLMを除く）の検証

```bash
python scripts/test_full_flow.py
```

**期待結果:** `[OK] 一連の流れが正常に完了しました。` と表示され、#dk_ca_初回面談fb にサンプルFBが投稿される。

---

## 2. 本番実装の開始ポイント

### ここから始める

| 順番 | 実施内容 | コマンド/場所 |
|------|----------|---------------|
| 1 | **APIクレジットの確保** | [console.anthropic.com](https://console.anthropic.com) でクレジット追加 |
| 2 | **書き起こしを配置** | `data/transcripts/raw/` に `.txt` で保存 |
| 3 | **実行** | `python src/main.py data/transcripts/raw/ファイル名.txt` |

---

## 3. 本番で使う流れ

```
1. 初回面談の音声を文字起こし
   ↓
2. 書き起こしを data/transcripts/raw/YYYYMMDD_顧客名_担当者.txt に保存
   ↓
3. python src/main.py data/transcripts/raw/YYYYMMDD_顧客名_担当者.txt を実行
   ↓
4. #dk_ca_初回面談fb でFBを確認
```

---

## 4. 本番前のチェックリスト

- [ ] `scripts/verify_slack.py` で Slack 連携が成功している
- [ ] `scripts/test_full_flow.py` で一連の流れが成功している
- [ ] Anthropic API にクレジットが入っている
- [ ] `.env` に `ANTHROPIC_API_KEY` と `SLACK_WEBHOOK_URL` が設定されている
- [ ] 書き起こしの形式（CA/候補者の発言など）が想定どおりか

---

## 5. 他メンバーへの展開

1. プロジェクトを共有（Git など）
2. 各メンバーが `pip install -r requirements.txt` を実行
3. `.env` を共有（Webhook は共通、APIキーは各自または共通で1つ）
4. `scripts/verify_slack.py` で動作確認
