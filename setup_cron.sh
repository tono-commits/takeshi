#!/usr/bin/env bash
# Installs a cron job to run the market report at 8:00 AM JST (= 23:00 UTC).
# Usage:
#   ./setup_cron.sh                          # use yfinance (no API key)
#   ALPHAVANTAGE_API_KEY=xxx ./setup_cron.sh # use Alpha Vantage

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$(which python3)"
LOG="$SCRIPT_DIR/market_report.log"

# Build the cron line
# 8:00 AM JST = 23:00 UTC (previous calendar day)
# Cron format: minute hour day month weekday
CRON_TIME="0 23 * * *"  # runs every day at 23:00 UTC = 08:00 JST next day

if [[ -n "${ALPHAVANTAGE_API_KEY:-}" ]]; then
    ENV_PREFIX="ALPHAVANTAGE_API_KEY=$ALPHAVANTAGE_API_KEY "
else
    ENV_PREFIX=""
fi

CRON_CMD="$CRON_TIME ${ENV_PREFIX}${PYTHON} ${SCRIPT_DIR}/market_report.py >> ${LOG} 2>&1"

# Remove any existing entry for market_report.py, then add the new one
( crontab -l 2>/dev/null | grep -v "market_report.py" ; echo "$CRON_CMD" ) | crontab -

echo "Cron job registered:"
echo "  $CRON_CMD"
echo ""
echo "Log file: $LOG"
echo "Test run now? [y/N]"
read -r answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    ${ENV_PREFIX}${PYTHON} "${SCRIPT_DIR}/market_report.py"
fi
