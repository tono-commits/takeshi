#!/usr/bin/env python3
"""毎朝8時に米国市場の市況を取得して表示するスクリプト。
使用方法: ANTHROPIC_API_KEY=your_key python3 market_briefing.py
"""

import anthropic
from datetime import datetime

SYSTEM_PROMPT = """あなたは金融市場アナリストです。
米国株式市場の最新データをウェブ検索で取得し、以下の形式で簡潔に報告してください。
数値は必ず前日比(%)も含めてください。"""

USER_PROMPT = """本日の米国市場の最新市況を調べて、以下の項目を日本語で報告してください：

【主要指数】
- S&P 500（終値と前日比%）
- NASDAQ総合（終値と前日比%）
- ダウ平均（終値と前日比%）

【市場指標】
- VIX（恐怖指数）
- 米10年国債利回り
- USD/JPY（ドル円）

【主要セクター動向】（上昇・下落の傾向を簡潔に）

【本日のポイント】（市場を動かした主なニュース・要因を2〜3点）

現在の日時：""" + datetime.now().strftime("%Y年%m月%d日 %H:%M JST")


def main():
    client = anthropic.Anthropic()

    print("=" * 60)
    print(f"  米国市場 朝の市況レポート")
    print(f"  {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    print("=" * 60)
    print()

    with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=[
            {"type": "web_search_20260209", "name": "web_search"},
        ],
        messages=[{"role": "user", "content": USER_PROMPT}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print("\n")
    print("=" * 60)


if __name__ == "__main__":
    main()
