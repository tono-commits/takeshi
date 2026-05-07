#!/usr/bin/env bash
# US market morning report - scheduled daily at 8:00 AM JST (23:00 UTC)

LOG_DIR="/home/user/takeshi/market_logs"
mkdir -p "$LOG_DIR"

DATE=$(TZ="Asia/Tokyo" date +"%Y-%m-%d")
LOG_FILE="$LOG_DIR/market_${DATE}.txt"

PROMPT='You are a financial market reporter. Search the web and provide today'\''s US stock market report in Japanese. Include:
1. Major indices (S&P 500, NASDAQ Composite, Dow Jones) - closing price and % change
2. VIX (volatility index)
3. USD/JPY exchange rate
4. Key market highlights in 2-3 sentences
Format clearly with Japanese labels. Be concise.'

echo "======================================" | tee "$LOG_FILE"
echo "  米国市場 朝の市況レポート" | tee -a "$LOG_FILE"
echo "  $(TZ='Asia/Tokyo' date '+%Y年%m月%d日 %H:%M') (JST)" | tee -a "$LOG_FILE"
echo "======================================" | tee -a "$LOG_FILE"

/opt/node22/bin/claude \
  --print \
  --allowedTools "WebSearch" \
  --bare \
  "$PROMPT" 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "レポート保存先: $LOG_FILE"
