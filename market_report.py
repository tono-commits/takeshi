#!/usr/bin/env python3
"""
US Market Morning Report
毎朝8時に米国市場の市況を取得・レポートするスクリプト
"""

import sys
import json
from datetime import datetime, timezone, timedelta

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance is not installed. Run: pip install yfinance", file=sys.stderr)
    sys.exit(1)

# JST timezone
JST = timezone(timedelta(hours=9))

INDICES = [
    ("^GSPC",  "S&P 500"),
    ("^IXIC",  "NASDAQ Composite"),
    ("^DJI",   "Dow Jones"),
    ("^RUT",   "Russell 2000"),
    ("^VIX",   "VIX (恐怖指数)"),
    ("^TNX",   "US 10年国債利回り"),
    ("DX-Y.NYB", "US Dollar Index"),
]

SECTORS = [
    ("XLK",  "テクノロジー"),
    ("XLF",  "金融"),
    ("XLE",  "エネルギー"),
    ("XLV",  "ヘルスケア"),
    ("XLY",  "一般消費財"),
    ("XLI",  "資本財"),
    ("XLB",  "素材"),
    ("XLRE", "不動産"),
    ("XLU",  "公益事業"),
    ("XLC",  "通信"),
    ("XLP",  "生活必需品"),
]


def fmt_change(change: float, pct: float) -> str:
    sign = "+" if change >= 0 else ""
    arrow = "▲" if change >= 0 else "▼"
    return f"{arrow} {sign}{change:,.2f} ({sign}{pct:.2f}%)"


def get_ticker_info(symbol: str) -> dict | None:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        if hist.empty or len(hist) < 1:
            return None

        close = hist["Close"].iloc[-1]
        if len(hist) >= 2:
            prev_close = hist["Close"].iloc[-2]
            change = close - prev_close
            pct = (change / prev_close) * 100
        else:
            change = 0.0
            pct = 0.0

        return {"close": close, "change": change, "pct": pct}
    except Exception as e:
        print(f"  Warning: {symbol} の取得失敗: {e}", file=sys.stderr)
        return None


def build_report() -> str:
    now_jst = datetime.now(JST)
    report_date = now_jst.strftime("%Y年%m月%d日 (%a) %H:%M JST")

    lines = []
    lines.append(f"# 米国市場 朝の市況レポート")
    lines.append(f"")
    lines.append(f"**{report_date}**")
    lines.append(f"")

    # ---------- 主要指数 ----------
    lines.append("## 主要指数")
    lines.append("")
    lines.append("| 指数 | 終値 | 前日比 |")
    lines.append("|------|-----:|--------|")

    for symbol, name in INDICES:
        info = get_ticker_info(symbol)
        if info is None:
            lines.append(f"| {name} | N/A | — |")
            continue

        close = info["close"]
        change_str = fmt_change(info["change"], info["pct"])

        if symbol == "^TNX":
            lines.append(f"| {name} | {close:.3f}% | {change_str} |")
        elif symbol in ("^VIX",):
            lines.append(f"| {name} | {close:.2f} | {change_str} |")
        else:
            lines.append(f"| {name} | {close:,.2f} | {change_str} |")

    lines.append("")

    # ---------- セクター別ETF ----------
    lines.append("## セクター別パフォーマンス (ETF)")
    lines.append("")
    lines.append("| セクター | 終値 | 前日比 |")
    lines.append("|----------|-----:|--------|")

    for symbol, name in SECTORS:
        info = get_ticker_info(symbol)
        if info is None:
            lines.append(f"| {name} ({symbol}) | N/A | — |")
            continue
        change_str = fmt_change(info["change"], info["pct"])
        lines.append(f"| {name} ({symbol}) | {info['close']:.2f} | {change_str} |")

    lines.append("")

    # ---------- 注記 ----------
    lines.append("---")
    lines.append("")
    lines.append("> データソース: Yahoo Finance  ")
    lines.append("> ※終値は直近の取引日のものです。")
    lines.append("")

    return "\n".join(lines)


def main():
    print("米国市場データを取得中...", file=sys.stderr)
    report = build_report()

    # ファイルに保存
    now_jst = datetime.now(JST)
    filename = f"market_reports/{now_jst.strftime('%Y-%m-%d')}.md"

    import os
    os.makedirs("market_reports", exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    # 最新レポートも更新
    with open("LATEST_MARKET_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\n=> 保存完了: {filename}", file=sys.stderr)


if __name__ == "__main__":
    main()
