import time
import threading
from config.settings import REQUEST_DELAY

class RateLimiter:
    """スレッドセーフなレートリミッター（サイトへの過負荷防止）"""

    def __init__(self, delay: float = REQUEST_DELAY):
        self._delay = delay
        self._last_call: dict[str, float] = {}
        self._lock = threading.Lock()

    def wait(self, domain: str = "default") -> None:
        with self._lock:
            last = self._last_call.get(domain, 0)
            elapsed = time.time() - last
            if elapsed < self._delay:
                time.sleep(self._delay - elapsed)
            self._last_call[domain] = time.time()

_global_limiter = RateLimiter()

def wait_for_domain(domain: str) -> None:
    _global_limiter.wait(domain)
