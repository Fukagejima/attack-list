"""
スコアリングエンジン
- 3C業界スコア集計
- 企業単位のICP/フィット/競合スコア計算
"""
from config.settings import SCORING_WEIGHTS, THREE_C_DIMENSIONS


def calc_industry_total_score(scores: dict) -> float:
    """3Cの各スコアから業界トータルスコアを計算（0〜100）"""
    customer_keys = THREE_C_DIMENSIONS["Customer"]
    competitor_keys = THREE_C_DIMENSIONS["Competitor"]
    company_keys = THREE_C_DIMENSIONS["Company"]

    def avg(keys):
        vals = [scores.get(k, 5) for k in keys]
        return sum(vals) / len(vals) if vals else 5

    customer_avg = avg(customer_keys)
    competitor_avg = avg(competitor_keys)
    company_avg = avg(company_keys)

    # 重み: Customer 40% / Competitor 30% / Company 30%
    total = customer_avg * 0.4 + competitor_avg * 0.3 + company_avg * 0.3
    return round(total * 10, 1)  # 10倍して100点満点に


def calc_company_total_score(
    icp: float, solution: float, competitor: float
) -> float:
    """企業スコアの加重平均（0〜100）"""
    w = SCORING_WEIGHTS
    raw = (
        icp * w["icp_fit"]
        + solution * w["solution_fit"]
        + competitor * w["competitor_saturation"]
    )
    return round(raw * 10, 1)


def rank_industries(industry_scores: dict) -> list[dict]:
    """業界スコア辞書をスコア降順でソートしてリスト化"""
    items = []
    for name, data in industry_scores.items():
        scores = data.get("scores", {})
        total = data.get("total_score") or calc_industry_total_score(scores)
        items.append({
            "industry": name,
            "total_score": total,
            "scores": scores,
            "summary": data.get("summary", ""),
            "risks": data.get("risks", ""),
        })
    items.sort(key=lambda x: x["total_score"], reverse=True)
    for i, item in enumerate(items, 1):
        item["rank"] = i
    return items


def rank_companies(companies: list[dict]) -> list[dict]:
    """企業リストをtotal_score降順で並べ替え、優先順位を付与"""
    sorted_list = sorted(companies, key=lambda x: x.get("total_score", 0), reverse=True)
    for i, c in enumerate(sorted_list, 1):
        c["rank"] = i
    return sorted_list
