import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from src.agent.claude_agent import generate_attack_list
from src.scorer.scoring_engine import rank_companies
from src.output.excel_writer import write_attack_list_excel, write_csv
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL
from utils.styles import inject_global_css, page_header, C

st.set_page_config(page_title="アタックリスト", page_icon="📋", layout="wide")
inject_global_css()


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
if not st.session_state.get("selected_industries"):
    st.warning("⚠️ 先に **③ 業界ヒートマップ** で業界を選択してください。")
    st.stop()
if not ANTHROPIC_API_KEY:
    st.error("❌ ANTHROPIC_API_KEY が設定されていません。")
    st.stop()

page_header("📋", "営業アタックリスト", "有望業界の具体企業リストをスコア付きで出力します")

ui = st.session_state.user_input
selected_industries = st.session_state.selected_industries

# ── 情報バー ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {C['border']};border-radius:10px;padding:12px 20px;margin-bottom:16px;display:flex;flex-wrap:wrap;gap:16px">
<div><span style="color:{C['text_muted']};font-size:0.78rem">会社</span><br><b style="color:{C['white']}">{ui['company_name']}</b></div>
<div style="width:1px;background:{C['border']}"></div>
<div><span style="color:{C['text_muted']};font-size:0.78rem">サービス</span><br><b style="color:{C['white']}">{ui['service_name']}</b></div>
<div style="width:1px;background:{C['border']}"></div>
<div><span style="color:{C['text_muted']};font-size:0.78rem">対象業界</span><br><b style="color:{C['accent']}">{' / '.join(selected_industries)}</b></div>
</div>
""", unsafe_allow_html=True)

# ── 生成ボタン ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])
with col1:
    generate_btn = st.button(
        "🚀 アタックリストを生成する",
        use_container_width=True,
        disabled=bool(st.session_state.attack_list),
        type="primary",
    )
with col2:
    if st.session_state.attack_list:
        if st.button("🔄 再生成", use_container_width=True):
            st.session_state.attack_list = []
            st.rerun()

# ── リスト生成 ────────────────────────────────────────────────────────────────
if generate_btn and not st.session_state.attack_list:
    with st.spinner("🤖 Claude が企業リストを生成中（30秒〜2分）..."):
        try:
            raw_list = generate_attack_list(
                company_name=ui["company_name"],
                service_name=ui["service_name"],
                strengths=ui["strengths"],
                target_industries=selected_industries,
                companies_per_industry=ui.get("companies_per_industry", 5),
            )
            ranked = rank_companies(raw_list)
            st.session_state.attack_list = ranked
            st.success(f"✅ {len(ranked)}社のアタックリストを生成しました！")
        except Exception as e:
            st.error(f"❌ 生成中にエラー: {e}")
            st.stop()

attack_list = st.session_state.attack_list
if not attack_list:
    st.markdown(f"""
<div style="background:{C['surface']};border:1px dashed {C['border']};border-radius:10px;padding:32px;text-align:center">
<p style="color:{C['text_muted']}">「アタックリストを生成する」ボタンを押してください</p>
</div>
""", unsafe_allow_html=True)
    st.stop()

# ── フィルタリング ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"<h4 style='color:{C['accent']}'>🔍 フィルター</h4>", unsafe_allow_html=True)
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filter_industry = st.multiselect("業界", options=list({c["industry"] for c in attack_list}))
with col_f2:
    min_score = st.slider("最低スコア", 0, 100, 0)
with col_f3:
    filter_conf = st.multiselect("データ確度", ["high","medium","low"], default=["high","medium","low"])

filtered = [
    c for c in attack_list
    if (not filter_industry or c["industry"] in filter_industry)
    and c.get("total_score", 0) >= min_score
    and c.get("data_confidence","medium") in filter_conf
]

st.caption(f"表示: {len(filtered)} / {len(attack_list)} 社")

# ── TOP3 カード ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"<h4 style='color:{C['accent']}'>🏆 TOP 3 注目企業</h4>", unsafe_allow_html=True)
top3 = filtered[:3]
medals = ["🥇","🥈","🥉"]
conf_color = {"high": C['success'], "medium": C['warning'], "low": C['danger']}
cols = st.columns(len(top3))
for col, company, medal in zip(cols, top3, medals):
    score = company.get("total_score", 0)
    conf = company.get("data_confidence","medium")
    cc = conf_color.get(conf, C['text_muted'])
    bar_w = int(score)
    with col:
        st.markdown(f"""
<div style="background:linear-gradient(160deg,{C['surface']},{C['surface2']});border:1px solid {C['border']};border-top:3px solid {C['accent']};border-radius:12px;padding:18px 20px;height:100%">
  <div style="font-size:1.5rem">{medal}</div>
  <div style="color:{C['white']};font-size:1.05rem;font-weight:700;margin:6px 0 2px">{company.get('company_name','')}</div>
  <div style="color:{C['text_muted']};font-size:0.82rem;margin-bottom:10px">{company.get('industry','')}</div>
  <div style="color:{C['text_muted']};font-size:0.78rem">売上規模</div>
  <div style="color:{C['white']};font-size:0.9rem;margin-bottom:8px">{company.get('revenue_scale','—')}</div>
  <div style="background:{C['bg']};border-radius:4px;height:6px;overflow:hidden;margin-bottom:4px">
    <div style="width:{bar_w}%;height:100%;background:linear-gradient(90deg,{C['accent']},{C['accent2']});border-radius:4px"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-bottom:10px">
    <span style="color:{C['text_muted']};font-size:0.78rem">スコア</span>
    <span style="color:{C['white']};font-weight:700">{score}/100</span>
  </div>
  <div style="color:{C['text_muted']};font-size:0.78rem">自社との相性</div>
  <div style="color:{C['text']};font-size:0.85rem;margin-top:4px">{company.get('compatibility_comment','—')}</div>
  <div style="margin-top:10px;color:{cc};font-size:0.75rem">● データ確度: {conf}</div>
</div>
""", unsafe_allow_html=True)

# ── メインテーブル ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"<h4 style='color:{C['accent']}'>📊 アタックリスト一覧</h4>", unsafe_allow_html=True)

conf_label = {"high":"🟢 高","medium":"🟡 中","low":"🔴 低"}
df_display = pd.DataFrame([
    {
        "順位": c["rank"],
        "企業名": c.get("company_name",""),
        "業界": c.get("industry",""),
        "売上規模": c.get("revenue_scale",""),
        "ICP適合": c.get("icp_fit_score",""),
        "フィット": c.get("solution_fit_score",""),
        "競合余地": c.get("competitor_saturation_score",""),
        "総合スコア": c.get("total_score",""),
        "自社との相性": c.get("compatibility_comment",""),
        "アプローチ": c.get("approach_hint",""),
        "確度": conf_label.get(c.get("data_confidence","medium"),"—"),
    }
    for c in filtered
])
st.dataframe(
    df_display,
    hide_index=True,
    use_container_width=True,
    height=min(600, len(filtered)*38+50),
    column_config={
        "総合スコア": st.column_config.ProgressColumn("総合スコア", min_value=0, max_value=100, format="%d"),
        "ICP適合": st.column_config.NumberColumn(format="%d"),
        "フィット": st.column_config.NumberColumn(format="%d"),
        "競合余地": st.column_config.NumberColumn(format="%d"),
    },
)

# ── ダウンロード ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"<h4 style='color:{C['accent']}'>💾 ダウンロード</h4>", unsafe_allow_html=True)

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

col_excel, col_csv = st.columns(2)
with col_excel:
    if st.button("📥 Excel を生成する", use_container_width=True):
        with st.spinner("Excel生成中..."):
            try:
                path = write_attack_list_excel(filtered, st.session_state.industry_analysis, meta)
                with open(path, "rb") as f:
                    st.download_button(
                        "⬇️ Excel ファイルを保存",
                        data=f.read(),
                        file_name=os.path.basename(path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
            except Exception as e:
                st.error(f"Excel生成エラー: {e}")

with col_csv:
    if st.button("📥 CSV を生成する", use_container_width=True):
        with st.spinner("CSV生成中..."):
            try:
                path = write_csv(filtered)
                with open(path, "rb") as f:
                    st.download_button(
                        "⬇️ CSV ファイルを保存",
                        data=f.read(),
                        file_name=os.path.basename(path),
                        mime="text/csv",
                        use_container_width=True,
                    )
            except Exception as e:
                st.error(f"CSV生成エラー: {e}")

st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {C['border']};border-radius:8px;padding:12px 16px;margin-top:16px">
<p style="color:{C['text_muted']};font-size:0.82rem;margin:0">
⚠️ 本リストはAIが公開情報を基に生成した <b>推定情報</b> です。
売上規模・スコアは推定値であり、最終判断は必ず人間が行ってください。
個人情報は含まれておらず、法人単位の情報のみを扱っています。
</p>
</div>
""", unsafe_allow_html=True)
