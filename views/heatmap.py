"""業界3Cヒートマップ ビュー"""
import streamlit as st
from src.agent.claude_agent import analyze_all_industries
from src.data_fetcher.industry_search import fetch_industry_web_context, fetch_broad_market_context
from config.industries import ALL_INDUSTRIES, INDUSTRY_CATEGORIES
from config.settings import ANTHROPIC_API_KEY
from utils.styles import C

EVAL_CSS = {
    "◎": "background:#1a3d2a;color:#3ecf8e;border:1px solid #3ecf8e;",
    "○": "background:#3a3210;color:#f0c040;border:1px solid #f0c040;",
    "△": "background:#3a2510;color:#f09040;border:1px solid #f09040;",
    "×": "background:#3a1010;color:#f06060;border:1px solid #f06060;",
}


def render():
    ui = st.session_state.get("user_input", {})
    if not ui:
        st.warning("先に情報入力を完了してください。")
        if st.button("← 情報入力へ戻る"):
            st.session_state.page = "input"
            st.rerun()
        return

    if not ANTHROPIC_API_KEY:
        st.error("❌ ANTHROPIC_API_KEY が設定されていません。")
        return

    # ── 情報バー ────────────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {C['border']};border-radius:10px;
padding:12px 20px;margin-bottom:16px;display:flex;flex-wrap:wrap;gap:16px;align-items:center">
<div><span style="color:{C['text_muted']};font-size:0.78rem">会社</span>
<b style="color:{C['white']};margin-left:8px">{ui.get('company_name','')}</b></div>
<div style="width:1px;height:20px;background:{C['border']}"></div>
<div><span style="color:{C['text_muted']};font-size:0.78rem">サービス</span>
<b style="color:{C['white']};margin-left:8px">{ui.get('service_name','')}</b></div>
<div style="width:1px;height:20px;background:{C['border']}"></div>
<div><span style="color:{C['text_muted']};font-size:0.78rem">分析対象</span>
<b style="color:{C['accent']};margin-left:8px">{len(ALL_INDUSTRIES)}業界 自動網羅</b></div>
</div>
""", unsafe_allow_html=True)

    # ── 分析実行 UI ──────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([3, 1, 1])
    already_done = bool(st.session_state.get("industry_analysis"))
    with col1:
        run_btn = st.button("全業界を分析する", use_container_width=True,
                            disabled=already_done, type="primary")
    with col2:
        use_web = st.toggle("ウェブ補強", value=False, disabled=already_done,
                            help="ONで+1〜2分、精度向上")
    with col3:
        if already_done and st.button("再分析", use_container_width=True):
            st.session_state.industry_analysis = []
            st.session_state.selected_industries = []
            st.rerun()

    # ── 分析実行 ────────────────────────────────────────────────────────────────
    if run_btn and not st.session_state.get("industry_analysis"):
        progress = st.progress(0, text="準備中...")
        status = st.empty()
        try:
            web_contexts, broad_ctx = {}, ""
            if use_web:
                status.info("ウェブ検索中...")
                progress.progress(15, text="ウェブ取得中...")
                try:
                    web_contexts = fetch_industry_web_context(ALL_INDUSTRIES[:20], ui["service_name"])
                    broad_ctx = fetch_broad_market_context(ui["service_name"], ui["strengths"])
                except Exception as e:
                    st.warning(f"ウェブ取得一部失敗（Claude知識で補完）: {e}")
                progress.progress(35)

            status.info("Claude が全業界を3C分析中（約1〜2分）...")
            progress.progress(40, text="バッチ分析中...")
            result = analyze_all_industries(
                company_name=ui["company_name"],
                service_name=ui["service_name"],
                strengths=ui["strengths"],
                existing_industry=ui["existing_industry"],
                target_revenue_scale=ui.get("target_revenue_scale", ""),
                web_contexts=web_contexts,
                broad_context=broad_ctx,
                existing_list_context=st.session_state.get("existing_list_context", ""),
            )
            st.session_state.industry_analysis = result
            st.session_state.current_step = max(st.session_state.get("current_step", 3), 4)
            progress.progress(100, text="完了！")
            status.success(f"{len(result)}業界の分析が完了しました！")
        except Exception as e:
            progress.empty()
            status.error(f"❌ エラー: {e}")
            return

    analysis: list[dict] = st.session_state.get("industry_analysis", [])
    if not analysis:
        st.markdown(f"""
<div style="background:{C['surface']};border:1px dashed {C['border']};border-radius:10px;
padding:32px;text-align:center;margin-top:20px">
<p style="color:{C['text_muted']}">「全業界を分析する」ボタンを押してください</p>
</div>""", unsafe_allow_html=True)
        return

    # ── 集計バッジ ──────────────────────────────────────────────────────────────
    counts = defaultdict(int)
    for r in analysis:
        counts[r.get("evaluation", "△")] += 1

    c1, c2, c3, c4 = st.columns(4)
    for col, ev, label, color in [
        (c1, "◎", "最優先", C['success']),
        (c2, "○", "優先",   C['warning']),
        (c3, "△", "要検討", "#f09040"),
        (c4, "×", "優先度低", C['danger']),
    ]:
        with col:
            st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {color};border-top:3px solid {color};
border-radius:10px;padding:14px;text-align:center">
<div style="font-size:1.8rem;font-weight:900;color:{color}">{ev}</div>
<div style="font-size:1.5rem;font-weight:700;color:{C['white']}">{counts[ev]}</div>
<div style="font-size:0.78rem;color:{C['text_muted']}">{label}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── フィルター ───────────────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        filter_eval = st.multiselect("評価で絞込", ["◎","○","△","×"], default=["◎","○"])
    with col_f2:
        filter_cat = st.multiselect("カテゴリで絞込", list(INDUSTRY_CATEGORIES.keys()))

    filtered = [
        r for r in analysis
        if (not filter_eval or r.get("evaluation") in filter_eval)
        and (not filter_cat or r.get("category") in filter_cat)
    ]

    col1_label = analysis[0].get("fit_column1_label", "適合度①") if analysis else "適合度①"
    col2_label = analysis[0].get("fit_column2_label", "適合度②") if analysis else "適合度②"

    # ── 一覧テーブル（全業界を1枚に） ────────────────────────────────────────────
    st.subheader(f"業界評価テーブル（{len(filtered)}業界）")
    st.caption(f"Company軸: **{col1_label}** / **{col2_label}**　　※ 市場規模・成長率は公開情報ベースの推定値を含みます。")

    # スクロール可能な単一テーブル
    rows_html = ""
    for i, r in enumerate(filtered):
        ev = r.get("evaluation", "△")
        ec = {"◎": "em2", "○": "em1", "△": "ed", "×": "ex"}.get(ev, "ed")
        row_bg = C['surface2'] if i % 2 == 1 else C['surface']
        rows_html += f"""
<tr>
<td class="{ec}" style="text-align:center;font-size:16px;font-weight:700">{ev}</td>
<td style="font-weight:600;color:{C['white']};background:{row_bg}">{r.get('industry','')}</td>
<td style="color:{C['text_muted']};font-size:11px;background:{row_bg}">{r.get('category','')}</td>
<td style="text-align:center;background:{row_bg}">{r.get('market_size','—')}</td>
<td style="text-align:center;background:{row_bg}">{r.get('growth_actual','—')}</td>
<td style="text-align:center;background:{row_bg}">{r.get('growth_future','—')}</td>
<td style="background:{row_bg}">{r.get('market_overview','—')}</td>
<td style="background:{row_bg}">{r.get('fit_column1','—')}</td>
<td style="background:{row_bg}">{r.get('fit_column2','—')}</td>
<td style="font-size:11px;background:{row_bg}">{r.get('competitor_summary','—')}</td>
</tr>"""

    html = f"""
<style>
.t3c{{font-size:12px;border-collapse:collapse;width:100%;color:{C['text']}}}
.t3c th{{background:#0a1e3a;color:{C['text_muted']};padding:8px 10px;text-align:center;
  border:1px solid {C['border']};font-weight:500;font-size:11px;position:sticky;top:0;z-index:1}}
.t3c th.hg1{{color:{C['accent']};font-weight:700}}
.t3c th.hg2{{color:#a0c4ff;font-weight:700}}
.t3c td{{padding:7px 10px;border:1px solid {C['border']};vertical-align:top}}
.em2{{background:#1a3d2a!important;color:#3ecf8e}}
.em1{{background:#3a3210!important;color:#f0c040}}
.ed{{background:#3a2510!important;color:#f09040}}
.ex{{background:#3a1010!important;color:#f06060}}
</style>
<div style="overflow-x:auto;max-height:600px;overflow-y:auto;border:1px solid {C['border']};border-radius:8px">
<table class="t3c">
<thead>
<tr>
<th style="min-width:44px">評価</th>
<th style="min-width:110px;text-align:left">業界</th>
<th style="min-width:90px">カテゴリ</th>
<th class="hg1" style="min-width:80px">市場規模</th>
<th class="hg1" style="min-width:60px">実績成長</th>
<th class="hg1" style="min-width:60px">将来予測</th>
<th class="hg1" style="min-width:180px">市場概況</th>
<th class="hg2" style="min-width:150px">{col1_label}</th>
<th class="hg2" style="min-width:150px">{col2_label}</th>
<th style="min-width:150px">競合状況</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
</div>"""

    st.markdown(html, unsafe_allow_html=True)

    # ── TOP10 ────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("総合スコア TOP 10")
    top10 = sorted(analysis, key=lambda x: x.get("score", 0), reverse=True)[:10]
    for i, r in enumerate(top10, 1):
        ev = r.get("evaluation", "△")
        ev_s = EVAL_CSS.get(ev, "")
        score = r.get("score", 0)
        st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {C['border']};border-radius:8px;
padding:10px 16px;margin-bottom:6px;display:flex;align-items:center;gap:12px">
<div style="color:{C['text_muted']};font-size:0.85rem;min-width:24px">#{i}</div>
<div style="{ev_s}border-radius:5px;padding:2px 8px;font-size:0.9rem;font-weight:700;min-width:32px;text-align:center">{ev}</div>
<div style="color:{C['white']};font-weight:600;min-width:140px">{r.get('industry','')}</div>
<div style="color:{C['text_muted']};font-size:0.8rem;min-width:100px">{r.get('category','')}</div>
<div style="flex:1;background:{C['surface2']};border-radius:4px;height:8px;overflow:hidden">
  <div style="width:{score}%;height:100%;background:linear-gradient(90deg,{C['accent']},{C['accent2']});border-radius:4px"></div>
</div>
<div style="color:{C['white']};font-weight:700;min-width:36px;text-align:right">{score}</div>
</div>""", unsafe_allow_html=True)

    # ── 業界選択 & 次へ ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("アタックリストを生成する業界を選択")
    priority = [r["industry"] for r in top10 if r.get("evaluation") in ("◎","○")]
    selected = st.multiselect(
        "業界を選択（3〜5業界推奨）",
        options=[r["industry"] for r in analysis],
        default=st.session_state.get("selected_industries") or priority[:3],
        help="◎/○ 評価の業界が自動選択されています",
    )

    if st.button(f"📋 {len(selected)} 業界でアタックリストを生成 →",
                 disabled=not selected, type="primary", use_container_width=True):
        st.session_state.selected_industries = selected
        st.session_state.attack_list = []
        st.session_state.page = "attack_list"
        st.session_state.current_step = 4
        st.rerun()
