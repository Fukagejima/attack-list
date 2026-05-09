import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from collections import defaultdict
from src.agent.claude_agent import analyze_all_industries
from src.data_fetcher.industry_search import fetch_industry_web_context, fetch_broad_market_context
from config.industries import ALL_INDUSTRIES, INDUSTRY_CATEGORIES
from config.settings import ANTHROPIC_API_KEY
from utils.styles import inject_global_css, page_header, C

st.set_page_config(page_title="業界ヒートマップ", page_icon="🌡️", layout="wide")
inject_global_css()

EVAL_CSS = {
    "◎": f"background:#1a3d2a;color:#3ecf8e;border:1px solid #3ecf8e;",
    "○": f"background:#3a3210;color:#f0c040;border:1px solid #f0c040;",
    "△": f"background:#3a2510;color:#f09040;border:1px solid #f09040;",
    "×": f"background:#3a1010;color:#f06060;border:1px solid #f06060;",
}


def init_session():
    defaults = {
        "authenticated": False,
        "user_input": {},
        "industry_analysis": [],
        "selected_industries": [],
        "attack_list": [],
        "current_step": 1,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

if not st.session_state.authenticated:
    st.warning("⚠️ ログインが必要です。")
    st.stop()
if not st.session_state.get("user_input"):
    st.warning("⚠️ 先に **② 情報入力** を完了してください。")
    st.stop()
if not ANTHROPIC_API_KEY:
    st.error("❌ ANTHROPIC_API_KEY が設定されていません。.env ファイルを確認してください。")
    st.stop()

page_header("🌡️", "業界優先度分析 — 3C ヒートマップ", f"全{len(ALL_INDUSTRIES)}業界を自動評価します")

ui = st.session_state.user_input

# ── 分析実行 UI ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {C['border']};border-radius:10px;padding:14px 20px;margin-bottom:16px;display:flex;align-items:center;gap:16px">
<div>
  <span style="color:{C['text_muted']};font-size:0.8rem">会社</span>
  <span style="color:{C['white']};font-weight:600;margin-left:8px">{ui['company_name']}</span>
</div>
<div style="width:1px;height:20px;background:{C['border']}"></div>
<div>
  <span style="color:{C['text_muted']};font-size:0.8rem">サービス</span>
  <span style="color:{C['white']};font-weight:600;margin-left:8px">{ui['service_name']}</span>
</div>
<div style="width:1px;height:20px;background:{C['border']}"></div>
<div>
  <span style="color:{C['text_muted']};font-size:0.8rem">分析対象</span>
  <span style="color:{C['accent']};font-weight:700;margin-left:8px">{len(ALL_INDUSTRIES)}業界</span>
</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    already_done = bool(st.session_state.industry_analysis)
    run_btn = st.button(
        "🚀 全業界を分析する",
        use_container_width=True,
        disabled=already_done,
        type="primary",
    )
with col2:
    use_web = st.toggle(
        "🌐 ウェブ検索で補強",
        value=False,
        help="ONにすると+1〜2分かかりますが精度が上がります",
        disabled=already_done,
    )
with col3:
    if already_done:
        if st.button("🔄 再分析する", use_container_width=True):
            st.session_state.industry_analysis = []
            st.session_state.selected_industries = []
            st.rerun()

# ── 分析実行 ─────────────────────────────────────────────────────────────────
if run_btn and not st.session_state.industry_analysis:
    progress = st.progress(0, text="準備中...")
    status = st.empty()

    try:
        web_contexts = {}
        broad_ctx = ""

        if use_web:
            status.info("🌐 ウェブから市場情報を取得中...")
            progress.progress(10, text="ウェブ検索中...")
            try:
                web_contexts = fetch_industry_web_context(ALL_INDUSTRIES[:20], ui["service_name"])
                broad_ctx = fetch_broad_market_context(ui["service_name"], ui["strengths"])
            except Exception as e:
                st.warning(f"⚠️ ウェブ取得一部失敗（Claude知識で補完）: {e}")
            progress.progress(35, text="ウェブ取得完了")

        status.info("🤖 Claude が全業界を3C分析中（約1〜2分）...")
        progress.progress(40, text="バッチ1/2 分析中...")

        result = analyze_all_industries(
            company_name=ui["company_name"],
            service_name=ui["service_name"],
            strengths=ui["strengths"],
            existing_industry=ui["existing_industry"],
            web_contexts=web_contexts,
            broad_context=broad_ctx,
        )

        progress.progress(95, text="整理中...")
        st.session_state.industry_analysis = result
        st.session_state.current_step = max(st.session_state.current_step, 4)
        progress.progress(100, text="完了！")
        status.success(f"✅ 分析完了！{len(result)}業界を評価しました。")

    except Exception as e:
        progress.empty()
        status.error(f"❌ エラーが発生しました: {e}")
        st.stop()

analysis: list[dict] = st.session_state.industry_analysis
if not analysis:
    st.markdown(f"""
<div style="background:{C['surface']};border:1px dashed {C['border']};border-radius:10px;padding:32px;text-align:center;margin-top:20px">
<p style="color:{C['text_muted']};font-size:1rem">「全業界を分析する」ボタンを押してください</p>
</div>
""", unsafe_allow_html=True)
    st.stop()

# ── 集計バッジ ─────────────────────────────────────────────────────────────────
counts = defaultdict(int)
for row in analysis:
    counts[row.get("evaluation", "△")] += 1

c1, c2, c3, c4 = st.columns(4)
for col, ev, label, color in [
    (c1, "◎", "最優先アタック", C['success']),
    (c2, "○", "優先アタック",   C['warning']),
    (c3, "△", "要検討",         "#f09040"),
    (c4, "×", "優先度低",       C['danger']),
]:
    with col:
        st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {color};border-top:3px solid {color};border-radius:10px;padding:14px;text-align:center">
<div style="font-size:1.8rem;font-weight:900;color:{color}">{ev}</div>
<div style="font-size:1.5rem;font-weight:700;color:{C['white']}">{counts[ev]}</div>
<div style="font-size:0.78rem;color:{C['text_muted']}">{label}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── フィルター ────────────────────────────────────────────────────────────────
col_f1, col_f2 = st.columns([1, 2])
with col_f1:
    filter_eval = st.multiselect("評価で絞込", options=["◎","○","△","×"], default=["◎","○"])
with col_f2:
    filter_cat = st.multiselect("カテゴリで絞込", options=list(INDUSTRY_CATEGORIES.keys()))

filtered = [
    r for r in analysis
    if (not filter_eval or r.get("evaluation") in filter_eval)
    and (not filter_cat or r.get("category") in filter_cat)
]

col1_label = analysis[0].get("fit_column1_label", "適合度①") if analysis else "適合度①"
col2_label = analysis[0].get("fit_column2_label", "適合度②") if analysis else "適合度②"

# ── メインテーブル ─────────────────────────────────────────────────────────────
st.subheader(f"📊 業界評価テーブル（{len(filtered)}業界）")
st.caption(f"Company軸: **{col1_label}** / **{col2_label}**")

grouped: dict[str, list[dict]] = defaultdict(list)
for row in filtered:
    grouped[row.get("category", "その他")].append(row)

for cat, rows in grouped.items():
    ev_summary = "".join(
        f'<span style="{EVAL_CSS.get(r.get("evaluation","△"))}border-radius:4px;padding:1px 5px;font-size:0.75rem;margin-left:3px">{r.get("evaluation","△")}</span>'
        for r in rows
    )
    with st.expander(f"**{cat}**　{ev_summary}", expanded=True):
        table_html = f"""
<style>
.t3c{{font-size:12px;border-collapse:collapse;width:100%;color:{C['text']}}}
.t3c th{{background:#0f2a50;color:{C['text_muted']};padding:8px 10px;text-align:center;border:1px solid {C['border']};font-weight:500;font-size:11px}}
.t3c th.hg1{{background:#0a1e3a;color:{C['accent']};font-weight:700}}
.t3c th.hg2{{background:#0a1e3a;color:#a0c4ff;font-weight:700}}
.t3c td{{padding:7px 10px;border:1px solid {C['border']};vertical-align:top;background:{C['surface']}}}
.t3c tr:nth-child(even) td{{background:{C['surface2']}}}
.t3c td:first-child{{font-weight:600;color:{C['white']};min-width:110px}}
.ev-maru2{{background:#1a3d2a!important;color:#3ecf8e;font-weight:700;text-align:center;font-size:15px}}
.ev-maru {{background:#3a3210!important;color:#f0c040;font-weight:700;text-align:center;font-size:15px}}
.ev-delta{{background:#3a2510!important;color:#f09040;font-weight:700;text-align:center;font-size:15px}}
.ev-batu {{background:#3a1010!important;color:#f06060;font-weight:700;text-align:center;font-size:15px}}
</style>
<table class="t3c">
<tr>
  <th rowspan="2" style="min-width:110px">業界</th>
  <th colspan="4" class="hg1">Customer（市場）</th>
  <th colspan="2" class="hg2">Company（自社適合）</th>
  <th rowspan="2" style="min-width:120px">競合状況</th>
  <th rowspan="2" style="min-width:44px">評価</th>
</tr>
<tr>
  <th class="hg1" style="min-width:70px">規模</th>
  <th class="hg1" style="min-width:60px">実績</th>
  <th class="hg1" style="min-width:60px">予測</th>
  <th class="hg1" style="min-width:180px">市場概況</th>
  <th class="hg2" style="min-width:150px">{col1_label}</th>
  <th class="hg2" style="min-width:150px">{col2_label}</th>
</tr>
"""
        for row in rows:
            ev = row.get("evaluation", "△")
            ev_cls = {"◎":"ev-maru2","○":"ev-maru","△":"ev-delta","×":"ev-batu"}.get(ev,"ev-delta")
            table_html += f"""
<tr>
  <td>{row.get('industry','')}</td>
  <td style="text-align:center">{row.get('market_size','—')}</td>
  <td style="text-align:center">{row.get('growth_actual','—')}</td>
  <td style="text-align:center">{row.get('growth_future','—')}</td>
  <td>{row.get('market_overview','—')}</td>
  <td>{row.get('fit_column1','—')}</td>
  <td>{row.get('fit_column2','—')}</td>
  <td style="font-size:11px">{row.get('competitor_summary','—')}</td>
  <td class="{ev_cls}">{ev}</td>
</tr>"""
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)
        st.caption("※ 市場規模・成長率は公開情報ベースの推定値を含みます。")

# ── TOP10 ランキング ────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🏆 総合スコア TOP 10")

top10 = sorted(analysis, key=lambda x: x.get("score", 0), reverse=True)[:10]
for i, r in enumerate(top10, 1):
    ev = r.get("evaluation", "△")
    ev_style = EVAL_CSS.get(ev, "")
    score = r.get("score", 0)
    bar_w = int(score)
    st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {C['border']};border-radius:8px;padding:10px 16px;margin-bottom:6px;display:flex;align-items:center;gap:12px">
  <div style="color:{C['text_muted']};font-size:0.85rem;min-width:24px">#{i}</div>
  <div style="{ev_style}border-radius:5px;padding:2px 8px;font-size:0.9rem;font-weight:700;min-width:32px;text-align:center">{ev}</div>
  <div style="color:{C['white']};font-weight:600;min-width:130px">{r.get('industry','')}</div>
  <div style="color:{C['text_muted']};font-size:0.8rem;min-width:90px">{r.get('category','')}</div>
  <div style="flex:1;background:{C['surface2']};border-radius:4px;height:8px;overflow:hidden">
    <div style="width:{bar_w}%;height:100%;background:linear-gradient(90deg,{C['accent']},{C['accent2']});border-radius:4px"></div>
  </div>
  <div style="color:{C['white']};font-weight:700;min-width:36px;text-align:right">{score}</div>
</div>
""", unsafe_allow_html=True)

# ── 業界選択 → アタックリストへ ───────────────────────────────────────────────
st.markdown("---")
st.subheader("✅ アタックリストを生成する業界を選択")

priority_industries = [r["industry"] for r in top10 if r.get("evaluation") in ("◎", "○")]
selected = st.multiselect(
    "業界を選択（3〜5業界推奨）",
    options=[r["industry"] for r in analysis],
    default=st.session_state.selected_industries or priority_industries[:3],
    help="◎/○ 評価の業界が自動選択されています",
)

if st.button(
    f"📋 選択した {len(selected)} 業界でアタックリストを生成 →",
    disabled=not selected,
    type="primary",
):
    st.session_state.selected_industries = selected
    st.session_state.attack_list = []
    st.success(f"✅ {len(selected)}業界を選択。サイドバーから **④ アタックリスト** に進んでください。")
