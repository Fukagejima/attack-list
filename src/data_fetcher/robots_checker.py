"""robots.txt に従ったクローリング可否チェック"""
import urllib.robotparser
from urllib.parse import urlparse
from utils.logger import get_logger
from config.settings import USER_AGENT

logger = get_logger(__name__)
_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


def can_fetch(url: str) -> bool:
    """robots.txt を確認してクロール可能かどうかを返す"""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{base}/robots.txt"

    if base not in _cache:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
            _cache[base] = rp
            logger.debug(f"robots.txt 読み込み完了: {robots_url}")
        except Exception as e:
            logger.warning(f"robots.txt 読み込み失敗 ({robots_url}): {e} → クロール許可として扱います")
            return True

    allowed = _cache[base].can_fetch(USER_AGENT, url)
    if not allowed:
        logger.info(f"robots.txt によりクロール不可: {url}")
    return allowed
