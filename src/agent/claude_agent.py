"""
Claude API エージェント
- 全業界網羅3C分析（Haiku並列処理で高速化）
- 企業スコアリング・アタックリスト生成（Sonnet）
"""
from __future__ import annotations
import json
import re
import concurrent.futures
import anthropic
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_HAIKU_MODEL
from config.industries import ALL_INDUSTRIES, INDUSTRY_TO_CATEGORY
from utils.logger import get_logger

logger = get_logger(__name__)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a Japanese market analyst specializing in BtoB/BtoC sales strategy.
Analyze industries and generate attack lists based on public information.

CRITICAL OUTPUT RULES:
- Output ONLY valid JSON. No markdown, no code blocks, no explanations outside JSON.
- Use ONLY standard ASCII double quotes (") for all JSON keys and string values.
- NEVER use Japanese quotation marks 「」 or single quotes ' in JSON.
- Japanese text in values is fine, but keys and structural characters must be ASCII JSON.
- Scores are integers 1-100.
- Evaluation must be one of: ◎ ○ △ ×"""

_BATCH_SIZE = 15


def _clean_json(raw: str) -> str:
    raw = re.sub(r"```(?:json)?", "", raw).strip()
    raw = raw.rstrip("`").strip()
    raw = raw.replace("「", '"').replace("」", '"')
    raw = re.sub(r"'([^']*)'(\s*:)", r'"\1"\2', raw)
    raw = re.sub(r":\s*'([^']*)'", r': "\1"', raw)
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    return raw


def _parse_json_safe(raw: str) -> list | dict:
    for attempt in (raw, _clean_json(raw)):
        try:
            return json.loads(attempt)
        except json.JSONDecodeError:
            pass
    for pattern in (r"\[.*\]", r"\{.*\}"):
        m = re.search(pattern, _clean_json(raw), re.DOTALL)
        if m:
            try:
                result = json.loads(m.group(0))
                return result if isinstance(result, list) else [result]
            except json.JSONDecodeError:
                pass
    raise ValueError(f"JSONパース失敗。先頭300文字:\n{raw[:300]}")


def _make_industry_prompt(
    batch: list[str],
    batch_idx: int,
    total_batches: int,
    company_name: str,
    service_name: str,
    strengths: str,
    existing_industry: str,
    target_revenue_scale: str,
    col1_label: str,
    col2_label: str,
    broad_context: str,
    existing_list_context: str,
    ctx_block: str,
) -> str:
    """各バッチ用のプロンプトを生成"""
    if col1_label and col2_label:
        label_instruction = f"""
### Company axis labels (FIXED - use exactly these)
fit_column1_label = "{col1_label}"
fit_column2_label = "{col2_label}" """
    else:
        label_instruction = f"""
### Company axis labels (decide based on service characteristics)
Name 2 axes showing how well each industry fits "{service_name}".
e.g. for AI consulting: "AI導入意欲" and "予算規模適合" """

    eval_instruction = f"""
## Evaluation rule (STRICT)
Across all {len(ALL_INDUSTRIES)} industries total, ◎ should be 3+, ○ should be 5+.
In THIS batch of {len(batch)}: assign ◎ to top 1-2, ○ to next 2-3. Never assign only △/×."""

    return f"""Analyze industries for a Japanese company. Return ONLY a JSON array.

## Company Info
- Company: {company_name}
- Service: {service_name}
- Strengths: {strengths}
- Current clients: {existing_industry}
{f"- Target revenue scale: {target_revenue_scale}" if target_revenue_scale else ""}
{f"- Market context: {broad_context[:300]}" if broad_context else ""}
{existing_list_context[:600] if existing_list_context else ""}
{ctx_block}

## Industries to analyze (ALL of them, batch {batch_idx+1}/{total_batches})
{json.dumps(batch, ensure_ascii=False)}

{label_instruction}
{eval_instruction}

## Output (JSON array only)
[{{"industry":"name","category":"カテゴリ名","market_size":"X兆円","growth_actual":"+X%","growth_future":"+X%","market_overview":"概況1〜2文","fit_column1_label":"ラベル1","fit_column1":"コメント","fit_column2_label":"ラベル2","fit_column2":"コメント","competitor_summary":"競合状況","evaluation":"◎","score":85}}]

Return ONLY the JSON array."""


def _call_batch(
    batch: list[str],
    batch_idx: int,
    total_batches: int,
    company_name: str,
    service_name: str,
    strengths: str,
    existing_industry: str,
    target_revenue_scale: str,
    col1_label: str,
    col2_label: str,
    broad_context: str,
    existing_list_context: str,
    web_contexts: dict,
) -> tuple[int, list[dict]]:
    """1バッチ分の分析を実行して (batch_idx, results) を返す"""
    ctx_block = ""
    if web_contexts:
        for ind in batch:
            ctx = web_contexts.get(ind, "")
            if ctx:
                ctx_block += f"\n[{ind}] {ctx[:150]}"

    prompt = _make_industry_prompt(
        batch, batch_idx, total_batches, company_name, service_name,
        strengths, existing_industry, target_revenue_scale,
        col1_label, col2_label, broad_context, existing_list_context, ctx_block,
    )

    try:
        resp = client.messages.create(
            model=CLAUDE_HAIKU_MODEL,   # ← Haiku で高速処理
            max_tokens=4096,
            system=[{"type": "text", "text": SYSTEM_PROMPT,
                     "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text.strip()
        batch_data = _parse_json_safe(raw)

        # カテゴリ補完
        for item in batch_data:
            if not item.get("category"):
                item["category"] = INDUSTRY_TO_CATEGORY.get(item.get("industry", ""), "その他")

        logger.info(f"バッチ{batch_idx+1} 完了: {len(batch_data)}業界")
        return batch_idx, batch_data

    except Exception as e:
        logger.error(f"バッチ{batch_idx+1} エラー: {e}")
        fallback = [{
            "industry": ind,
            "category": INDUSTRY_TO_CATEGORY.get(ind, "その他"),
            "market_size": "—", "growth_actual": "—", "growth_future": "—",
            "market_overview": "取得エラー（再分析してください）",
            "fit_column1_label": col1_label or "適合度①", "fit_column1": "—",
            "fit_column2_label": col2_label or "適合度②", "fit_column2": "—",
            "competitor_summary": "—", "evaluation": "△", "score": 0,
        } for ind in batch]
        return batch_idx, fallback


def analyze_all_industries(
    company_name: str,
    service_name: str,
    strengths: str,
    existing_industry: str,
    target_revenue_scale: str = "",
    web_contexts: dict[str, str] = None,
    broad_context: str = "",
    existing_list_context: str = "",
) -> list[dict]:
    """
    全業界を網羅的に3C分析。
    Haiku モデル + 並列バッチ処理で高速化（約1/3の時間）。
    """
    batches = [ALL_INDUSTRIES[i:i + _BATCH_SIZE]
               for i in range(0, len(ALL_INDUSTRIES), _BATCH_SIZE)]
    total = len(batches)
    logger.info(f"全業界分析開始: {len(ALL_INDUSTRIES)}業界 / {total}バッチ / モデル: {CLAUDE_HAIKU_MODEL}")

    # ── STEP1: バッチ0を先に実行してColumn軸ラベルを確定 ──────────────────────
    # （ラベルは全バッチで統一するため、1件だけ先行実行）
    _, first_results = _call_batch(
        batches[0], 0, total, company_name, service_name, strengths,
        existing_industry, target_revenue_scale, "", "", broad_context,
        existing_list_context, web_contexts or {},
    )

    col1_label = first_results[0].get("fit_column1_label", "適合度①") if first_results else "適合度①"
    col2_label = first_results[0].get("fit_column2_label", "適合度②") if first_results else "適合度②"
    logger.info(f"Column軸ラベル確定: {col1_label} / {col2_label}")

    # ── STEP2: 残りのバッチを並列実行 ─────────────────────────────────────────
    remaining = batches[1:]
    all_results_map: dict[int, list] = {0: first_results}

    if remaining:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(remaining)) as executor:
            futures = {
                executor.submit(
                    _call_batch,
                    batch, idx + 1, total, company_name, service_name, strengths,
                    existing_industry, target_revenue_scale, col1_label, col2_label,
                    broad_context, existing_list_context, web_contexts or {},
                ): idx + 1
                for idx, batch in enumerate(remaining)
            }
            for future in concurrent.futures.as_completed(futures):
                batch_idx, results = future.result()
                all_results_map[batch_idx] = results

    # ── バッチ順に結合 ─────────────────────────────────────────────────────────
    all_results: list[dict] = []
    for i in range(total):
        batch_data = all_results_map.get(i, [])
        for item in batch_data:
            item["fit_column1_label"] = col1_label
            item["fit_column2_label"] = col2_label
        all_results.extend(batch_data)

    all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
    logger.info(f"全業界分析完了: {len(all_results)}業界")
    return all_results


def generate_attack_list(
    company_name: str,
    service_name: str,
    strengths: str,
    target_industries: list[str],
    companies_per_industry: int = 10,
    target_revenue_scale: str = "",
    existing_list_context: str = "",
) -> list[dict]:
    """対象業界の具体企業リストとスコアを生成（Sonnet で高精度）"""
    industry_list_str = "\n".join(f"- {ind}" for ind in target_industries)

    prompt = f"""Generate a sales attack list of real Japanese companies for the following service.

## Company Info
- Company: {company_name}
- Service: {service_name}
- Strengths: {strengths}
{f"- Target company revenue scale: {target_revenue_scale} (prioritize companies matching this scale)" if target_revenue_scale else ""}

## Target Industries
{industry_list_str}
{existing_list_context[:600] if existing_list_context else ""}

## Instructions
List {companies_per_industry} real Japanese companies per industry.
Use only publicly available corporate information (not personal data).
For estimated values, append （推定）.

## Output format (JSON array only, no other text)
[
  {{
    "rank": 1,
    "company_name": "株式会社XXX",
    "industry": "industry name",
    "revenue_scale": "売上規模 e.g. 約500億円（推定）",
    "revenue_estimated": true,
    "employee_scale": "従業員規模",
    "icp_fit_score": 8,
    "solution_fit_score": 7,
    "competitor_saturation_score": 6,
    "total_score": 72,
    "compatibility_comment": "2 sentences in Japanese",
    "approach_hint": "1 sentence approach hint in Japanese",
    "public_info_source": "source hint",
    "data_confidence": "high"
  }}
]

total_score = (icp_fit*0.4 + solution_fit*0.35 + competitor_saturation*0.25) * 10
data_confidence: high=IR confirmed / medium=estimated / low=uncertain"""

    logger.info(f"アタックリスト生成: {target_industries} / モデル: {CLAUDE_MODEL}")
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8192,
        system=[{"type": "text", "text": SYSTEM_PROMPT,
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    data = _parse_json_safe(raw)
    logger.info(f"アタックリスト完了: {len(data)}社")
    return data
