#!/bin/bash
# 米国市場の朝8:00 市況レポート
# 毎日 JST 8:00 (UTC 23:00) に実行される

LOG_DIR="/home/user/takeshi/logs"
LOG_FILE="$LOG_DIR/market_report_$(date +%Y%m%d).log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$LOG_DIR"

PROMPT="今日の米国市場の市況を日本語で簡潔にまとめてください。以下の情報を含めてください：
1. 主要指数（S&P 500、NASDAQ、ダウ平均）の前日終値と騰落率
2. 主要な市場ニュース・イベント（FRB動向、経済指標など）
3. 注目セクターや個別銘柄の動き
4. 本日の注目ポイント

日付: $(TZ='Asia/Tokyo' date '+%Y年%m月%d日 %H:%M JST')"

echo "========================================" | tee -a "$LOG_FILE"
echo "米国市場 朝の市況レポート" | tee -a "$LOG_FILE"
echo "$(TZ='Asia/Tokyo' date '+%Y年%m月%d日 %H:%M JST')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Claude CLIを使ってweb検索で市況を取得
claude --dangerously-skip-permissions -p "$PROMPT" \
  --allowedTools "WebSearch,WebFetch" \
  2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "レポート完了: $(date)" | tee -a "$LOG_FILE"
