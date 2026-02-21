#!/bin/bash
# CA FB + RA FB を一括起動
# 使い方: ./scripts/start_all_fb.sh  または  bash scripts/start_all_fb.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CA_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RA_ROOT="${RA_FB_PATH:-/Users/ikeobook15/RA_FBシステム}"

if [[ ! -d "$RA_ROOT" ]]; then
  echo "RA_FBシステム が見つかりません: $RA_ROOT"
  echo "環境変数 RA_FB_PATH でパスを指定できます"
  exit 1
fi

cleanup() {
  echo ""
  echo "終了しています..."
  kill $CA_PID $RA_PID 2>/dev/null || true
  exit 0
}

trap cleanup SIGINT SIGTERM

echo "=========================================="
echo "CA FB (sales-fb-agent) + RA FB を起動"
echo "=========================================="
echo "CA: $CA_ROOT"
echo "RA: $RA_ROOT"
echo ""

# CA FB 起動
(
  cd "$CA_ROOT"
  if [[ -d .venv ]]; then
    source .venv/bin/activate
  elif [[ -d venv ]]; then
    source venv/bin/activate
  fi
  exec python3 -m src.slack_app
) &
CA_PID=$!
echo "[CA] 起動中... PID=$CA_PID"

# RA FB 起動
(
  cd "$RA_ROOT"
  if [[ -d .venv ]]; then
    source .venv/bin/activate
  elif [[ -d venv ]]; then
    source venv/bin/activate
  fi
  exec python3 scripts/slack_server.py
) &
RA_PID=$!
echo "[RA] 起動中... PID=$RA_PID"

echo ""
echo "両方起動しました。Ctrl+C で終了します。"
echo "  CA: /fb (初回面談FB)"
echo "  RA: /rafb_call (初回架電FB), /rafb_mtg (法人面談FB)"
echo ""

wait
