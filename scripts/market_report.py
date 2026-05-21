#!/usr/bin/env python3
"""
US Market Daily Report Generator
Fetches previous trading day's closing data and outputs a formatted report.
"""

import json
import sys
from datetime import datetime, timezone, timedelta

try:
    import yfinance as yf
except ImportError:
    print("yfinance not installed", file=sys.stderr)
    sys.exit(1)

JST = timezone(timedelta(hours=9))

INDICES = {
    "S&P 500":      "^GSPC",
    "ダウ平均":      "^DJI",
    "NASDAQ":       "^IXIC",
    "Russell 2000": "^RUT",
    "VIX":          "^VIX",
}

SECTORS = {
    "テクノロジー (XLK)":    "XLK",
    "金融 (XLF)":           "XLF",
    "エネルギー (XLE)":      "XLE",
    "ヘルスケア (XLV)":      "XLV",
    "一般消費財 (XLY)":      "XLY",
    "生活必需品 (XLP)":      "XLP",
    "素材 (XLB)":           "XLB",
    "不動産 (XLRE)":         "XLRE",
    "公益事業 (XLU)":        "XLU",
    "資本財 (XLI)":          "XLI",
    "通信 (XLC)":            "XLC",
}

FX = {
    "USD/JPY": "USDJPY=X",
    "EUR/USD": "EURUSD=X",
}

BONDS = {
    "米国2年債利回り":  "^IRX",
    "米国10年債利回り": "^TNX",
    "米国30年債利回り": "^TYX",
}

COMMODITIES = {
    "WTI原油":  "CL=F",
    "金":       "GC=F",
}


def fmt_change(current, prev, is_pct=False):
    if prev is None or prev == 0:
        return "N/A", "N/A"
    change = current - prev
    pct = change / prev * 100
    arrow = "▲" if change >= 0 else "▼"
    sign = "+" if change >= 0 else ""
    if is_pct:
        return f"{sign}{change:.2f}pt", f"{arrow} {sign}{pct:.2f}%"
    return f"{sign}{change:,.2f} ({sign}{pct:.2f}%)", arrow


def fetch_quote(ticker_symbol):
    tk = yf.Ticker(ticker_symbol)
    hist = tk.history(period="5d")
    if hist.empty or len(hist) < 2:
        return None
    latest = hist.iloc[-1]
    prev = hist.iloc[-2]
    return {
        "close": latest["Close"],
        "prev_close": prev["Close"],
        "date": hist.index[-1].strftime("%Y-%m-%d"),
    }


def build_section(title, symbols):
    lines = [f"### {title}", ""]
    for label, sym in symbols.items():
        q = fetch_quote(sym)
        if q is None:
            lines.append(f"- **{label}**: データ取得失敗")
            continue
        close = q["close"]
        prev  = q["prev_close"]
        change = close - prev
        pct = change / prev * 100 if prev else 0
        sign = "+" if change >= 0 else ""
        arrow = "▲" if change >= 0 else "▼"
        lines.append(
            f"- **{label}**: {close:,.2f}　{arrow} {sign}{change:,.2f} ({sign}{pct:.2f}%)"
        )
    lines.append("")
    return lines


def main():
    now_jst = datetime.now(JST)
    report_date = now_jst.strftime("%Y年%m月%d日 %H:%M JST")

    lines = [
        f"# 🇺🇸 米国市場 朝の市況レポート",
        f"",
        f"> **{report_date}** 時点（前日終値ベース）",
        f"",
    ]

    lines += build_section("📈 主要指数", INDICES)
    lines += build_section("🏦 セクター別 ETF", SECTORS)
    lines += build_section("💱 為替", FX)
    lines += build_section("📉 米国債利回り", BONDS)
    lines += build_section("🛢️ コモディティ", COMMODITIES)

    lines += [
        "---",
        "_データソース: Yahoo Finance_",
    ]

    print("\n".join(lines))


if __name__ == "__main__":
    main()
