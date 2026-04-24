#!/usr/bin/env python3
"""Daily US market morning report — designed to run via cron at 8:00 AM JST."""

import sys
from datetime import datetime

def get_data_yfinance():
    import yfinance as yf

    TICKERS = {
        "S&P 500":          "^GSPC",
        "Dow Jones":        "^DJI",
        "NASDAQ":           "^IXIC",
        "VIX (恐怖指数)":   "^VIX",
        "USD/JPY":          "JPY=X",
        "Gold (金)":        "GC=F",
        "Crude Oil (原油)": "CL=F",
        "10年米国債利回り": "^TNX",
    }

    results = []
    for name, symbol in TICKERS.items():
        try:
            info = yf.Ticker(symbol).fast_info
            price = info.last_price
            prev  = info.previous_close
            if price is None or prev is None:
                raise ValueError("データなし")
            chg = price - prev
            pct = (chg / prev) * 100
            results.append((name, price, chg, pct))
        except Exception as e:
            results.append((name, None, None, None))
    return results


def get_data_alphavantage(api_key: str):
    import requests

    SYMBOLS = {
        "S&P 500":          ("SPY",  "stock"),
        "Dow Jones":        ("DIA",  "stock"),
        "NASDAQ":           ("QQQ",  "stock"),
        "Gold (金)":        ("GLD",  "stock"),
        "USD/JPY":          ("USDJPY", "forex"),
    }

    results = []
    base = "https://www.alphavantage.co/query"

    for name, (sym, kind) in SYMBOLS.items():
        try:
            if kind == "forex":
                r = requests.get(base, params={
                    "function": "CURRENCY_EXCHANGE_RATE",
                    "from_currency": "USD",
                    "to_currency": "JPY",
                    "apikey": api_key,
                }, timeout=10)
                data = r.json()
                price = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
                results.append((name, price, None, None))
            else:
                r = requests.get(base, params={
                    "function": "GLOBAL_QUOTE",
                    "symbol": sym,
                    "apikey": api_key,
                }, timeout=10)
                q = r.json()["Global Quote"]
                price = float(q["05. price"])
                chg   = float(q["09. change"])
                pct   = float(q["10. change percent"].replace("%", ""))
                results.append((name, price, chg, pct))
        except Exception:
            results.append((name, None, None, None))
    return results


def fmt_row(name: str, price, chg, pct) -> str:
    if price is None:
        return f"  {name:<22} データ取得失敗"
    price_str = f"{price:>12,.2f}"
    if chg is not None and pct is not None:
        arrow = "▲" if chg >= 0 else "▼"
        sign  = "+" if chg >= 0 else ""
        change = f"{arrow} {sign}{chg:,.2f} ({sign}{pct:.2f}%)"
    else:
        change = ""
    return f"  {name:<22} {price_str}   {change}"


def main():
    import os

    alpha_key = os.environ.get("ALPHAVANTAGE_API_KEY", "")

    now = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    sep = "=" * 60
    print(f"\n{sep}")
    print(f"  米国市場 朝の市況レポート  {now}")
    print(sep)

    results = []

    if alpha_key:
        results = get_data_alphavantage(alpha_key)
    else:
        try:
            results = get_data_yfinance()
        except ImportError:
            print("  [エラー] yfinanceが未インストールです。")
            print("  pip install yfinance  または  ALPHAVANTAGE_API_KEY を設定してください。")
            sys.exit(1)

    for row in results:
        print(fmt_row(*row))

    print(sep)
    print()


if __name__ == "__main__":
    main()
