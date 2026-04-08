#!/bin/bash
# 米国市場の市況レポートスクリプト
# 毎朝8:00 JST (23:00 UTC) に実行されます

LOG_DIR="$(dirname "$0")/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/market_$(date +%Y%m%d).log"

PROMPT="今日の米国株式市場の市況を日本語で報告してください。以下の情報を含めてください：
1. 主要指数（S&P 500、NASDAQ、ダウ平均）の前日終値・変動幅・変動率
2. 市場全体のトレンド・センチメント
3. 主要な市場を動かしたニュースや出来事
4. セクター別のパフォーマンス（上昇・下落セクター）
5. 本日の注目ポイント・見通し

現在の日時: $(TZ='Asia/Tokyo' date '+%Y年%m月%d日 %H:%M JST')"

echo "======================================"
echo "米国市場 朝の市況レポート"
echo "$(TZ='Asia/Tokyo' date '+%Y年%m月%d日 %H:%M JST')"
echo "======================================"

claude -p --allowedTools "WebSearch,WebFetch" "$PROMPT"

echo ""
echo "レポート生成完了: $(date)"
