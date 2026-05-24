#!/usr/bin/env python3
"""Fetch US market data via yfinance and output a Markdown summary."""

import sys
from datetime import datetime, timezone, timedelta

import yfinance as yf

JST = timezone(timedelta(hours=9))

SYMBOLS = [
    ("S&P 500",          "^GSPC",    0),
    ("NASDAQ 100",        "^NDX",     0),
    ("Dow Jones",         "^DJI",     0),
    ("Russell 2000",      "^RUT",     2),
    ("VIX",               "^VIX",     2),
    ("USD/JPY",           "USDJPY=X", 2),
    ("米国10年債利回り",   "^TNX",     3),
    ("WTI原油",           "CL=F",     2),
    ("金",                "GC=F",     1),
    ("Nikkei 225",        "^N225",    0),
]


def fetch_quote(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="5d", auto_adjust=False)
    if hist.empty:
        raise ValueError("No data returned")
    latest = hist.iloc[-1]
    prev = hist.iloc[-2] if len(hist) >= 2 else latest
    price = float(latest["Close"])
    prev_close = float(prev["Close"])
    change = price - prev_close
    pct = (change / prev_close * 100) if prev_close else 0.0
    return {"price": price, "change": change, "pct": pct}


def fmt(value: float, decimals: int) -> str:
    return f"{value:,.{decimals}f}"


def build_markdown() -> str:
    now = datetime.now(JST)
    lines = [
        f"# 📊 米国市場サマリー — {now.strftime('%Y年%m月%d日')}",
        "",
        f"> 取得日時: {now.strftime('%Y-%m-%d %H:%M JST')}",
        "",
        "| 指数 / 銘柄 | 終値 | 前日比 | 変化率 |",
        "|:---|---:|---:|---:|",
    ]

    errors = []
    for name, symbol, decimals in SYMBOLS:
        try:
            q = fetch_quote(symbol)
            price = q["price"]
            change = q["change"]
            pct = q["pct"]

            direction = "🟢 ▲" if change >= 0 else "🔴 ▼"
            sign = "+" if change >= 0 else ""
            lines.append(
                f"| {name} | {fmt(price, decimals)} | "
                f"{direction} {sign}{fmt(change, decimals)} | "
                f"{sign}{pct:.2f}% |"
            )
        except Exception as e:
            lines.append(f"| {name} | — | — | — |")
            errors.append(f"- {name} ({symbol}): {e}")

    lines += [
        "",
        "---",
        "_データソース: Yahoo Finance (yfinance)  |  "
        "自動投稿 by [daily-market-update](.github/workflows/daily-market-update.yml)_",
    ]

    if errors:
        lines += [
            "",
            "<details><summary>取得エラー詳細</summary>",
            "",
            *errors,
            "</details>",
        ]

    return "\n".join(lines)


if __name__ == "__main__":
    try:
        print(build_markdown())
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
