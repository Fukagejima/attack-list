"""
既存アタックリストCSVのパーサー
アップロードされたCSVから営業パターンを抽出し、
Claude分析のコンテキストとして利用する
"""
from __future__ import annotations
import io
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

# カラム名の候補（表記ゆれ対応）
_COL_MAP = {
    "industry":  ["業界", "industry", "Industry"],
    "company":   ["企業名", "会社名", "company", "Company"],
    "revenue":   ["売上規模", "売上", "revenue"],
    "status":    ["ステータス", "status", "Status"],
    "theme":     ["支援テーマ", "テーマ", "備考", "メモ", "theme"],
    "listed":    ["上場区分", "上場", "listed"],
    "score":     ["受注確度", "確度", "score"],
}


def _find_col(df: pd.DataFrame, key: str) -> str | None:
    for candidate in _COL_MAP.get(key, []):
        if candidate in df.columns:
            return candidate
    return None


def parse_csv(file_bytes: bytes) -> tuple[pd.DataFrame, dict]:
    """
    アップロードされたCSVを解析して (DataFrame, summary_dict) を返す。
    summary_dict はClaudeへのコンテキストとして使用する。
    """
    # エンコーディング自動判別（BOM付きUTF-8 / Shift-JIS 対応）
    for enc in ("utf-8-sig", "utf-8", "shift_jis", "cp932"):
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding=enc)
            logger.info(f"CSV読み込み成功: {enc} / {len(df)}行 / 列: {list(df.columns)}")
            break
        except Exception:
            continue
    else:
        raise ValueError("CSVの読み込みに失敗しました。UTF-8またはShift-JIS形式で保存してください。")

    summary = _extract_summary(df)
    return df, summary


def _extract_summary(df: pd.DataFrame) -> dict:
    summary: dict = {"row_count": len(df)}

    # ── 業界分布 ────────────────────────────────────────────────────────────────
    ind_col = _find_col(df, "industry")
    if ind_col:
        counts = df[ind_col].dropna().value_counts().head(10).to_dict()
        summary["industry_distribution"] = counts
        summary["top_industries"] = list(counts.keys())[:5]

    # ── ステータス分布 ──────────────────────────────────────────────────────────
    st_col = _find_col(df, "status")
    if st_col:
        summary["status_distribution"] = df[st_col].dropna().value_counts().to_dict()

    # ── 上場区分 ────────────────────────────────────────────────────────────────
    li_col = _find_col(df, "listed")
    if li_col:
        summary["listed_distribution"] = df[li_col].dropna().value_counts().to_dict()

    # ── 売上規模 ────────────────────────────────────────────────────────────────
    rev_col = _find_col(df, "revenue")
    if rev_col:
        summary["revenue_distribution"] = df[rev_col].dropna().value_counts().to_dict()

    # ── 支援テーマ ──────────────────────────────────────────────────────────────
    th_col = _find_col(df, "theme")
    if th_col:
        themes = df[th_col].dropna().tolist()
        summary["theme_samples"] = themes[:10]

    # ── 既存企業名 ──────────────────────────────────────────────────────────────
    co_col = _find_col(df, "company")
    if co_col:
        summary["existing_companies"] = df[co_col].dropna().tolist()

    logger.info(f"サマリー抽出完了: {summary}")
    return summary


def format_context_for_claude(summary: dict) -> str:
    """summary を Claude プロンプトに埋め込む文字列に変換"""
    lines = ["## 既存アタックリスト（アップロード済み）の分析"]
    lines.append(f"- 総件数: {summary.get('row_count', '不明')}社")

    if "industry_distribution" in summary:
        dist = summary["industry_distribution"]
        total = sum(dist.values())
        ind_str = " / ".join(
            f"{k}({round(v/total*100)}%)" for k, v in list(dist.items())[:6]
        )
        lines.append(f"- 業界分布: {ind_str}")

    if "status_distribution" in summary:
        st = summary["status_distribution"]
        won = st.get("受注", 0) + st.get("受注済", 0)
        total_st = sum(st.values())
        lines.append(f"- ステータス: {dict(list(st.items())[:5])} （受注率{round(won/total_st*100) if total_st else 0}%）")

    if "listed_distribution" in summary:
        lines.append(f"- 上場区分: {summary['listed_distribution']}")

    if "revenue_distribution" in summary:
        lines.append(f"- 売上規模: {dict(list(summary['revenue_distribution'].items())[:4])}")

    if "theme_samples" in summary:
        themes = summary["theme_samples"][:6]
        lines.append(f"- 主な支援テーマ: {' / '.join(str(t) for t in themes)}")

    if "existing_companies" in summary:
        companies = summary["existing_companies"][:8]
        lines.append(f"- 既存顧客サンプル: {' / '.join(str(c) for c in companies)}")

    lines.append("")
    lines.append("※ 上記の既存顧客パターンを参考に、")
    lines.append("  ① 既存業界内の類似企業（横展開候補）")
    lines.append("  ② 既存業界と親和性の高い新規業界（ポテンシャル候補）")
    lines.append("  の両方を考慮して分析・リストアップしてください。")

    return "\n".join(lines)
