#!/usr/bin/env python3
"""Daily US market morning report."""

import sys
from datetime import datetime
import yfinance as yf

TICKERS = {
    "S&P 500":      "^GSPC",
    "Dow Jones":    "^DJI",
    "NASDAQ":       "^IXIC",
    "Russell 2000": "^RUT",
    "VIX":          "^VIX",
    "USD/JPY":      "USDJPY=X",
    "米10年債利回り": "^TNX",
    "WTI原油":      "CL=F",
    "金":           "GC=F",
}

def fetch(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        if hist.empty or len(hist) < 1:
            return None, None, None
        latest = hist["Close"].iloc[-1]
        prev   = hist["Close"].iloc[-2] if len(hist) >= 2 else latest
        change = latest - prev
        pct    = (change / prev) * 100 if prev != 0 else 0
        return latest, change, pct
    except Exception:
        return None, None, None

def arrow(pct: float) -> str:
    return "▲" if pct >= 0 else "▼"

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n{'='*52}")
    print(f"  米国市場 朝の市況レポート  {now}")
    print(f"{'='*52}")

    any_success = False
    for name, symbol in TICKERS.items():
        price, change, pct = fetch(symbol)
        if price is None:
            print(f"  {name:<14} データ取得失敗")
            continue
        any_success = True
        sign = "+" if pct >= 0 else ""
        print(f"  {name:<14} {price:>10,.2f}  {arrow(pct)} {sign}{pct:.2f}%  ({sign}{change:,.2f})")

    print(f"{'='*52}\n")
    if not any_success:
        print("  ※ ネットワーク接続を確認してください。\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
