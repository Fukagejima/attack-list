"""レート制限・robots.txt チェック付きウェブフェッチャー"""
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from config.settings import USER_AGENT, REQUEST_TIMEOUT, MAX_RETRIES, REQUEST_DELAY
from utils.logger import get_logger
from utils.rate_limiter import wait_for_domain
from src.data_fetcher.robots_checker import can_fetch

logger = get_logger(__name__)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch_html(url: str, check_robots: bool = True) -> str | None:
    """
    URLからHTMLを取得する。
    - robots.txt 確認済み
    - リトライ付き
    - ドメイン別レート制限付き
    返り値: HTML文字列 or None
    """
    if check_robots and not can_fetch(url):
        logger.warning(f"robots.txt によりスキップ: {url}")
        return None

    domain = urlparse(url).netloc
    wait_for_domain(domain)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"取得開始 [{attempt}/{MAX_RETRIES}]: {url}")
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding
            logger.info(f"取得成功 (HTTP {resp.status_code}): {url}")
            return resp.text
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP エラー ({e.response.status_code}): {url}")
            if e.response.status_code in (403, 404, 410):
                return None  # リトライ不要
        except requests.exceptions.RequestException as e:
            logger.warning(f"リクエスト失敗 ({attempt}回目): {url} → {e}")
            if attempt < MAX_RETRIES:
                time.sleep(REQUEST_DELAY * attempt)

    logger.error(f"最大リトライ到達、取得断念: {url}")
    return None


def parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def extract_text(url: str, check_robots: bool = True) -> str:
    """URLからメインテキストを抽出して返す"""
    html = fetch_html(url, check_robots)
    if not html:
        return ""
    soup = parse_html(html)
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())
