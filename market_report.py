#!/usr/bin/env python3
"""毎朝の米国市場レポートを生成・表示するスクリプト

使い方:
  python3 market_report.py              # ターミナルに表示
  python3 market_report.py --log        # ログファイルにも保存
  python3 market_report.py --notify     # デスクトップ通知も送信 (notify-send必須)
"""

import sys
import os
import argparse
import subprocess
from datetime import datetime

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

try:
    import urllib.request, json
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False


TICKERS = {
    "S&P 500":      "^GSPC",
    "NASDAQ":       "^IXIC",
    "DOW":          "^DJI",
    "VIX (恐怖指数)":  "^VIX",
    "米10年債利回り":    "^TNX",
    "ドル円":          "JPY=X",
    "金":             "GC=F",
    "WTI原油":        "CL=F",
}

LOG_PATH = os.path.join(os.path.dirname(__file__), "market_log.txt")


def fetch_yfinance(symbol: str) -> dict | None:
    if not HAS_YFINANCE:
        return None
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="2d")
        if hist.empty:
            return None
        close = float(hist["Close"].iloc[-1])
        prev  = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else close
        change = close - prev
        pct    = (change / prev) * 100 if prev else 0.0
        return {"close": close, "change": change, "pct": pct}
    except Exception:
        return None


def fetch_yahoo_api(symbol: str) -> dict | None:
    """Yahoo Finance v8 APIを直接叩く (yfinanceが失敗した場合のフォールバック)"""
    if not HAS_URLLIB:
        return None
    try:
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/"
            f"{symbol.replace('^', '%5E')}?interval=1d&range=2d"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        closes = [c for c in closes if c is not None]
        if len(closes) < 1:
            return None
        close = closes[-1]
        prev  = closes[-2] if len(closes) >= 2 else close
        change = close - prev
        pct    = (change / prev) * 100 if prev else 0.0
        return {"close": close, "change": change, "pct": pct}
    except Exception:
        return None


def fetch(symbol: str) -> dict | None:
    return fetch_yfinance(symbol) or fetch_yahoo_api(symbol)


def arrow(pct: float) -> str:
    return "▲" if pct >= 0 else "▼"


def build_report() -> str:
    now = datetime.now()
    lines = []
    lines.append("=" * 56)
    lines.append(f"  米国市場 朝の市況レポート  {now.strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 56)

    for name, sym in TICKERS.items():
        data = fetch(sym)
        if data is None:
            lines.append(f"  {name:<18} データ取得失敗")
            continue
        a    = arrow(data["pct"])
        sign = "+" if data["change"] >= 0 else ""
        lines.append(
            f"  {name:<18} {data['close']:>11,.2f}  "
            f"{a} {sign}{data['change']:.2f} ({sign}{data['pct']:.2f}%)"
        )

    lines.append("=" * 56)
    return "\n".join(lines)


def send_notification(title: str, body: str) -> None:
    try:
        subprocess.run(["notify-send", title, body], check=True, timeout=5)
    except Exception:
        pass  # 通知ツール未インストール環境では無視


def main():
    parser = argparse.ArgumentParser(description="米国市場 朝の市況レポート")
    parser.add_argument("--log",    action="store_true", help=f"ログ保存 ({LOG_PATH})")
    parser.add_argument("--notify", action="store_true", help="デスクトップ通知を送信")
    args = parser.parse_args()

    report = build_report()
    print(report)

    if args.log:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(report + "\n\n")
        print(f"  → ログ保存: {LOG_PATH}")

    if args.notify:
        first_line = [l for l in report.splitlines() if l.strip() and "=" not in l]
        send_notification("米国市場 朝の市況", "\n".join(first_line[:5]))


if __name__ == "__main__":
    main()
