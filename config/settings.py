import os
from dotenv import load_dotenv

# .env ファイルを明示的なパスで読み込む（実行ディレクトリに依存しない）
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(_BASE_DIR, ".env"), override=True)

# ── 認証設定 ──────────────────────────────────────────────────────────────────
APP_USERNAME = os.getenv("APP_USERNAME", "admin")
APP_PASSWORD = os.getenv("APP_PASSWORD", "password123")

# ── Anthropic API ─────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL       = "claude-sonnet-4-6"   # アタックリスト生成（高精度）
CLAUDE_HAIKU_MODEL = "claude-haiku-4-5"    # 3C分析（高速・低コスト）

# ── スクレイピング設定 ─────────────────────────────────────────────────────────
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY_SECONDS", "2.0"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# ── データソース (公開情報のみ) ─────────────────────────────────────────────────
# 各サイトのURL設定。robots.txtを確認し利用規約に従ってください。
TARGET_SITES = {
    "press_release": [
        "https://prtimes.jp/",            # PR TIMES
        "https://www.businesswire.com/",  # Business Wire
    ],
    "corporate_db": [
        "https://www.ullet.com/",         # ユーレット（企業情報）
        "https://catr.jp/",               # 会社四季報オンライン（無料部分）
    ],
    "job_posting": [
        "https://www.indeed.com/",        # Indeed
        "https://doda.jp/",               # doda
    ],
    "industry_portal": [
        "https://gyokai-search.com/",     # 業界サーチ
    ],
}

# ── スコアリング重み ────────────────────────────────────────────────────────────
SCORING_WEIGHTS = {
    "icp_fit": 0.40,           # ICP適合度（業種・規模・ビジネスモデル）
    "solution_fit": 0.35,      # ソリューションフィット感
    "competitor_saturation": 0.25,  # 競合飽和度（低いほど高スコア）
}

# 3C分析の評価軸（ヒートマップ用）
THREE_C_DIMENSIONS = {
    "Customer": [
        "market_size",          # 市場規模
        "growth_actual",        # 実績伸び率
        "growth_future",        # 将来伸び率
        "market_overview",      # 市場概要スコア
    ],
    "Competitor": [
        "competitor_count",     # 競合数（多いと低スコア）
        "competitor_strength",  # 競合強度（強いと低スコア）
        "market_share_gap",     # 市場シェア余地
    ],
    "Company": [
        "solution_match",       # 自社ソリューション適合
        "past_cases",           # 実績親和性
        "resource_fit",         # リソース適合
    ],
}

# ── 出力設定 ───────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
