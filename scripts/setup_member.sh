#!/bin/bash
# 営業FBエージェント メンバー用セットアップ
# このスクリプトと同じフォルダに .env を置いて実行してください。
# 管理者から受け取った .env をそのまま使えます（編集不要）

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "営業FBエージェント セットアップ"
echo "=========================================="

# .env の確認
if [ ! -f .env ]; then
    echo "[エラー] .env が見つかりません。"
    echo "管理者から受け取った .env をこのフォルダに置いてください。"
    exit 1
fi
echo "[OK] .env を確認しました"

# リポジトリをクローン（このフォルダの親に作成）
if [ ! -d "$PARENT_DIR/sales-fb-agent" ]; then
    echo "[1/4] リポジトリをクローン中..."
    (cd "$PARENT_DIR" && git clone https://github.com/popopo1010/sales-fb-agent.git)
else
    echo "[1/4] sales-fb-agent は既に存在します"
fi

cd "$PARENT_DIR/sales-fb-agent"

# .env をコピー（上書き）
echo "[2/4] .env を配置中..."
cp "$SCRIPT_DIR/.env" .env

# 仮想環境
echo "[3/4] 仮想環境を作成中..."
python3 -m venv .venv
source .venv/bin/activate

# 依存関係
echo "[4/4] 依存関係をインストール中..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

PROJECT_DIR="$PARENT_DIR/sales-fb-agent"
echo ""
echo "=========================================="
echo "【完了】セットアップが完了しました"
echo "=========================================="
echo ""
echo "起動コマンド:"
echo "  cd $PROJECT_DIR"
echo "  source .venv/bin/activate"
echo "  python3 -m src.slack_app"
echo ""
echo "起動後、Slack で /fb を試してください。"
echo ""
