#!/bin/bash
# Set up daily US market report at 8:00 AM Japan time (JST = UTC+9)
# Cron runs in UTC by default, so 8:00 JST = 23:00 UTC (previous day)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$SCRIPT_DIR/market_report.py"
LOG="$SCRIPT_DIR/market_report.log"

CRON_LINE="0 23 * * * python3 $SCRIPT >> $LOG 2>&1"

# Remove existing entry if present, then add fresh
( crontab -l 2>/dev/null | grep -v "market_report.py" ; echo "$CRON_LINE" ) | crontab -

echo "cronジョブを設定しました:"
echo "  実行時刻: 毎日 8:00 JST (= 23:00 UTC)"
echo "  スクリプト: $SCRIPT"
echo "  ログ: $LOG"
echo ""
echo "現在のcron設定:"
crontab -l
