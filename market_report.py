#!/usr/bin/env python3
"""US market morning report — prints key indices, sectors, and assets."""

import sys
import yfinance as yf
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

INDICES = {
    "S&P 500":        "^GSPC",
    "Dow Jones":      "^DJI",
    "Nasdaq":         "^IXIC",
    "Russell 2000":   "^RUT",
    "VIX (恐怖指数)":  "^VIX",
}

SECTORS = {
    "テクノロジー":  "XLK",
    "金融":          "XLF",
    "ヘルスケア":    "XLV",
    "エネルギー":    "XLE",
    "一般消費財":    "XLY",
    "生活必需品":    "XLP",
    "資本財":        "XLI",
    "通信":          "XLC",
    "素材":          "XLB",
    "不動産":        "XLRE",
    "公益事業":      "XLU",
}

ASSETS = {
    "金 (Gold)":      "GC=F",
    "原油 (WTI)":     "CL=F",
    "米10年債利回り":  "^TNX",
    "ドル円":          "JPY=X",
}


def pct_arrow(chg: float) -> str:
    sign = "▲" if chg >= 0 else "▼"
    return f"{sign}{abs(chg):.2f}%"


def fetch_quote(ticker: str) -> tuple[float, float, float] | None:
    """Returns (price, prev_close, pct_change) or None on failure."""
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        price = info.last_price
        prev  = info.previous_close
        if price is None or prev is None or prev == 0:
            return None
        return price, prev, (price - prev) / prev * 100
    except Exception:
        return None


def build_section(title: str, items: dict[str, str], fmt: str = ",.2f") -> list[str]:
    lines = [f"\n## {title}\n", "| 銘柄 | 価格 | 前日比 |", "|------|------|--------|"]
    for name, sym in items.items():
        result = fetch_quote(sym)
        if result is None:
            lines.append(f"| {name} | — | — |")
        else:
            price, _, pct = result
            lines.append(f"| {name} | {price:{fmt}} | {pct_arrow(pct)} |")
    return lines


def main() -> None:
    now_jst = datetime.now(JST)
    now_utc = datetime.now(timezone.utc)

    out: list[str] = [
        f"# 米国市場 朝の市況レポート 🇺🇸",
        f"",
        f"**レポート日時**: {now_jst.strftime('%Y年%m月%d日 %H:%M')} JST  ",
        f"**前日米国市場終値ベース**",
    ]

    out += build_section("主要指数", INDICES)
    out += build_section("セクター ETF", SECTORS)
    out += build_section("その他資産", ASSETS)

    out += [
        "",
        "---",
        f"*データソース: Yahoo Finance / 生成: {now_utc.strftime('%Y-%m-%d %H:%M UTC')}*",
    ]

    report = "\n".join(out)
    print(report)

    # Write to file if path given as argument (used by GitHub Actions)
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8") as f:
            f.write(report)


if __name__ == "__main__":
    main()
