#!/bin/bash
# Setup daily US market report cron job at 8:00 AM

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$SCRIPT_DIR/market_report.py"
LOG="$SCRIPT_DIR/market_report.log"
PYTHON="$(which python3)"

chmod +x "$SCRIPT"

# Build cron entry: 8:00 AM every weekday (Mon-Fri)
CRON_ENTRY="0 8 * * 1-5 $PYTHON $SCRIPT >> $LOG 2>&1"

# Add only if not already present
if crontab -l 2>/dev/null | grep -qF "$SCRIPT"; then
    echo "Cron job already exists. No changes made."
else
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo "Cron job added:"
    echo "  $CRON_ENTRY"
fi

echo ""
echo "Run manually anytime with:"
echo "  python3 $SCRIPT"
