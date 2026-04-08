#!/usr/bin/env python3
"""
米国市場 朝8時 市況レポート
US Market Morning Briefing — fetches from Yahoo Finance (crumb auth)
"""

import requests
import json
import sys
from datetime import datetime
import pytz

JST = pytz.timezone("Asia/Tokyo")

SYMBOLS = {
    "S&P 500":         "^GSPC",
    "Dow Jones":       "^DJI",
    "NASDAQ":          "^IXIC",
    "Russell 2000":    "^RUT",
    "VIX (恐怖指数)":   "^VIX",
    "USD/JPY":         "USDJPY=X",
    "10年米国債利回り": "^TNX",
    "原油 (WTI)":       "CL=F",
    "金 (Gold)":        "GC=F",
}

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
})


def get_crumb() -> str | None:
    """Yahoo Finance crumb を取得（新しい認証方式）"""
    try:
        # クッキーを設定するためにトップページを訪問
        SESSION.get("https://finance.yahoo.com", timeout=10)
        r = SESSION.get(
            "https://query1.finance.yahoo.com/v1/test/getcrumb",
            timeout=10,
        )
        if r.status_code == 200:
            return r.text.strip()
    except Exception:
        pass
    return None


def fetch_quotes(symbols: list[str], crumb: str) -> dict:
    """複数シンボルを一括取得"""
    syms = ",".join(symbols)
    url = (
        "https://query1.finance.yahoo.com/v7/finance/quote"
        f"?symbols={syms}&crumb={crumb}"
    )
    try:
        r = SESSION.get(url, timeout=15)
        r.raise_for_status()
        results = r.json()["quoteResponse"]["result"]
        return {q["symbol"]: q for q in results}
    except Exception:
        return {}


def arrow(change: float) -> str:
    if change > 0:
        return "▲"
    elif change < 0:
        return "▼"
    return " "


def fmt_price(symbol: str, price: float | None) -> str:
    if price is None:
        return "N/A"
    if "TNX" in symbol or "JPY" in symbol:
        return f"{price:.3f}"
    if price >= 10000:
        return f"{price:,.1f}"
    if price >= 100:
        return f"{price:,.2f}"
    return f"{price:.2f}"


def fmt_change(chg: float | None, pct: float | None) -> tuple[str, str, str]:
    if chg is None or pct is None:
        return "N/A", "N/A", " "
    sign = "+" if chg >= 0 else ""
    a = arrow(chg)
    if abs(chg) >= 100:
        return f"{sign}{chg:,.1f}", f"{sign}{pct:.2f}%", a
    return f"{sign}{chg:.2f}", f"{sign}{pct:.2f}%", a


def print_briefing(crumb: str):
    now = datetime.now(JST)
    symbols = list(SYMBOLS.values())
    quotes = fetch_quotes(symbols, crumb)

    rows = []
    for name, sym in SYMBOLS.items():
        q = quotes.get(sym)
        if not q:
            rows.append((name, "取得失敗", "", "", ""))
            continue

        price = q.get("regularMarketPrice")
        chg   = q.get("regularMarketChange")
        pct   = q.get("regularMarketChangePercent")

        price_str             = fmt_price(sym, price)
        chg_str, pct_str, a   = fmt_change(chg, pct)
        rows.append((name, price_str, chg_str, pct_str, a))

    # カラム幅を動的に計算
    name_w  = max(len(r[0]) for r in rows) + 2
    price_w = max(len(r[1]) for r in rows) + 2
    chg_w   = max(len(r[2]) for r in rows) + 2
    pct_w   = max(len(r[3]) for r in rows) + 2
    width   = name_w + price_w + chg_w + pct_w + 10

    border = "=" * width
    print(border)
    title = f"  米国市場 市況レポート  {now.strftime('%Y年%m月%d日 %H:%M')} JST"
    print(title)
    print(border)

    for name, price_str, chg_str, pct_str, a in rows:
        print(
            f"  {name:<{name_w}}"
            f"{price_str:>{price_w}}  "
            f"{a} {chg_str:>{chg_w}}  {pct_str:>{pct_w}}"
        )

    print(border)
    print()

    # サマリーコメント
    sp = quotes.get("^GSPC")
    vix = quotes.get("^VIX")
    if sp and vix:
        sp_pct  = sp.get("regularMarketChangePercent", 0)
        vix_val = vix.get("regularMarketPrice", 0)

        if sp_pct >= 1.0:
            trend = "強い上昇"
        elif sp_pct >= 0.3:
            trend = "小幅上昇"
        elif sp_pct <= -1.0:
            trend = "強い下落"
        elif sp_pct <= -0.3:
            trend = "小幅下落"
        else:
            trend = "ほぼ横ばい"

        if vix_val >= 30:
            sentiment = "高ボラティリティ — リスク回避モード"
        elif vix_val >= 20:
            sentiment = "やや不安定"
        else:
            sentiment = "比較的落ち着いた状態"

        print(f"  S&P500 前日比: {sp_pct:+.2f}% ({trend})")
        print(f"  VIX {vix_val:.1f}: {sentiment}")
        print()


def main():
    crumb = get_crumb()
    if not crumb:
        print("エラー: Yahoo Finance への接続に失敗しました。", file=sys.stderr)
        print("ネットワーク接続を確認してください。", file=sys.stderr)
        sys.exit(1)
    print_briefing(crumb)


if __name__ == "__main__":
    main()
