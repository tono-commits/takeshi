#!/usr/bin/env bash
# 米国市場 朝8:00 市況レポート — cron セットアップ
# 実行: bash setup_cron.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$(command -v python3 || command -v python)"
LOG_FILE="$SCRIPT_DIR/market_briefing.log"

if [ -z "$PYTHON" ]; then
  echo "エラー: python3 が見つかりません。" >&2
  exit 1
fi

# pytz がなければインストール
"$PYTHON" -c "import pytz" 2>/dev/null || {
  echo "pytz をインストールします..."
  "$PYTHON" -m pip install pytz --quiet
}

echo "スクリプトパス : $SCRIPT_DIR/market_briefing.py"
echo "Python        : $PYTHON"
echo "ログ出力先    : $LOG_FILE"
echo ""

# cron エントリ (毎朝 8:00 JST = UTC 23:00 前日)
# ※ システムが JST (UTC+9) の場合は "0 8 * * *"、UTC の場合は "0 23 * * *"
read -rp "システムのタイムゾーンは JST (日本時間) ですか？ [y/N]: " tz_jst
if [[ "$tz_jst" =~ ^[Yy]$ ]]; then
  CRON_TIME="0 8 * * *"
  TZ_NOTE="JST (朝8:00)"
else
  CRON_TIME="0 23 * * *"
  TZ_NOTE="UTC (23:00 = 翌朝 8:00 JST)"
fi

CRON_CMD="$PYTHON $SCRIPT_DIR/market_briefing.py >> $LOG_FILE 2>&1"
CRON_ENTRY="$CRON_TIME $CRON_CMD"

# 既存の crontab を取得し、重複がなければ追加
TMPFILE=$(mktemp)
crontab -l 2>/dev/null > "$TMPFILE" || true

if grep -qF "market_briefing.py" "$TMPFILE"; then
  echo "cron エントリは既に登録されています。"
else
  echo "$CRON_ENTRY" >> "$TMPFILE"
  crontab "$TMPFILE"
  echo "cron に登録しました: $TZ_NOTE"
  echo "  $CRON_ENTRY"
fi

rm -f "$TMPFILE"
echo ""
echo "今すぐテスト実行しますか？"
read -rp "[y/N]: " do_test
if [[ "$do_test" =~ ^[Yy]$ ]]; then
  "$PYTHON" "$SCRIPT_DIR/market_briefing.py"
fi
