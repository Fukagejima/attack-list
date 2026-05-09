import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import APP_USERNAME, APP_PASSWORD
from utils.styles import inject_global_css, page_header, C

st.set_page_config(page_title="ログイン", page_icon="🔐", layout="centered")
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

page_header("🔐", "ログイン", "アカウント情報を入力してください")

if st.session_state.authenticated:
    st.markdown(f"""
<div style="background:rgba(62,207,142,0.12);border:1px solid #3ecf8e;border-radius:10px;padding:18px 22px;">
<span style="color:#3ecf8e;font-size:1.1rem;font-weight:600">✅ ログイン済みです</span><br>
<span style="color:#7a90b8;font-size:0.9rem">サイドバーから <b style="color:#4f8ef7">② 情報入力</b> に進んでください。</span>
</div>
""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("ログアウト", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_step = 1
        st.rerun()
else:
    # ログインカード
    st.markdown(f"""
<div style="
    background:linear-gradient(135deg,{C['surface']},{C['surface2']});
    border:1px solid {C['border']};
    border-radius:14px;
    padding:32px 36px;
    max-width:440px;
    margin:0 auto;
">
""", unsafe_allow_html=True)

    with st.form("login_form"):
        st.markdown(f"<p style='color:{C['text_muted']};margin-bottom:20px'>認証情報を入力してください</p>", unsafe_allow_html=True)
        username = st.text_input("👤 ユーザー名", placeholder="admin")
        password = st.text_input("🔑 パスワード", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("ログイン →", use_container_width=True, type="primary")

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if username == APP_USERNAME and password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.current_step = 2
            st.balloons()
            st.rerun()
        else:
            st.error("❌ ユーザー名またはパスワードが正しくありません。")

    with st.expander("ℹ️ デフォルト認証情報（開発用）"):
        st.code(f"ユーザー名: {APP_USERNAME}\nパスワード: {APP_PASSWORD}")
        st.caption(".env ファイルで変更できます。")
