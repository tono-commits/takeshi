#!/usr/bin/env python3
"""
US Market Daily Update Script
毎朝8:00（JST）に米国市場の市況を取得・表示するスクリプト
"""

import requests
import json
from datetime import datetime, timezone, timedelta
import sys

JST = timezone(timedelta(hours=9))

SYMBOLS = {
    "S&P 500":     "^GSPC",
    "Dow Jones":   "^DJI",
    "NASDAQ":      "^IXIC",
    "Russell 2000":"^RUT",
    "VIX (恐怖指数)": "^VIX",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; market-update-bot/1.0)"
}


def fetch_quote(symbol: str) -> dict | None:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        meta = data["chart"]["result"][0]["meta"]
        return {
            "price":          meta.get("regularMarketPrice"),
            "prev_close":     meta.get("chartPreviousClose"),
            "market_state":   meta.get("marketState", "CLOSED"),
            "currency":       meta.get("currency", "USD"),
        }
    except Exception as e:
        print(f"  [取得エラー: {e}]", file=sys.stderr)
        return None


def arrow(change: float) -> str:
    return "▲" if change >= 0 else "▼"


def format_line(name: str, info: dict) -> str:
    price     = info["price"]
    prev      = info["prev_close"]
    change    = price - prev
    pct       = (change / prev) * 100 if prev else 0
    sign      = "+" if change >= 0 else ""
    return (
        f"  {name:<16} {price:>10,.2f}  "
        f"{arrow(change)} {sign}{change:>8,.2f} ({sign}{pct:.2f}%)"
    )


def main():
    now_jst = datetime.now(JST)
    now_et  = datetime.now(timezone(timedelta(hours=-4)))  # EDT (夏時間)

    print("=" * 60)
    print("  🇺🇸 米国市場 デイリー市況レポート")
    print(f"  {now_jst.strftime('%Y年%m月%d日 %H:%M JST')}  "
          f"({now_et.strftime('%m/%d %H:%M ET')})")
    print("=" * 60)

    results = {}
    for name, sym in SYMBOLS.items():
        info = fetch_quote(sym)
        if info:
            results[name] = info

    if not results:
        print("  データを取得できませんでした。ネットワークを確認してください。")
        sys.exit(1)

    # 市場ステータス
    sample = next(iter(results.values()))
    state_map = {
        "PRE":        "プレマーケット中",
        "REGULAR":    "通常取引中",
        "POST":       "アフターアワーズ中",
        "CLOSED":     "取引終了（前日終値）",
        "PREPRE":     "取引前",
        "POSTPOST":   "取引後",
    }
    state_label = state_map.get(sample["market_state"], sample["market_state"])
    print(f"\n  市場ステータス: {state_label}")
    print()

    print("  指数名             現在値        変動           変動率")
    print("  " + "-" * 56)
    for name, info in results.items():
        try:
            print(format_line(name, info))
        except Exception:
            print(f"  {name:<16}  データなし")

    print()

    # 簡易サマリー
    sp = results.get("S&P 500")
    if sp:
        pct = ((sp["price"] - sp["prev_close"]) / sp["prev_close"]) * 100
        if pct >= 1.0:
            mood = "強気 (Bull) — 主要指数は堅調に上昇"
        elif pct >= 0.0:
            mood = "やや強気 — 小幅上昇"
        elif pct >= -1.0:
            mood = "やや弱気 — 小幅下落"
        else:
            mood = "弱気 (Bear) — 主要指数は大幅下落"
        print(f"  【サマリー】S&P500 前日比 {pct:+.2f}%  → {mood}")

    vix = results.get("VIX (恐怖指数)")
    if vix:
        v = vix["price"]
        vix_label = "低ボラティリティ" if v < 15 else ("通常" if v < 25 else ("警戒" if v < 35 else "極度の恐怖"))
        print(f"  【VIX】{v:.2f} → {vix_label}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
