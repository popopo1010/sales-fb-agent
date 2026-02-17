# 営業FBエージェント

初回面談の書き起こしからFBを生成し、#dk_ca_初回面談fb に送信するシステム。

## 起動

```bash
cd sales-fb-agent && source .venv/bin/activate && python3 -m src.slack_app
```

## CLI

```bash
python src/main.py data/transcripts/raw/書き起こし.txt
```
