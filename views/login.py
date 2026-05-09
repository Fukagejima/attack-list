"""ログイン画面（マルチユーザー対応）"""
import streamlit as st
from src.db.auth import login
from src.db.client import is_db_enabled
from utils.styles import C


def render():
    st.markdown(f"""
<div style="max-width:440px;margin:40px auto 0">
<div style="
  background:linear-gradient(135deg,{C['surface']},{C['surface2']});
  border:1px solid {C['border']};
  border-top:3px solid {C['accent']};
  border-radius:16px;
  padding:36px 40px;
">
<h2 style="color:{C['white']};margin:0 0 6px;font-size:1.4rem">ログイン</h2>
<p style="color:{C['text_muted']};font-size:0.88rem;margin-bottom:24px">
  アカウント情報を入力してください
</p>
""", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("ユーザー名", placeholder="username")
        password = st.text_input("パスワード", type="password", placeholder="••••••••")
        submitted = st.form_submit_button(
            "ログイン",
            use_container_width=True,
            type="primary",
        )

    st.markdown("</div></div>", unsafe_allow_html=True)

    if submitted:
        if not username or not password:
            st.error("ユーザー名とパスワードを入力してください。")
            return
        user = login(username, password)
        if user:
            st.session_state.authenticated = True
            st.session_state.current_user  = user
            st.session_state.page          = "input"
            st.session_state.current_step  = 2
            st.rerun()
        else:
            st.error("ユーザー名またはパスワードが正しくありません。")

    if not is_db_enabled():
        with st.expander("ℹ️ DB未接続時のデフォルト認証情報"):
            import os
            st.code(
                f"ユーザー名: {os.getenv('APP_USERNAME','admin')}\n"
                f"パスワード: {os.getenv('APP_PASSWORD','password123')}"
            )
            st.caption(".env ファイルで変更できます。")
