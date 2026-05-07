#!/usr/bin/env python3
"""US market morning report - runs daily at 8:00 AM JST (23:00 UTC)."""

import yfinance as yf
from datetime import datetime
import pytz

JST = pytz.timezone("Asia/Tokyo")

INDICES = {
    "S&P 500":    "^GSPC",
    "NASDAQ":     "^IXIC",
    "Dow Jones":  "^DJI",
    "VIX (恐怖指数)": "^VIX",
}

FUTURES = {
    "S&P先物":    "ES=F",
    "NASDAQ先物": "NQ=F",
}

CURRENCIES = {
    "USD/JPY": "JPYUSD=X",
}


def fmt_change(change, pct):
    arrow = "▲" if change >= 0 else "▼"
    sign = "+" if change >= 0 else ""
    return f"{arrow} {sign}{change:,.2f} ({sign}{pct:.2f}%)"


def get_quote(ticker_symbol):
    t = yf.Ticker(ticker_symbol)
    info = t.fast_info
    price = info.last_price
    prev_close = info.previous_close
    if price is None or prev_close is None:
        return None, None, None
    change = price - prev_close
    pct = (change / prev_close) * 100
    return price, change, pct


def main():
    now_jst = datetime.now(JST)
    print("=" * 52)
    print(f"  米国市場 朝の市況レポート")
    print(f"  {now_jst.strftime('%Y年%m月%d日 %H:%M')} (JST)")
    print("=" * 52)

    print("\n【主要指数 (前日終値)】")
    for name, symbol in INDICES.items():
        price, change, pct = get_quote(symbol)
        if price is not None:
            print(f"  {name:<16} {price:>12,.2f}  {fmt_change(change, pct)}")
        else:
            print(f"  {name:<16}  データ取得失敗")

    print("\n【先物 (現在値)】")
    for name, symbol in FUTURES.items():
        price, change, pct = get_quote(symbol)
        if price is not None:
            print(f"  {name:<16} {price:>12,.2f}  {fmt_change(change, pct)}")
        else:
            print(f"  {name:<16}  データ取得失敗")

    print("\n【為替】")
    t = yf.Ticker("USDJPY=X")
    info = t.fast_info
    rate = info.last_price
    prev = info.previous_close
    if rate and prev:
        change = rate - prev
        pct = (change / prev) * 100
        print(f"  {'USD/JPY':<16} {rate:>12.2f}円  {fmt_change(change, pct)}")
    else:
        print("  USD/JPY          データ取得失敗")

    print("\n" + "=" * 52)


if __name__ == "__main__":
    main()
