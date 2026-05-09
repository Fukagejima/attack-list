import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.industries import COMPANY_SIZE_LIST
from utils.styles import inject_global_css, page_header, C

st.set_page_config(page_title="情報入力", page_icon="📝", layout="wide")
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
    st.warning("⚠️ ログインが必要です。サイドバーから **① ログイン** へ。")
    st.stop()

page_header("📝", "自社・サービス情報の入力", "入力情報をもとにAIが全業界を網羅的に自動評価します。業界選択は不要です。")

prev = st.session_state.get("user_input", {})

# ── 入力フォーム ───────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown(f"<h4 style='color:{C['accent']};margin-bottom:12px'>🏢 自社情報</h4>", unsafe_allow_html=True)
    company_name = st.text_input(
        "会社名 *",
        value=prev.get("company_name", ""),
        placeholder="例：株式会社ナナホシ",
    )
    existing_industry = st.text_input(
        "現在の主要取引先業界 *",
        value=prev.get("existing_industry", ""),
        placeholder="例：美容・コスメ、EC・D2C",
        help="現在売れている業界（自由記述）",
    )
    company_size_own = st.selectbox(
        "自社の規模",
        options=COMPANY_SIZE_LIST,
        index=COMPANY_SIZE_LIST.index(prev["company_size_own"])
        if prev.get("company_size_own") in COMPANY_SIZE_LIST else 0,
    )

with col_right:
    st.markdown(f"<h4 style='color:{C['accent']};margin-bottom:12px'>🛠️ サービス・強み</h4>", unsafe_allow_html=True)
    service_name = st.text_input(
        "サービス名 / 製品名 *",
        value=prev.get("service_name", ""),
        placeholder="例：インフルエンサーマーケティング支援「NANAHOSHI」",
    )
    strengths = st.text_area(
        "強み・差別化ポイント *",
        value=prev.get("strengths", ""),
        height=155,
        placeholder=(
            "例：\n"
            "・フォロワー1万人以上のインフルエンサー3,000名と契約済み\n"
            "・美容・食品領域での成約実績200社超\n"
            "・投稿後72時間以内の効果レポート提供\n"
            "・初回トライアルプラン（5万円〜）あり"
        ),
    )

st.markdown("---")

# ── 出力設定 ───────────────────────────────────────────────────────────────────
st.markdown(f"<h4 style='color:{C['accent']};margin-bottom:12px'>⚙️ 出力設定</h4>", unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a:
    target_company_size = st.multiselect(
        "ターゲット企業規模",
        options=COMPANY_SIZE_LIST,
        default=prev.get("target_company_size", [
            "大企業（売上1,000億円以上）",
            "中堅企業（売上100億〜1,000億円）",
            "中小企業（売上10億〜100億円）",
        ]),
    )
with col_b:
    companies_per_industry = st.slider(
        "業界あたりの出力企業数",
        min_value=3, max_value=10, value=prev.get("companies_per_industry", 5),
    )

st.markdown(f"""
<div style="background:rgba(79,142,247,0.10);border:1px solid {C['accent']};border-radius:8px;padding:12px 16px;margin:12px 0">
💡 業界は選択不要です。AIが全業界（約30業界）を自動的に評価し、◎○△×でスコアリングします。
</div>
""", unsafe_allow_html=True)

st.markdown("---")

all_filled = all([
    company_name.strip(),
    service_name.strip(),
    strengths.strip(),
    existing_industry.strip(),
])

if not all_filled:
    st.markdown(f"<p style='color:{C['text_muted']}'>📌 * の項目をすべて入力してください。</p>", unsafe_allow_html=True)

if st.button("💾 保存して業界分析へ →", disabled=not all_filled, use_container_width=True, type="primary"):
    st.session_state.user_input = {
        "company_name": company_name.strip(),
        "service_name": service_name.strip(),
        "strengths": strengths.strip(),
        "existing_industry": existing_industry.strip(),
        "company_size_own": company_size_own,
        "target_company_size": target_company_size,
        "companies_per_industry": companies_per_industry,
    }
    st.session_state.current_step = max(st.session_state.current_step, 3)
    st.session_state.industry_analysis = []
    st.session_state.attack_list = []
    st.session_state.selected_industries = []
    st.success("✅ 保存しました。サイドバーから **③ 業界ヒートマップ** に進んでください。")

if st.session_state.get("user_input"):
    with st.expander("📄 保存済み入力内容を確認"):
        st.json(st.session_state.user_input)
