#!/bin/bash
# 管理者用: メンバーに渡すパッケージを作成
# 実行すると member-package/ が作成され、中に .env と setup_member.sh が入ります。
# このフォルダを zip にして、Slack DM 等でメンバーに送ってください。

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

PACKAGE_DIR="member-package"
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# .env の確認
if [ ! -f .env ]; then
    echo "[エラー] .env が見つかりません。プロジェクト直下に .env を置いてください。"
    exit 1
fi

# パッケージにコピー
cp .env "$PACKAGE_DIR/"
cp scripts/setup_member.sh "$PACKAGE_DIR/"
chmod +x "$PACKAGE_DIR/setup_member.sh"

# 使い方 README
cat > "$PACKAGE_DIR/README.txt" << 'EOF'
【営業FBエージェント メンバー用】

※ .env は編集不要です。最初から設定済みです。

■ セットアップ（1回だけ）
1. このフォルダ（member-package）を任意の場所に解凍
2. ターミナルでこのフォルダに移動して実行:
   cd （解凍したフォルダのパス）
   chmod +x setup_member.sh
   ./setup_member.sh
3. 完了メッセージに表示される起動コマンドを実行

■ 起動（毎回）
セットアップ時に表示されたコマンドを実行。
（解凍したフォルダの1つ上の階層に sales-fb-agent ができます）

■ Slack で /fb を入力して使う
EOF

echo "=========================================="
echo "メンバー用パッケージを作成しました"
echo "=========================================="
echo ""
echo "作成場所: $PROJECT_ROOT/$PACKAGE_DIR/"
echo ""
echo "■ メンバーに渡す手順"
echo "1. 次のコマンドで zip を作成:"
echo "   cd $PROJECT_ROOT && zip -r member-package.zip member-package"
echo ""
echo "2. member-package.zip を Slack DM 等でメンバーに送る"
echo ""
echo "3. メンバーは解凍後、フォルダ内で ./setup_member.sh を実行"
echo "   （.env は編集不要・そのまま使える）"
echo ""
