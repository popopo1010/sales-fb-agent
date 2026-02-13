#!/bin/bash
# 営業FBエージェント 実行スクリプト
# 使い方: ./run.sh data/transcripts/raw/書き起こし.txt
#        ./run.sh -o data/transcripts/raw/書き起こし.txt  # 出力のみ（Slack送信しない）

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "[INFO] 仮想環境が見つかりません。作成します..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt -q
else
  source .venv/bin/activate
fi

python src/main.py "$@"
