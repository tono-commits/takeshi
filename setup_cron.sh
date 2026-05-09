#!/usr/bin/env bash
# 毎朝8:00に市況レポートを実行するcronジョブを登録するセットアップスクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$(which python3)"
MARKET_SCRIPT="$SCRIPT_DIR/market_report.py"
LOG_FILE="$SCRIPT_DIR/market_log.txt"

CRON_JOB="0 8 * * * $PYTHON $MARKET_SCRIPT --log >> $LOG_FILE 2>&1"

# 既存のcronジョブに重複追加しないようにチェック
if crontab -l 2>/dev/null | grep -qF "$MARKET_SCRIPT"; then
    echo "既にcronジョブが登録されています:"
    crontab -l | grep "$MARKET_SCRIPT"
    exit 0
fi

# 既存のcrontabに追記
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "cronジョブを登録しました:"
echo "  $CRON_JOB"
echo ""
echo "毎朝 8:00 に市況レポートが $LOG_FILE に保存されます。"
echo ""
echo "確認コマンド:  crontab -l"
echo "削除コマンド:  crontab -l | grep -v market_report | crontab -"
