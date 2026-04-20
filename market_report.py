#!/usr/bin/env python3
"""Daily US market report — fetches from Yahoo Finance (no API key needed)."""

import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

SYMBOLS = [
    ("^GSPC",    "S&P 500"),
    ("^IXIC",    "NASDAQ"),
    ("^DJI",     "Dow Jones"),
    ("^VIX",     "VIX (恐怖指数)"),
    ("^TNX",     "米10年国債利回り"),
    ("DX-Y.NYB", "ドル指数 (DXY)"),
    ("USDJPY=X", "USD/JPY"),
]


def fetch_quote(symbol: str) -> dict | None:
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        + symbol
        + "?interval=1d&range=2d"
    )
    cmd = [
        "curl", "-s", "-L",
        "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H", "Accept: application/json",
        "-H", "Accept-Language: en-US,en;q=0.9",
        "--max-time", "10",
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        meta = data["chart"]["result"][0]["meta"]
        return meta
    except Exception:
        return None


def arrow(change: float) -> str:
    if change > 0:
        return "▲"
    elif change < 0:
        return "▼"
    return "─"


def color(change: float, text: str) -> str:
    """ANSI color: green for positive, red for negative."""
    if change > 0:
        return f"\033[32m{text}\033[0m"
    elif change < 0:
        return f"\033[31m{text}\033[0m"
    return text


def format_report(use_color: bool = True) -> str:
    now = datetime.now(JST)
    lines = [
        "=" * 56,
        f"  米国市場 朝の市況レポート",
        f"  {now.strftime('%Y年%m月%d日 %H:%M')} (JST)",
        "=" * 56,
    ]

    for symbol, name in SYMBOLS:
        meta = fetch_quote(symbol)
        if meta is None:
            lines.append(f"  {name:<22} データ取得失敗")
            continue

        price = meta.get("regularMarketPrice", meta.get("previousClose", 0))
        prev  = meta.get("chartPreviousClose", meta.get("previousClose", price))

        if prev and prev != 0:
            change     = price - prev
            change_pct = (change / prev) * 100
        else:
            change = change_pct = 0.0

        sign = "+" if change >= 0 else ""
        mark = arrow(change)
        change_str = f"{mark} {sign}{change:.2f} ({sign}{change_pct:.2f}%)"

        if use_color:
            change_str = color(change, change_str)

        lines.append(f"  {name:<22} {price:>10,.2f}  {change_str}")

    lines += ["=" * 56, ""]
    return "\n".join(lines)


if __name__ == "__main__":
    use_color = "--no-color" not in sys.argv
    print(format_report(use_color=use_color))
