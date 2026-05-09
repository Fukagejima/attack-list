"""
企業情報パーサー
公開HTMLから法人情報の断片を抽出するユーティリティ群
"""
import re
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from utils.logger import get_logger

logger = get_logger(__name__)

REVENUE_PATTERNS = [
    r"売上(?:高|収益)[^\d]*?([\d,]+)\s*(?:百万円|億円|千万円)",
    r"(?:revenue|sales)[^\d]*?([\d,]+)\s*(?:million|billion)",
    r"(\d[\d,]+)\s*百万円",
    r"(\d[\d,]+)\s*億円",
]

EMPLOYEE_PATTERNS = [
    r"従業員数[^\d]*?([\d,]+)\s*名",
    r"社員数[^\d]*?([\d,]+)\s*名",
    r"employees[:\s]+([\d,]+)",
]


@dataclass
class CompanyProfile:
    name: str = ""
    industry: str = ""
    revenue_raw: str = ""          # 原文（「推定」フラグ付き）
    revenue_estimated: bool = True
    employee_count: str = ""
    description: str = ""
    url: str = ""
    source_urls: list[str] = field(default_factory=list)
    press_snippets: list[str] = field(default_factory=list)
    job_keywords: list[str] = field(default_factory=list)


def extract_revenue(text: str) -> tuple[str, bool]:
    """テキストから売上情報を抽出。(値文字列, 推定フラグ) を返す"""
    for pattern in REVENUE_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(0).strip(), False
    return "情報なし（推定）", True


def extract_employee_count(text: str) -> str:
    for pattern in EMPLOYEE_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return "不明"


def parse_company_page(html: str, url: str = "") -> CompanyProfile:
    """企業サイトのHTMLからCompanyProfileを生成"""
    profile = CompanyProfile(url=url)
    soup = BeautifulSoup(html, "lxml")

    # タイトル → 企業名候補
    title = soup.find("title")
    if title:
        profile.name = title.get_text().split("|")[0].split("｜")[0].strip()

    # ページ全体のテキスト
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    full_text = " ".join(soup.get_text(separator=" ").split())

    profile.description = full_text[:500]
    rev, est = extract_revenue(full_text)
    profile.revenue_raw = rev
    profile.revenue_estimated = est
    profile.employee_count = extract_employee_count(full_text)
    profile.source_urls.append(url)

    logger.debug(f"パース完了: {profile.name} | 売上: {profile.revenue_raw}")
    return profile
