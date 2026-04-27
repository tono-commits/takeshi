#!/bin/bash
# 米国市場 朝の市況レポート 実行スクリプト
# このファイルをcronから呼び出す

# API keyの読み込み（~/.market_briefing_envから）
ENV_FILE="$HOME/.market_briefing_env"
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

# API keyが設定されていなければ終了
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY が設定されていません。"
    echo "~/.market_briefing_env に以下を記載してください:"
    echo "  export ANTHROPIC_API_KEY=sk-ant-your-key-here"
    exit 1
fi

export ANTHROPIC_API_KEY

# ログファイルに出力
LOG_DIR="$HOME/takeshi/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/market_$(date +%Y%m%d).log"

python3 "$HOME/takeshi/market_briefing.py" 2>&1 | tee "$LOG_FILE"
