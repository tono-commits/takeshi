#!/usr/bin/env bash
# 毎朝8:00（JST / UTC 23:00）に米国市場市況を実行するcronジョブを設定するスクリプト

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/market_update.py"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/market_update.log"

# ログディレクトリ作成
mkdir -p "$LOG_DIR"

# cronエントリ（JST 08:00 = UTC 23:00）
CRON_ENTRY="0 23 * * * /usr/bin/python3 $SCRIPT_PATH >> $LOG_FILE 2>&1"

echo "=== 米国市場 市況 cron セットアップ ==="
echo ""
echo "追加するcronエントリ:"
echo "  $CRON_ENTRY"
echo ""

# 既存のcrontabに追加（重複なし）
(crontab -l 2>/dev/null | grep -v "market_update.py" ; echo "$CRON_ENTRY") | crontab -

echo "✓ cronジョブを設定しました。"
echo "  実行タイミング: 毎日 23:00 UTC（= 08:00 JST）"
echo "  ログ出力先:     $LOG_FILE"
echo ""
echo "手動実行:"
echo "  python3 $SCRIPT_PATH"
echo ""
echo "ログ確認:"
echo "  tail -f $LOG_FILE"
echo ""
echo "cron確認:"
echo "  crontab -l"
