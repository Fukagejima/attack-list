"""管理者画面 — ユーザー管理 & 分析履歴"""
import streamlit as st
from src.db.auth import create_user, list_users, toggle_user_active, delete_user
from src.db.history import load_my_sessions, load_session_detail
from src.db.client import is_db_enabled
from utils.styles import C


def render():
    user = st.session_state.get("current_user", {})
    is_admin = user.get("role") == "admin"

    tab_labels = ["履歴を呼び出す"]
    if is_admin:
        tab_labels.append("ユーザー管理")

    tabs = st.tabs(tab_labels)

    # ── 履歴タブ ──────────────────────────────────────────────────────────────
    with tabs[0]:
        _render_history(user)

    # ── ユーザー管理タブ（管理者のみ） ─────────────────────────────────────────
    if is_admin and len(tabs) > 1:
        with tabs[1]:
            _render_user_management()


def _render_history(user: dict):
    st.subheader("過去の分析履歴")
    if not is_db_enabled():
        st.info("データベース未接続のため、履歴機能は利用できません。")
        return

    sessions = load_my_sessions(user.get("id", ""))
    if not sessions:
        st.markdown(f"""
<div style="background:{C['surface']};border:1px dashed {C['border']};
border-radius:10px;padding:24px;text-align:center">
<p style="color:{C['text_muted']}">保存された分析履歴がありません</p>
</div>""", unsafe_allow_html=True)
        return

    for s in sessions:
        created = s.get("created_at", "")[:16].replace("T", " ")
        label = f"{created}　{s.get('company_name','')}／{s.get('service_name','')}"
        if st.button(label, key=f"hist_{s['id']}", use_container_width=True):
            with st.spinner("履歴を読み込み中..."):
                detail = load_session_detail(s["id"])
            if detail:
                st.session_state.user_input          = detail["user_input"]
                st.session_state.industry_analysis   = detail["industry_analysis"]
                st.session_state.attack_list         = detail["attack_list"]
                st.session_state.selected_industries = detail["selected_industries"]
                st.session_state.page                = "attack_list"
                st.session_state.current_step        = 4
                st.rerun()
            else:
                st.error("履歴の読み込みに失敗しました。")


def _render_user_management():
    st.subheader("ユーザー管理")
    if not is_db_enabled():
        st.warning("データベースが接続されていないためユーザー管理は利用できません。")
        return

    # ── ユーザー追加 ──────────────────────────────────────────────────────────
    with st.expander("新しいユーザーを追加", expanded=True):
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("ユーザー名", placeholder="tanaka")
                new_display  = st.text_input("表示名",     placeholder="田中 太郎")
            with col2:
                new_password = st.text_input("パスワード", type="password")
                new_role     = st.selectbox("権限", ["member", "admin"])
            if st.form_submit_button("追加する", type="primary", use_container_width=True):
                if not new_username or not new_password:
                    st.error("ユーザー名とパスワードは必須です。")
                else:
                    ok, msg = create_user(new_username, new_password, new_display, new_role)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # ── ユーザー一覧 ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"<h4 style='color:{C['white']}'>登録ユーザー一覧</h4>", unsafe_allow_html=True)
    users = list_users()
    current_uid = st.session_state.get("current_user", {}).get("id")

    for u in users:
        uid   = u["id"]
        uname = u["display_name"] or u["username"]
        role  = u["role"]
        active = u["is_active"]
        badge_color = C["success"] if active else C["danger"]
        badge_text  = "有効" if active else "無効"
        role_color  = C["accent"] if role == "admin" else C["text_muted"]

        col_info, col_toggle, col_del = st.columns([4, 1, 1])
        with col_info:
            st.markdown(
                f'<span style="color:{C["white"]};font-weight:600">{uname}</span>'
                f'<span style="color:{C["text_muted"]};font-size:0.82rem;margin-left:8px">@{u["username"]}</span>'
                f'<span style="color:{role_color};font-size:0.78rem;margin-left:8px">[{role}]</span>'
                f'<span style="color:{badge_color};font-size:0.78rem;margin-left:8px">● {badge_text}</span>',
                unsafe_allow_html=True,
            )
        with col_toggle:
            if uid != current_uid:  # 自分自身は無効にできない
                label = "無効化" if active else "有効化"
                if st.button(label, key=f"toggle_{uid}", use_container_width=True):
                    toggle_user_active(uid, not active)
                    st.rerun()
        with col_del:
            if uid != current_uid:
                if st.button("削除", key=f"del_{uid}", use_container_width=True):
                    delete_user(uid)
                    st.rerun()
