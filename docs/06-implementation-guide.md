# 実装ガイド

## 1. 前提条件

- Python 3.10 以上
- OpenAI API キー または Anthropic API キー
- Slack Bot Token（`chat:write` スコープ）
- PSSマニュアル・オペレーションマニュアル（`reference/` に格納）

---

## 2. ディレクトリ

プロジェクト内で以下が用意済み（`00-repository-structure.md` 参照）。

```
reference/pss/
reference/operations/
data/transcripts/raw/
data/feedback/
config/prompts/
src/{agent,slack,utils}/
tests/
```

---

## 3. PSS・オペレーションマニュアルの格納

### 3.1 格納場所

| ドキュメント | パス |
|--------------|------|
| **PSSマニュアル** | `reference/pss/` |
| **オペレーションマニュアル** | `reference/operations/` |

### 3.2 推奨ファイル構成

```
reference/
├── pss/
│   ├── pss-sales-scheme.md    # PSS営業スキーム本体
│   ├── evaluation-criteria.md # 評価基準（任意）
│   └── assets/               # 図表（任意）
└── operations/
    └── operation-manual.md   # オペレーションマニュアル
```

### 3.3 読み込み例（Python）

```python
import os

def load_reference_docs(base_path: str) -> str:
    content = []
    for root, _, files in os.walk(base_path):
        for f in files:
            if f.endswith(('.md', '.txt')):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as fp:
                    content.append(f"## {os.path.basename(path)}\n\n{fp.read()}")
    return "\n\n".join(content)

pss_content = load_reference_docs("reference/pss")
ops_content = load_reference_docs("reference/operations")
```

---

## 4. プロンプト設計

### 4.1 FB出力形式（単一ソース）

FB出力形式は **config/fb_format.md** で定義。8項目（良い点・改善点・ニーズの整理・意思決定6カテゴリ・年収相場との整合性・障壁・総評・残論点）の詳細はこのファイルを参照すること。

### 4.2 プロンプト構築

```python
def build_prompt(transcript: str, pss_dir: str, ops_dir: str) -> str:
    pss_content = load_reference_docs(pss_dir)
    ops_content = load_reference_docs(ops_dir)
    fb_format = (root / "config" / "fb_format.md").read_text(encoding="utf-8")
    template = (root / "config" / "prompts" / "fb_generation.txt").read_text(encoding="utf-8")
    return template.format(
        pss_content=pss_content,
        ops_content=ops_content,
        transcript=transcript,
        fb_format=fb_format,
    )
```

---

## 5. LLM連携

- **Anthropic**: デフォルトモデル `claude-sonnet-4-20250514`
- **OpenAI**: デフォルトモデル `gpt-4o`

```python
# OpenAI の場合
from openai import OpenAI
client = OpenAI()

def generate_feedback(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content
```

---

## 6. Slack送信

```python
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_to_slack(text: str, channel: str) -> bool:
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    try:
        client.chat_postMessage(channel=channel, text=text)
        return True
    except SlackApiError as e:
        print(f"Slack error: {e.response['error']}")
        return False
```

---

## 7. メインパイプライン

```python
def main(transcript_path: str, slack_channel: str):
    transcript = load_transcript(transcript_path)
    prompt = build_prompt(
        transcript,
        pss_dir="reference/pss",
        ops_dir="reference/operations"
    )
    fb = generate_feedback(prompt)
    send_to_slack(fb, slack_channel)
```

---

## 8. 環境変数

`.env.example`:

```env
OPENAI_API_KEY=sk-...
# または ANTHROPIC_API_KEY=sk-ant-...

SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=#sales-feedback
# または SLACK_USER_ID=U01234567 でDM
```

---

## 9. 依存関係

`requirements.txt`:

```
openai>=1.0.0
slack-sdk>=3.0.0
python-dotenv>=1.0.0
```

---

## 10. 実行例

```bash
# 環境変数読み込み
export $(cat .env | xargs)

# 実行
python src/main.py --input data/transcripts/sample.txt --channel "#sales-fb"
```
