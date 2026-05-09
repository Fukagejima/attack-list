"""
ポテンシャル営業先アタックリスト作成エージェント
シングルページ ステップルーター
"""
import streamlit as st

st.set_page_config(
    page_title="営業アタックリスト作成エージェント",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.styles import inject_global_css, render_step_nav, C

inject_global_css()

# ── セッション初期化 ──────────────────────────────────────────────────────────
def _init():
    defaults = {
        "page":               "login",
        "current_step":       1,
        "authenticated":      False,
        "current_user":       {},
        "user_input":         {},
        "chat_messages":      [],
        "chat_done":          False,
        "industry_analysis":  [],
        "selected_industries":[],
        "attack_list":        [],
        "db_session_id":      None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ── 認証ガード ────────────────────────────────────────────────────────────────
if not st.session_state.authenticated and st.session_state.page != "login":
    st.session_state.page = "login"

# ── ヘッダー（ロゴ＋ユーザー表示＋ログアウト） ────────────────────────────────
header_col, user_col = st.columns([5, 1])
with header_col:
    st.markdown(f"""
<div style="padding:10px 0 4px;margin-bottom:4px">
<div style="color:{C['white']};font-size:1.15rem;font-weight:700;line-height:1.3">
  ポテンシャル営業先 アタックリスト作成エージェント
</div>
<div style="color:{C['text_muted']};font-size:0.8rem;margin-top:2px">
  AIが全業界を分析し、有望マーケットと具体企業リストを生成します
</div>
</div>
""", unsafe_allow_html=True)

with user_col:
    user = st.session_state.get("current_user", {})
    if user:
        display = user.get("display_name") or user.get("username", "")
        role    = user.get("role", "")
        st.markdown(f"""
<div style="text-align:right;padding-top:8px">
<div style="color:{C['white']};font-size:0.85rem;font-weight:600">{display}</div>
<div style="color:{C['text_muted']};font-size:0.75rem">{role}</div>
</div>""", unsafe_allow_html=True)
        col_hist, col_logout = st.columns(2)
        with col_hist:
            if st.button("履歴", use_container_width=True, key="btn_history"):
                st.session_state.page = "admin"
                st.rerun()
        with col_logout:
            if st.button("ログアウト", use_container_width=True, key="btn_logout"):
                for k in ["authenticated","current_user","user_input","chat_messages",
                          "chat_done","industry_analysis","selected_industries",
                          "attack_list","db_session_id","chat_partial"]:
                    st.session_state.pop(k, None)
                st.session_state.page = "login"
                st.session_state.current_step = 1
                st.rerun()

# ── ステップナビゲーション ────────────────────────────────────────────────────
page = st.session_state.page
step_map = {"login": 1, "input": 2, "heatmap": 3, "attack_list": 4}
render_step_nav(step_map.get(page, 1))

st.markdown("<hr style='margin:0 0 20px'>", unsafe_allow_html=True)

# ── ページルーティング ─────────────────────────────────────────────────────────
if page == "login":
    from views.login import render
    render()

elif page == "input":
    st.markdown(f"<h2 style='color:{C['white']};margin:0 0 4px'>情報入力</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{C['text_muted']};margin-bottom:16px'>AIとの会話で自社・サービス情報を入力してください</p>", unsafe_allow_html=True)
    from views.chat_input import render
    render()

elif page == "heatmap":
    st.markdown(f"<h2 style='color:{C['white']};margin:0 0 4px'>業界3C分析</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{C['text_muted']};margin-bottom:16px'>全30業界を Customer / Competitor / Company の3C視点で自動評価します</p>", unsafe_allow_html=True)
    from views.heatmap import render
    render()

elif page == "attack_list":
    st.markdown(f"<h2 style='color:{C['white']};margin:0 0 4px'>アタックリスト</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{C['text_muted']};margin-bottom:16px'>有望業界の具体企業リストをスコア付きで出力します</p>", unsafe_allow_html=True)
    from views.attack_list import render
    render()

elif page == "admin":
    st.markdown(f"<h2 style='color:{C['white']};margin:0 0 4px'>管理・履歴</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{C['text_muted']};margin-bottom:16px'>過去の分析履歴の呼び出し・ユーザー管理（管理者のみ）</p>", unsafe_allow_html=True)
    from views.admin import render
    render()
