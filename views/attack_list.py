"""アタックリスト出力ビュー"""
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from src.agent.claude_agent import generate_attack_list
from src.scorer.scoring_engine import rank_companies
from src.output.excel_writer import write_attack_list_excel, write_csv
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL
from utils.styles import C


def render():
    ui = st.session_state.get("user_input", {})
    selected_industries = st.session_state.get("selected_industries", [])

    if not ui:
        st.warning("情報入力を完了してください。")
        if st.button("← 情報入力へ"):
            st.session_state.page = "input"
            st.rerun()
        return
    if not selected_industries:
        st.warning("業界3C分析で業界を選択してください。")
        if st.button("← 3C分析へ"):
            st.session_state.page = "heatmap"
            st.rerun()
        return
    if not ANTHROPIC_API_KEY:
        st.error("❌ ANTHROPIC_API_KEY が設定されていません。")
        return

    # ── 情報バー ──────────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {C['border']};border-radius:10px;
padding:12px 20px;margin-bottom:16px;display:flex;flex-wrap:wrap;gap:16px;align-items:center">
<div><span style="color:{C['text_muted']};font-size:0.78rem">会社</span>
<b style="color:{C['white']};margin-left:8px">{ui.get('company_name','')}</b></div>
<div style="width:1px;height:20px;background:{C['border']}"></div>
<div><span style="color:{C['text_muted']};font-size:0.78rem">サービス</span>
<b style="color:{C['white']};margin-left:8px">{ui.get('service_name','')}</b></div>
<div style="width:1px;height:20px;background:{C['border']}"></div>
<div><span style="color:{C['text_muted']};font-size:0.78rem">対象業界</span>
<b style="color:{C['accent']};margin-left:8px">{' / '.join(selected_industries)}</b></div>
</div>
""", unsafe_allow_html=True)

    # ── 生成ボタン ────────────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    with col1:
        gen_btn = st.button("アタックリストを生成する",
                            use_container_width=True,
                            disabled=bool(st.session_state.get("attack_list")),
                            type="primary")
    with col2:
        if st.session_state.get("attack_list"):
            if st.button("再生成", use_container_width=True):
                st.session_state.attack_list = []
                st.rerun()

    if gen_btn and not st.session_state.get("attack_list"):
        with st.spinner("企業リストを生成中（30秒〜2分）..."):
            try:
                raw = generate_attack_list(
                    company_name=ui["company_name"],
                    service_name=ui["service_name"],
                    strengths=ui["strengths"],
                    target_industries=selected_industries,
                    companies_per_industry=ui.get("companies_per_industry", 10),
                    target_revenue_scale=ui.get("target_revenue_scale", ""),
                    existing_list_context=st.session_state.get("existing_list_context", ""),
                )
                st.session_state.attack_list = rank_companies(raw)
                st.success(f"{len(st.session_state.attack_list)}社のリストを生成しました！")
            except Exception as e:
                st.error(f"❌ エラー: {e}")
                return

    attack_list = st.session_state.get("attack_list", [])
    if not attack_list:
        st.markdown(f"""
<div style="background:{C['surface']};border:1px dashed {C['border']};border-radius:10px;
padding:32px;text-align:center">
<p style="color:{C['text_muted']}">「アタックリストを生成する」ボタンを押してください</p>
</div>""", unsafe_allow_html=True)
        return

    # ── フィルター ────────────────────────────────────────────────────────────
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        f_ind = st.multiselect("業界", list({c["industry"] for c in attack_list}))
    with col_f2:
        min_s = st.slider("最低スコア", 0, 100, 0)
    with col_f3:
        f_conf = st.multiselect("データ確度", ["high","medium","low"], default=["high","medium","low"])
    filtered = [
        c for c in attack_list
        if (not f_ind or c["industry"] in f_ind)
        and c.get("total_score", 0) >= min_s
        and c.get("data_confidence","medium") in f_conf
    ]
    st.caption(f"表示: {len(filtered)} / {len(attack_list)} 社")

    # ── TOP3 カード ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"<h4 style='color:{C['accent']}'>TOP 3</h4>", unsafe_allow_html=True)
    conf_color = {"high": C['success'], "medium": C['warning'], "low": C['danger']}
    medals = ["🥇","🥈","🥉"]
    cols = st.columns(min(3, len(filtered)))
    for col, company, medal in zip(cols, filtered[:3], medals):
        sc = company.get("total_score", 0)
        cc = conf_color.get(company.get("data_confidence","medium"), C['text_muted'])
        with col:
            st.markdown(f"""
<div style="background:linear-gradient(160deg,{C['surface']},{C['surface2']});
border:1px solid {C['border']};border-top:3px solid {C['accent']};
border-radius:12px;padding:18px 20px;height:100%">
<div style="font-size:1.4rem">{medal}</div>
<div style="color:{C['white']};font-size:1.02rem;font-weight:700;margin:6px 0 2px">{company.get('company_name','')}</div>
<div style="color:{C['text_muted']};font-size:0.82rem;margin-bottom:10px">{company.get('industry','')}</div>
<div style="color:{C['text_muted']};font-size:0.76rem">売上規模</div>
<div style="color:{C['white']};font-size:0.88rem;margin-bottom:8px">{company.get('revenue_scale','—')}</div>
<div style="background:{C['bg']};border-radius:4px;height:6px;overflow:hidden;margin-bottom:4px">
<div style="width:{sc}%;height:100%;background:linear-gradient(90deg,{C['accent']},{C['accent2']});border-radius:4px"></div>
</div>
<div style="display:flex;justify-content:space-between;margin-bottom:8px">
<span style="color:{C['text_muted']};font-size:0.76rem">スコア</span>
<span style="color:{C['white']};font-weight:700">{sc}/100</span>
</div>
<div style="color:{C['text']};font-size:0.84rem">{company.get('compatibility_comment','—')}</div>
<div style="margin-top:8px;color:{cc};font-size:0.74rem">● 確度: {company.get('data_confidence','—')}</div>
</div>""", unsafe_allow_html=True)

    # ── テーブル ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"<h4 style='color:{C['accent']}'>一覧</h4>", unsafe_allow_html=True)
    conf_label = {"high":"🟢 高","medium":"🟡 中","low":"🔴 低"}
    df = pd.DataFrame([{
        "順位": c["rank"],
        "企業名": c.get("company_name",""),
        "業界": c.get("industry",""),
        "売上規模": c.get("revenue_scale",""),
        "ICP": c.get("icp_fit_score",""),
        "フィット": c.get("solution_fit_score",""),
        "競合余地": c.get("competitor_saturation_score",""),
        "総合スコア": c.get("total_score",""),
        "相性コメント": c.get("compatibility_comment",""),
        "アプローチ": c.get("approach_hint",""),
        "確度": conf_label.get(c.get("data_confidence","medium"),"—"),
    } for c in filtered])
    st.dataframe(
        df, hide_index=True, use_container_width=True,
        height=min(600, len(filtered)*38+50),
        column_config={
            "総合スコア": st.column_config.ProgressColumn("総合スコア", min_value=0, max_value=100, format="%d"),
            "ICP": st.column_config.NumberColumn(format="%d"),
            "フィット": st.column_config.NumberColumn(format="%d"),
            "競合余地": st.column_config.NumberColumn(format="%d"),
        },
    )

    # ── ダウンロード ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"<h4 style='color:{C['accent']}'>ダウンロード</h4>", unsafe_allow_html=True)
    meta = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "company_name": ui["company_name"],
        "service_name": ui["service_name"],
        "strengths": ui["strengths"],
        "existing_industry": ui["existing_industry"],
        "target_industry_count": len(selected_industries),
        "company_count": len(filtered),
        "model": CLAUDE_MODEL,
    }
    col_e, col_c = st.columns(2)
    with col_e:
        if st.button("Excel を生成", use_container_width=True):
            with st.spinner("生成中..."):
                try:
                    path = write_attack_list_excel(filtered, st.session_state.get("industry_analysis", []), meta)
                    with open(path, "rb") as f:
                        st.download_button("Excel を保存", data=f.read(),
                            file_name=os.path.basename(path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True)
                except Exception as e:
                    st.error(f"Excel生成エラー: {e}")
    with col_c:
        if st.button("CSV を生成", use_container_width=True):
            with st.spinner("生成中..."):
                try:
                    path = write_csv(filtered)
                    with open(path, "rb") as f:
                        st.download_button("CSV を保存", data=f.read(),
                            file_name=os.path.basename(path), mime="text/csv",
                            use_container_width=True)
                except Exception as e:
                    st.error(f"CSV生成エラー: {e}")

    st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {C['border']};border-radius:8px;padding:12px 16px;margin-top:12px">
<p style="color:{C['text_muted']};font-size:0.82rem;margin:0">
本リストはAIが公開情報を基に生成した<b>推定情報</b>です。最終判断は必ず人間が行ってください。
</p>
</div>""", unsafe_allow_html=True)
