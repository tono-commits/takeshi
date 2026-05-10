#!/usr/bin/env python3
"""US market daily report - fetches and displays key market indicators."""

import json
import sys
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Accept": "application/json",
}

INDICES = [
    ("^GSPC",   "S&P 500    "),
    ("^DJI",    "Dow Jones  "),
    ("^IXIC",   "Nasdaq     "),
    ("^VIX",    "VIX (恐怖指数)"),
]

ASSETS = [
    ("GC=F",    "Gold (金)   "),
    ("CL=F",    "WTI原油     "),
    ("USDJPY=X","USD/JPY    "),
]

def fetch_yahoo(symbol):
    encoded = symbol.replace("^", "%5E").replace("=", "%3D")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?interval=1d&range=2d"
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        result = data["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        closes = [c for c in closes if c is not None]
        if len(closes) < 2:
            return None, None, None
        last, prev = closes[-1], closes[-2]
        change = last - prev
        pct = (change / prev) * 100
        return last, change, pct
    except (URLError, HTTPError, KeyError, IndexError, json.JSONDecodeError):
        return None, None, None

def arrow(change):
    return "▲" if change >= 0 else "▼"

def fmt_row(name, price, chg, pct):
    sign = "+" if chg >= 0 else ""
    return f"  {name}: {price:>12,.2f}  {arrow(chg)} {sign}{chg:,.2f} ({sign}{pct:.2f}%)"

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("=" * 56)
    print(f"  米国市場 市況レポート  {now}")
    print("=" * 56)

    any_failed = False

    print("\n【主要指数】")
    for symbol, name in INDICES:
        price, chg, pct = fetch_yahoo(symbol)
        if price is None:
            print(f"  {name}: データ取得失敗")
            any_failed = True
        else:
            print(fmt_row(name, price, chg, pct))

    print("\n【商品・為替】")
    for symbol, name in ASSETS:
        price, chg, pct = fetch_yahoo(symbol)
        if price is None:
            print(f"  {name}: データ取得失敗")
            any_failed = True
        else:
            print(fmt_row(name, price, chg, pct))

    print("\n" + "=" * 56)

    if any_failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
