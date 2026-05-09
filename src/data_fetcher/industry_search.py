"""
業界市場データのウェブ取得モジュール
公開情報から業界の市場規模・成長率データを取得する
"""
from __future__ import annotations
import re
from urllib.parse import quote
from src.data_fetcher.web_fetcher import fetch_html, extract_text
from utils.logger import get_logger

logger = get_logger(__name__)

# 取得対象の公開情報ソース（robots.txt許可・公開統計情報）
MARKET_DATA_SOURCES = [
    # 経済産業省 各種統計（公開データ）
    "https://www.meti.go.jp/statistics/toppage/report/minikaisetsu/hitokoto_kako/",
    # 業界動向サーチ（無料公開部分）
    "https://gyokai-search.com/",
    # 中小企業庁 小規模企業白書
    "https://www.chusho.meti.go.jp/pamflet/hakusyo/",
]

# DuckDuckGo HTML検索（APIキー不要）
DDGO_URL = "https://html.duckduckgo.com/html/?q={query}"


def _search_web(query: str) -> str:
    """DuckDuckGo HTML検索でスニペットを取得"""
    url = DDGO_URL.format(query=quote(query))
    html = fetch_html(url, check_robots=False)
    if not html:
        return ""
    # 検索スニペットの抽出
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    snippets = []
    for el in soup.select(".result__snippet")[:5]:
        text = el.get_text(" ", strip=True)
        if text:
            snippets.append(text)
    result = " / ".join(snippets)
    logger.debug(f"検索結果 ({query}): {result[:200]}")
    return result


def fetch_industry_web_context(
    industries: list[str],
    service_name: str,
) -> dict[str, str]:
    """
    業界リストに対してウェブ検索を行い、
    {業界名: 検索スニペット文字列} を返す。

    ※ フォールバック: 取得失敗時は空文字を返す（Claude の知識で補完）
    """
    contexts: dict[str, str] = {}

    for industry in industries:
        try:
            query = f"{industry} 市場規模 成長率 {2024} 日本"
            snippet = _search_web(query)
            contexts[industry] = snippet
            logger.info(f"ウェブコンテキスト取得: {industry} ({len(snippet)}文字)")
        except Exception as e:
            logger.warning(f"検索失敗 ({industry}): {e}")
            contexts[industry] = ""

    return contexts


def fetch_broad_market_context(service_name: str, strengths: str) -> str:
    """
    サービスに関連する広域マーケットトレンドを取得
    3C分析全体のコンテキストとして使用
    """
    queries = [
        f"{service_name} 市場 トレンド 2024 2025",
        f"{service_name} 競合 業界 日本",
    ]
    results = []
    for q in queries:
        try:
            text = _search_web(q)
            if text:
                results.append(text)
        except Exception as e:
            logger.warning(f"広域検索失敗: {e}")

    return " | ".join(results)
