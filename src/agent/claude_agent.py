"""
Claude API エージェント
- 全業界網羅3C分析
- 企業スコアリング・アタックリスト生成
"""
from __future__ import annotations
import json
import re
import anthropic
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL
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


def _clean_json(raw: str) -> str:
    """Claude が返した文字列を valid JSON に修正する"""
    # コードブロック除去
    raw = re.sub(r"```(?:json)?", "", raw).strip()
    raw = raw.rstrip("`").strip()

    # 日本語引用符 → ASCII ダブルクォート
    raw = raw.replace("「", '"').replace("」", '"')
    raw = raw.replace("「", '"').replace("」", '"')

    # シングルクォートをダブルクォートに（値部分のみ、JSONキー周辺）
    # キーの前後: {'key': 'val'} → {"key": "val"}
    raw = re.sub(r"'([^']*)'(\s*:)", r'"\1"\2', raw)   # 'key':
    raw = re.sub(r":\s*'([^']*)'", r': "\1"', raw)      # : 'val'

    # 末尾カンマ除去（JSON非対応）
    raw = re.sub(r",\s*([}\]])", r"\1", raw)

    return raw


def _parse_json_safe(raw: str) -> list | dict:
    """JSONパースを複数段階でリトライする"""
    # 1st try: そのまま
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 2nd try: クリーニング後
    cleaned = _clean_json(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3rd try: [...] ブロック抽出
    m = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    # 4th try: {...} ブロック抽出（単一オブジェクトの場合）
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if m:
        try:
            return [json.loads(m.group(0))]
        except json.JSONDecodeError:
            pass

    raise ValueError(f"JSONパース失敗。先頭300文字:\n{raw[:300]}")


# 業界リストを分割してバッチ処理
_BATCH_SIZE = 15


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
    バッチ処理で分割して速度向上 + JSON安定化。
    """
    all_results: list[dict] = []
    batches = [
        ALL_INDUSTRIES[i:i + _BATCH_SIZE]
        for i in range(0, len(ALL_INDUSTRIES), _BATCH_SIZE)
    ]
    logger.info(f"全業界分析: {len(ALL_INDUSTRIES)}業界 / {len(batches)}バッチ")

    # Company軸ラベルは1回目のバッチで確定させ、以降は使い回す
    col1_label: str = ""
    col2_label: str = ""

    for batch_idx, batch in enumerate(batches):
        logger.info(f"バッチ {batch_idx+1}/{len(batches)}: {batch}")

        # ウェブコンテキストをこのバッチ分だけ添付
        ctx_block = ""
        if web_contexts:
            for ind in batch:
                ctx = web_contexts.get(ind, "")
                if ctx:
                    ctx_block += f"\n[{ind}] {ctx[:200]}"

        label_instruction = ""
        if batch_idx == 0:
            label_instruction = f"""
### Company軸の命名（このバッチで決定し、以降のバッチでも同じラベルを使うこと）
"{service_name}" の特性を踏まえ、業界との相性を表す2つの観点を命名してください。
例: サービスがSNSマーケなら「インフルエンサー適合性」「SNS広告効率」など"""
        else:
            label_instruction = f"""
### Company軸のラベル（固定）
fit_column1_label = "{col1_label}"
fit_column2_label = "{col2_label}"
上記のラベルを必ず使うこと。"""

        industries_str = json.dumps(batch, ensure_ascii=False)

        # 全バッチ共通のevaluation分布指示（全体で◎/○が必ず出るよう）
        eval_distribution = ""
        if batch_idx == 0:
            eval_distribution = f"""
## Evaluation distribution rule (STRICT)
Across ALL {len(ALL_INDUSTRIES)} industries analyzed in all batches combined:
- ◎ (最優先): assign to at least 3 industries — the best fits for this service
- ○ (優先): assign to at least 5 industries — good fits
- △ (要検討): moderate fit
- × (優先度低): poor fit
For THIS batch of {len(batch)} industries, assign ◎ to the top 1-2 and ○ to the next 2-3 if they qualify.
Do NOT assign only △ and × — always find the relative best industries in each batch."""
        else:
            eval_distribution = f"""
## Evaluation distribution rule (STRICT)
Even in this batch, assign ◎ to the 1-2 best-fitting industries and ○ to the next 2-3.
Do NOT assign only △ and × to all industries in this batch."""

        prompt = f"""Analyze the following industries for a Japanese company and return a JSON array.

## Company Info
- Company: {company_name}
- Service: {service_name}
- Strengths: {strengths}
- Current main clients: {existing_industry}
{f"- Target company revenue scale: {target_revenue_scale}" if target_revenue_scale else ""}
{f"- Market context: {broad_context[:400]}" if broad_context else ""}
{existing_list_context[:800] if existing_list_context else ""}
{ctx_block}

## Industries to analyze (analyze ALL of them)
{industries_str}

{label_instruction}
{eval_distribution}

## Output format (JSON array, one object per industry)
Return ONLY a JSON array like this:
[
  {{
    "industry": "exact industry name from input list",
    "category": "parent category name in Japanese",
    "market_size": "market size e.g. 3兆円 or 6,300億円（推定）",
    "growth_actual": "recent 3yr growth e.g. +3〜4%",
    "growth_future": "future 3yr forecast e.g. +3〜5%",
    "market_overview": "market overview in 1-2 Japanese sentences",
    "fit_column1_label": "Company axis 1 label",
    "fit_column1": "evaluation comment 1 sentence",
    "fit_column2_label": "Company axis 2 label",
    "fit_column2": "evaluation comment 1 sentence",
    "competitor_summary": "competitor situation 1 sentence",
    "evaluation": "◎",
    "score": 85,
    "data_source_note": "data source note"
  }}
]

IMPORTANT: Output ONLY the JSON array. No other text."""

        try:
            resp = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4096,
                system=[{
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }],
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.content[0].text.strip()
            logger.debug(f"バッチ{batch_idx+1} 先頭200文字: {raw[:200]}")

            batch_data = _parse_json_safe(raw)

            # Company軸ラベルを1バッチ目で固定
            if batch_idx == 0 and batch_data:
                col1_label = batch_data[0].get("fit_column1_label", col1_label)
                col2_label = batch_data[0].get("fit_column2_label", col2_label)

            # カテゴリ補完
            for item in batch_data:
                if not item.get("category"):
                    item["category"] = INDUSTRY_TO_CATEGORY.get(
                        item.get("industry", ""), "その他"
                    )
                # ラベルを統一
                if col1_label:
                    item["fit_column1_label"] = col1_label
                if col2_label:
                    item["fit_column2_label"] = col2_label

            all_results.extend(batch_data)
            logger.info(f"バッチ{batch_idx+1} 完了: {len(batch_data)}業界取得")

        except Exception as e:
            logger.error(f"バッチ{batch_idx+1} エラー: {e}")
            # エラーが出たバッチはスキップしてフォールバックデータを追加
            for ind in batch:
                all_results.append({
                    "industry": ind,
                    "category": INDUSTRY_TO_CATEGORY.get(ind, "その他"),
                    "market_size": "—",
                    "growth_actual": "—",
                    "growth_future": "—",
                    "market_overview": "取得エラー（再分析をお試しください）",
                    "fit_column1_label": col1_label or "適合度①",
                    "fit_column1": "—",
                    "fit_column2_label": col2_label or "適合度②",
                    "fit_column2": "—",
                    "competitor_summary": "—",
                    "evaluation": "△",
                    "score": 0,
                    "data_source_note": f"エラー: {e}",
                })

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
    """対象業界の具体企業リストとスコアを生成"""
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

    logger.info(f"アタックリスト生成: {target_industries}")
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8192,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()

    data = _parse_json_safe(raw)
    logger.info(f"アタックリスト完了: {len(data)}社")
    return data
