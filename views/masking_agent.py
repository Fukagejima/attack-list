"""
SharePoint マスキングエージェント - UIビュー（ガワ）
白・オレンジ基調デザイン
"""
import streamlit as st
from config.settings import APP_USERNAME, APP_PASSWORD


# ── カラーパレット（白・オレンジ基調） ────────────────────────────────────────
MC = {
    "bg":           "#FFFFFF",
    "bg_sub":       "#FFF8F3",
    "surface":      "#FFFFFF",
    "surface2":     "#FFF3E8",
    "border":       "#FFD0A8",
    "accent":       "#FF6B00",
    "accent2":      "#FF9A4A",
    "accent_light": "#FFF3E8",
    "accent_dark":  "#CC5500",
    "text":         "#1A1A1A",
    "text_muted":   "#7A6A60",
    "success":      "#2D9B5A",
    "warning":      "#E8A800",
    "danger":       "#D93025",
    "white":        "#FFFFFF",
    "header_bg":    "#FF6B00",
}


def inject_masking_css():
    st.markdown(f"""
<style>
/* ── ページ全体をリセット ────────────────────────── */
html, body, .stApp {{
    background-color: {MC['bg_sub']} !important;
    color: {MC['text']} !important;
    font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', 'Segoe UI', sans-serif;
}}
section[data-testid="stMain"] > div {{
    background-color: {MC['bg_sub']} !important;
}}

/* ── 上部ヘッダーバー ────────────────────────────── */
.mask-header {{
    background: linear-gradient(135deg, {MC['accent']} 0%, {MC['accent2']} 100%);
    border-radius: 14px;
    padding: 28px 32px 22px;
    margin-bottom: 28px;
    box-shadow: 0 4px 20px rgba(255,107,0,0.25);
    display: flex;
    align-items: center;
    gap: 18px;
}}
.mask-header-icon {{
    font-size: 2.8rem;
    line-height: 1;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}}
.mask-header-title {{
    color: #fff !important;
    font-size: 1.65rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.2;
    letter-spacing: 0.02em;
}}
.mask-header-sub {{
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.9rem;
    margin-top: 4px;
}}

/* ── セクションカード ────────────────────────────── */
.mask-card {{
    background: {MC['surface']};
    border: 1.5px solid {MC['border']};
    border-radius: 12px;
    padding: 22px 26px;
    margin-bottom: 18px;
    box-shadow: 0 2px 10px rgba(255,107,0,0.06);
}}
.mask-card-title {{
    color: {MC['accent']} !important;
    font-size: 1.0rem;
    font-weight: 700;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.mask-card-title::before {{
    content: '';
    display: inline-block;
    width: 4px;
    height: 18px;
    background: {MC['accent']};
    border-radius: 2px;
    flex-shrink: 0;
}}

/* ── 入力フィールド上書き ────────────────────────── */
[data-testid="stTextInput"] input {{
    background-color: {MC['bg_sub']} !important;
    color: {MC['text']} !important;
    border: 1.5px solid {MC['border']} !important;
    border-radius: 8px !important;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: {MC['accent']} !important;
    box-shadow: 0 0 0 3px rgba(255,107,0,0.12) !important;
}}
[data-testid="stTextInput"] label, label[data-testid="stWidgetLabel"] * {{
    color: {MC['text']} !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}}

/* ── チェックボックス ────────────────────────────── */
[data-testid="stCheckbox"] label {{
    color: {MC['text']} !important;
    font-size: 0.92rem !important;
}}
[data-testid="stCheckbox"] input:checked + div {{
    background-color: {MC['accent']} !important;
    border-color: {MC['accent']} !important;
}}

/* ── ボタン ──────────────────────────────────────── */
[data-testid="stButton"] button {{
    background: {MC['surface2']} !important;
    color: {MC['accent']} !important;
    border: 1.5px solid {MC['border']} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}}
[data-testid="stButton"] button:hover {{
    background: {MC['accent']} !important;
    color: {MC['white']} !important;
    border-color: {MC['accent']} !important;
    box-shadow: 0 3px 12px rgba(255,107,0,0.3) !important;
    transform: translateY(-1px) !important;
}}
button[data-testid="baseButton-primary"],
[data-testid="stButton"] button[kind="primary"] {{
    background: linear-gradient(135deg, {MC['accent']}, {MC['accent2']}) !important;
    color: #fff !important;
    border: none !important;
    font-size: 1.0rem !important;
    font-weight: 700 !important;
    padding: 10px 32px !important;
    box-shadow: 0 4px 16px rgba(255,107,0,0.35) !important;
}}
button[data-testid="baseButton-primary"]:hover,
[data-testid="stButton"] button[kind="primary"]:hover {{
    box-shadow: 0 6px 24px rgba(255,107,0,0.5) !important;
    transform: translateY(-2px) !important;
    background: linear-gradient(135deg, {MC['accent_dark']}, {MC['accent']}) !important;
}}

/* ── プログレスバー ──────────────────────────────── */
[data-testid="stProgress"] > div > div {{
    background: linear-gradient(90deg, {MC['accent']}, {MC['accent2']}) !important;
    border-radius: 4px !important;
}}
[data-testid="stProgress"] > div {{
    background-color: {MC['border']} !important;
    border-radius: 4px !important;
}}

/* ── アラート ────────────────────────────────────── */
[data-testid="stAlert"] {{
    border-radius: 10px !important;
}}

/* ── セパレータ ──────────────────────────────────── */
hr {{
    border-color: {MC['border']} !important;
}}

/* ── ファイルタイプバッジ ─────────────────────────── */
.file-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    margin-right: 8px;
    margin-bottom: 6px;
    border: 1.5px solid;
}}
.file-badge-word  {{ background:#E8F0FE; border-color:#4285F4; color:#1557B0; }}
.file-badge-excel {{ background:#E6F4EA; border-color:#34A853; color:#137333; }}
.file-badge-pdf   {{ background:#FCE8E6; border-color:#EA4335; color:#C5221F; }}

/* ── マスキングターゲットバッジ ─────────────────── */
.mask-target-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 16px;
    background: {MC['accent_light']};
    border: 1.5px solid {MC['accent']};
    border-radius: 20px;
    font-size: 0.84rem;
    font-weight: 600;
    color: {MC['accent_dark']};
    margin-right: 8px;
    margin-bottom: 6px;
}}

/* ── ステータスログエリア ────────────────────────── */
.status-log {{
    background: #1A1A1A;
    border-radius: 10px;
    padding: 16px 20px;
    font-family: 'Courier New', monospace;
    font-size: 0.83rem;
    max-height: 220px;
    overflow-y: auto;
    border: 1.5px solid {MC['border']};
}}
.log-info    {{ color: #7ECFFF; }}
.log-success {{ color: #5BDB8E; }}
.log-warn    {{ color: #FFB84A; }}
.log-error   {{ color: #FF6B6B; }}

/* ── ログインフォーム専用 ────────────────────────── */
.mask-login-wrap {{
    max-width: 440px;
    margin: 0 auto;
}}
/* フォーム内ラベル */
[data-testid="stForm"] label,
[data-testid="stForm"] [data-testid="stWidgetLabel"] * {{
    color: {MC['text']} !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}}
/* フォーム内ボタン */
[data-testid="stForm"] button[data-testid="baseButton-primary"] {{
    background: linear-gradient(135deg, {MC['accent']}, {MC['accent2']}) !important;
    color: #fff !important;
    border: none !important;
    font-size: 1.0rem !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(255,107,0,0.35) !important;
    margin-top: 8px;
}}
[data-testid="stForm"] button[data-testid="baseButton-primary"]:hover {{
    box-shadow: 0 6px 24px rgba(255,107,0,0.5) !important;
    transform: translateY(-2px) !important;
}}

/* ── スクロールバー ──────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {MC['bg_sub']}; }}
::-webkit-scrollbar-thumb {{
    background: {MC['border']};
    border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{ background: {MC['accent']}; }}
</style>
""", unsafe_allow_html=True)


def render_header():
    col_main, col_logout = st.columns([9, 1])
    with col_main:
        st.markdown("""
<div class="mask-header">
  <div class="mask-header-icon">🛡️</div>
  <div>
    <div class="mask-header-title">SharePoint マスキングエージェント</div>
    <div class="mask-header-sub">機密情報を自動検出・マスキングし、安全なファイルを別の場所へ保存します</div>
  </div>
</div>
""", unsafe_allow_html=True)
    with col_logout:
        st.markdown("<div style='padding-top:8px'>", unsafe_allow_html=True)
        if st.button("🚪 ログアウト", key="mask_logout_btn"):
            st.session_state.mask_authenticated = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_file_type_badges():
    st.markdown("""
<div style="margin-bottom:4px">
  <span class="file-badge file-badge-word">📄 Word</span>
  <span class="file-badge file-badge-excel">📊 Excel</span>
  <span class="file-badge file-badge-pdf">📕 PDF</span>
</div>
<div style="margin-bottom:4px">
  <span class="mask-target-badge">🔗 URL</span>
  <span class="mask-target-badge">🖥️ IPアドレス</span>
  <span class="mask-target-badge">🔑 パスワード</span>
</div>
""", unsafe_allow_html=True)


def render_source_section():
    st.markdown("""
<div class="mask-card">
  <div class="mask-card-title">STEP 2 ── 取得元 SharePoint URL</div>
""", unsafe_allow_html=True)

    src_url = st.text_input(
        "SharePoint フォルダ URL（どの形式でも可）",
        placeholder="https://yourorg.sharepoint.com/sites/SiteName/Shared Documents/Folder",
        key="mask_src_url",
    )

    auth_mode = st.radio(
        "認証方式",
        options=["🔐 ブラウザでログイン（推奨）", "🔑 ユーザー名 / パスワード", "🏢 Azure AD アプリ"],
        horizontal=True,
        key="mask_auth_mode",
    )

    src_user = src_pass = src_token = src_client_id = src_client_secret = ""

    if auth_mode == "🔐 ブラウザでログイン（推奨）":
        src_token = _render_device_code_auth(src_url)

    elif auth_mode == "🔑 ユーザー名 / パスワード":
        col1, col2 = st.columns(2)
        with col1:
            src_user = st.text_input("ユーザー名（メール）", placeholder="user@org.onmicrosoft.com", key="mask_src_user")
        with col2:
            src_pass = st.text_input("パスワード", type="password", placeholder="••••••••", key="mask_src_pass")

    elif auth_mode == "🏢 Azure AD アプリ":
        st.markdown(f"""
<div style="background:#FFF8F0;border:1px solid #FFD0A8;border-radius:8px;
            padding:10px 14px;margin-bottom:10px;font-size:0.83rem;color:{MC['text_muted']}">
  <b style="color:{MC['accent']}">IT管理者に依頼して取得してください</b><br>
  Azure Portal → Azure AD → アプリの登録 → SharePoint「Sites.Read.All」権限を付与
</div>
""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            src_client_id = st.text_input("クライアント ID", placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", key="mask_src_cid")
        with col2:
            src_client_secret = st.text_input("クライアントシークレット", type="password", key="mask_src_csecret")

    st.markdown("</div>", unsafe_allow_html=True)
    return src_url, src_user, src_pass, src_token, src_client_id, src_client_secret


def _render_device_code_auth(src_url: str) -> str:
    """
    Device Code Flow による認証UI。
    取得済みトークンがあればそれを返す。なければ空文字。
    """
    import threading, time
    try:
        import msal
    except ImportError:
        st.error("msal ライブラリが必要です: pip install msal")
        return ""

    token = st.session_state.get("mask_device_token", "")

    # ── 認証済み ──────────────────────────────────────────────────────────────
    if token:
        st.markdown(f"""
<div style="background:#E8F5E9;border:1.5px solid #4CAF50;border-radius:8px;
            padding:10px 14px;font-size:0.88rem;color:#2E7D32;">
  ✅ <b>Microsoft 認証済み</b>（トークン有効）
</div>
""", unsafe_allow_html=True)
        if st.button("🔄 再認証する", key="mask_reauth"):
            st.session_state.mask_device_token  = ""
            st.session_state.mask_device_flow   = None
            st.session_state.mask_device_result = None
            st.rerun()
        return token

    # ── 認証コード発行 ────────────────────────────────────────────────────────
    flow   = st.session_state.get("mask_device_flow")
    result = st.session_state.get("mask_device_result")

    if not flow:
        # サイトURLからテナントを推定
        import re as _re
        m = _re.match(r'https?://([^.]+)\.sharepoint\.com', src_url or "", _re.I)
        tenant = f"{m.group(1)}.onmicrosoft.com" if m else "common"

        st.markdown(f"""
<div style="background:#FFF8F0;border:1px solid #FFD0A8;border-radius:8px;
            padding:10px 14px;margin-bottom:10px;font-size:0.85rem;color:{MC['text_muted']}">
  ボタンを押すと <b>8桁のコード</b> が表示されます。<br>
  表示されたURLを開いてコードを入力するだけで認証完了します。<br>
  MFA・条件付きアクセスにも対応しています。
</div>
""", unsafe_allow_html=True)

        col_btn, _ = st.columns([2, 3])
        with col_btn:
            if st.button("🔐 Microsoft ログインを開始", type="primary", key="mask_start_device"):
                if not src_url:
                    st.error("先に SharePoint URL を入力してください。")
                else:
                    try:
                        # SPO root URL を src_url から取得
                        spo_match = _re.match(r'(https?://[^/]+)', src_url or "")
                        spo_root  = spo_match.group(1) if spo_match else f"https://{tenant}"

                        # 複数の既知クライアントIDを順に試す
                        CLIENT_IDS = [
                            "04b07795-8542-4c45-a7b9-6e6d47d0cbad",  # Azure CLI
                            "1950a258-227b-4e31-a9cf-717495945fc2",  # Azure PowerShell
                            "d3590ed6-52b3-4102-aeff-aad2292ab01c",  # Microsoft Office
                        ]
                        app = None
                        new_flow = None
                        last_err = ""
                        for cid in CLIENT_IDS:
                            try:
                                _app = msal.PublicClientApplication(
                                    client_id=cid,
                                    authority=f"https://login.microsoftonline.com/{tenant}",
                                )
                                # SharePoint 直接スコープ（管理者同意不要）
                                _flow = _app.initiate_device_flow(
                                    scopes=[
                                        f"{spo_root}/AllSites.Read",
                                        f"{spo_root}/AllSites.Write",
                                    ]
                                )
                                if "user_code" in _flow:
                                    app, new_flow = _app, _flow
                                    break
                                last_err = _flow.get("error_description", "")
                            except Exception as e:
                                last_err = str(e)
                        if not new_flow:
                            raise Exception(f"全クライアントIDで認証開始に失敗: {last_err}")
                        container = {"done": False, "token": None, "error": None}

                        def _poll(a, f, c):
                            r = a.acquire_token_by_device_flow(f)
                            c["token"] = r.get("access_token")
                            c["error"] = r.get("error_description")
                            c["done"]  = True

                        t = threading.Thread(target=_poll, args=(app, new_flow, container), daemon=True)
                        t.start()
                        st.session_state.mask_device_flow   = new_flow
                        st.session_state.mask_device_result = container
                        st.rerun()
                    except Exception as e:
                        st.error(f"認証開始エラー: {e}")
        return ""

    # ── コード表示・ポーリング ─────────────────────────────────────────────────
    user_code = flow.get("user_code", "")
    verify_url = flow.get("verification_uri", "https://microsoft.com/devicelogin")

    st.markdown(f"""
<div style="background:#FFF3E8;border:2px solid {MC['accent']};border-radius:12px;
            padding:18px 22px;text-align:center;">
  <div style="color:{MC['text_muted']};font-size:0.85rem;margin-bottom:8px">
    ① 下のURLをブラウザで開く &nbsp;→&nbsp; ② コードを入力 &nbsp;→&nbsp; ③ Microsoft アカウントでログイン
  </div>
  <div style="margin:10px 0">
    <a href="{verify_url}" target="_blank"
       style="color:{MC['accent']};font-weight:700;font-size:1.05rem;">
      🌐 {verify_url}
    </a>
  </div>
  <div style="
    display:inline-block;
    background:{MC['accent']};color:#fff;
    font-size:2rem;font-weight:800;letter-spacing:0.25em;
    padding:10px 28px;border-radius:10px;
    font-family:monospace;
  ">{user_code}</div>
  <div style="color:{MC['text_muted']};font-size:0.8rem;margin-top:10px">
    このコードの有効期限: 約15分
  </div>
</div>
""", unsafe_allow_html=True)

    # 完了チェック
    if result and result.get("done"):
        if result.get("token"):
            st.session_state.mask_device_token  = result["token"]
            st.session_state.mask_device_flow   = None
            st.session_state.mask_device_result = None
            st.rerun()
        else:
            st.error(f"認証失敗: {result.get('error', '不明なエラー')}")
            st.session_state.mask_device_flow   = None
            st.session_state.mask_device_result = None
    else:
        # ポーリング: 3秒ごとに確認
        time.sleep(3)
        st.rerun()

    return ""


def render_masking_section():
    st.markdown("""
<div class="mask-card">
  <div class="mask-card-title">STEP 2 ── マスキング設定</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        mask_url = st.checkbox("🔗 URL / ハイパーリンク", value=True, key="mask_opt_url")
    with col2:
        mask_ip = st.checkbox("🖥️ IP アドレス", value=True, key="mask_opt_ip")
    with col3:
        mask_pw = st.checkbox("🔑 パスワード文字列", value=True, key="mask_opt_pw")

    mask_char = st.selectbox(
        "マスク文字",
        options=["★★★★★", "●●●●●", "＊＊＊＊＊", "[MASKED]", "[REDACTED]"],
        index=3,
        key="mask_char",
    )

    st.markdown("</div>", unsafe_allow_html=True)
    return mask_url, mask_ip, mask_pw, mask_char


def render_destination_section():
    st.markdown("""
<div class="mask-card">
  <div class="mask-card-title">STEP 3 ── 保存先 URL（省略可 → ダウンロードのみ）</div>
""", unsafe_allow_html=True)

    dst_url = st.text_input(
        "保存先 SharePoint フォルダ URL（空欄の場合はダウンロードのみ）",
        placeholder="https://yourorg.sharepoint.com/sites/SiteName/Masked Documents/...",
        key="mask_dst_url",
    )

    st.markdown("</div>", unsafe_allow_html=True)
    return dst_url


def render_execute_button():
    st.markdown("""
<div class="mask-card" style="text-align:center; padding:24px 26px;">
  <div class="mask-card-title" style="justify-content:center;">STEP 4 ── 実行</div>
""", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([2, 3, 2])
    with col_c:
        run = st.button(
            "🛡️　マスキングを開始する",
            type="primary",
            use_container_width=True,
            key="mask_run_btn",
        )

    st.markdown("</div>", unsafe_allow_html=True)
    return run


def render_status_panel():
    """実行ステータス・ログパネル"""
    status = st.session_state.get("mask_status", "idle")
    logs   = st.session_state.get("mask_logs", [])

    if status == "idle" and not logs:
        return

    st.markdown("""
<div class="mask-card">
  <div class="mask-card-title">実行ログ</div>
""", unsafe_allow_html=True)

    # ── プログレスバー ──
    progress = st.session_state.get("mask_progress", 0)
    if status == "running":
        st.progress(progress / 100)

    # ── ログ ──
    if logs:
        log_html = ""
        for entry in logs[-30:]:
            level = entry.get("level", "info")
            msg   = entry.get("msg", "")
            cls   = {"info": "log-info", "success": "log-success",
                     "warn": "log-warn", "error": "log-error"}.get(level, "log-info")
            log_html += f'<div class="{cls}">{msg}</div>\n'
        st.markdown(f'<div class="status-log">{log_html}</div>', unsafe_allow_html=True)

    # ── 完了サマリ ──
    if status == "done":
        summary = st.session_state.get("mask_summary", {})
        total   = summary.get("total", 0)
        success = summary.get("success", 0)
        failed  = summary.get("failed", 0)
        masked  = summary.get("masked_count", 0)

        c1, c2, c3, c4 = st.columns(4)
        _metric_card(c1, "処理ファイル数", f"{total}",   MC["accent"])
        _metric_card(c2, "成功",           f"{success}", MC["success"])
        _metric_card(c3, "失敗",           f"{failed}",  MC["danger"] if failed else MC["text_muted"])
        _metric_card(c4, "マスク箇所数",   f"{masked}",  MC["accent2"])

    elif status == "error":
        st.error(st.session_state.get("mask_error_msg", "エラーが発生しました。"))

    st.markdown("</div>", unsafe_allow_html=True)


def _metric_card(col, label: str, value: str, color: str):
    with col:
        st.markdown(f"""
<div style="
    background:{MC['accent_light']};
    border:1.5px solid {MC['border']};
    border-top:3px solid {color};
    border-radius:10px;
    padding:12px 14px;
    text-align:center;
">
    <div style="color:{MC['text_muted']};font-size:0.76rem;margin-bottom:4px">{label}</div>
    <div style="color:{color};font-size:1.5rem;font-weight:800">{value}</div>
</div>
""", unsafe_allow_html=True)


def render_login():
    """ログイン画面（白・オレンジテーマ）"""
    st.markdown("""
<div style="text-align:center; margin-bottom:28px;">
  <div style="
      display:inline-flex; align-items:center; justify-content:center;
      width:64px; height:64px; border-radius:16px;
      background:linear-gradient(135deg,#FF6B00,#FF9A4A);
      box-shadow:0 4px 16px rgba(255,107,0,0.3);
      font-size:2rem; margin-bottom:12px;
  ">🛡️</div>
  <div style="color:#FF6B00;font-size:1.3rem;font-weight:800;">
      SharePoint マスキングエージェント
  </div>
  <div style="color:#7A6A60;font-size:0.85rem;margin-top:4px;">
      機密情報を自動検出・マスキングするシステム
  </div>
</div>
""", unsafe_allow_html=True)

    with st.form("mask_login_form", clear_on_submit=False):
        username = st.text_input(
            "ユーザー名",
            placeholder="admin",
            key="mask_login_user",
        )
        password = st.text_input(
            "パスワード",
            type="password",
            placeholder="••••••••",
            key="mask_login_pass",
        )
        submitted = st.form_submit_button(
            "🔓　ログイン",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        if username == APP_USERNAME and password == APP_PASSWORD:
            st.session_state.mask_authenticated = True
            st.rerun()
        else:
            st.error("❌ ユーザー名またはパスワードが正しくありません。")

    with st.expander("ℹ️ デフォルト認証情報（開発用）"):
        st.code(f"ユーザー名: {APP_USERNAME}\nパスワード: {APP_PASSWORD}")
        st.caption(".env ファイルで変更できます。")


def _init_session():
    defaults = {
        "mask_authenticated":  False,
        "mask_status":         "idle",
        "mask_progress":       0,
        "mask_logs":           [],
        "mask_summary":        {},
        "mask_results":        [],
        "mask_error_msg":      "",
        "mask_device_token":   "",
        "mask_device_flow":    None,
        "mask_device_result":  None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render():
    """メインレンダー関数"""
    _init_session()
    inject_masking_css()

    if not st.session_state.mask_authenticated:
        render_login()
        return

    render_header()

    st.markdown("""
<p style="color:#7A6A60;font-size:0.9rem;margin:-10px 0 14px">
    対応ファイル形式と自動検出対象:
</p>
""", unsafe_allow_html=True)
    render_file_type_badges()
    st.markdown("<br>", unsafe_allow_html=True)

    # ── STEP 1: マスキング設定（共通） ──
    mask_url, mask_ip, mask_pw, _ = render_masking_section()
    opts = {"url": mask_url, "ip": mask_ip, "password": mask_pw}

    st.markdown("<br>", unsafe_allow_html=True)

    # ── タブ切り替え ──
    tab_upload, tab_sp = st.tabs(["📁　ファイルを直接アップロード", "🌐　SharePoint URL から取得"])

    with tab_upload:
        _render_upload_tab(opts)

    with tab_sp:
        _render_sharepoint_tab(opts)

    render_download_panel()


def _render_upload_tab(opts: dict):
    """直接アップロードタブ"""
    st.markdown(f"""
<div class="mask-card">
  <div class="mask-card-title">STEP 2 ── ファイルをアップロード</div>
  <p style="color:{MC['text_muted']};font-size:0.85rem;margin:0 0 12px">
    Word / Excel / PowerPoint ファイルを選択してください（複数可）
  </p>
""", unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "ファイルを選択",
        type=["docx", "xlsx", "pptx"],
        accept_multiple_files=True,
        key="mask_upload_files",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if not uploaded:
        return

    # ファイル一覧プレビュー
    st.markdown(f"""
<div style="background:{MC['accent_light']};border:1.5px solid {MC['border']};
            border-radius:10px;padding:14px 18px;margin-bottom:16px;">
  <div style="color:{MC['accent']};font-size:0.85rem;font-weight:700;margin-bottom:8px">
    選択済みファイル ({len(uploaded)} 件)
  </div>
""", unsafe_allow_html=True)
    for f in uploaded:
        ext  = f.name.rsplit('.', 1)[-1].upper()
        size = f"{f.size / 1024:.1f} KB"
        st.markdown(
            f'<div style="color:{MC["text"]};font-size:0.85rem;padding:2px 0">'
            f'📄 {f.name} <span style="color:{MC["text_muted"]}">({ext} · {size})</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([2, 3, 2])
    with col_c:
        run = st.button(
            "🛡️　マスキングを開始する",
            type="primary",
            use_container_width=True,
            key="mask_upload_run",
        )

    if run:
        if not (opts.get("url") or opts.get("ip") or opts.get("password")):
            st.error("マスキング対象を1つ以上選択してください。")
        else:
            _execute_direct_masking(uploaded, opts)


def _execute_direct_masking(uploaded_files, opts: dict):
    """アップロードされたファイルをメモリ上でマスク処理"""
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.masking.word_masker  import mask_word
    from src.masking.excel_masker import mask_excel
    from src.masking.ppt_masker   import mask_ppt
    from datetime import datetime

    PROCESSORS = {
        'docx': (mask_word,  '.docx'),
        'xlsx': (mask_excel, '.xlsx'),
        'pptx': (mask_ppt,   '.docx'),
    }

    results = []

    with st.status("🛡️ マスキング処理中...", expanded=True) as status_box:
        for uf in uploaded_files:
            ext = uf.name.rsplit('.', 1)[-1].lower()
            if ext not in PROCESSORS:
                continue

            ts = datetime.now().strftime('%H:%M:%S')
            st.write(f"[{ts}]  処理中: {uf.name}")

            try:
                processor, out_ext = PROCESSORS[ext]
                file_bytes = uf.read()
                masked_bytes, mask_count = processor(file_bytes, opts)

                stem     = uf.name.rsplit('.', 1)[0]
                out_name = f"{stem}_masked{out_ext}"

                ts = datetime.now().strftime('%H:%M:%S')
                st.write(f"[{ts}]  ✅ {out_name}  (マスク {mask_count} 件)")

                results.append({
                    "name":        uf.name,
                    "out_name":    out_name,
                    "status":      "success",
                    "mask_count":  mask_count,
                    "file_bytes":  masked_bytes,
                    "local_path":  "",
                })
            except Exception as e:
                ts = datetime.now().strftime('%H:%M:%S')
                st.write(f"[{ts}]  ❌ {uf.name}: {e}")
                results.append({
                    "name": uf.name, "out_name": "", "status": "error",
                    "mask_count": 0, "file_bytes": b"", "local_path": "",
                    "error": str(e),
                })

        success     = sum(1 for r in results if r["status"] == "success")
        total_masks = sum(r["mask_count"] for r in results)
        status_box.update(
            label=f"✅ 完了 — {success} 件成功 / マスク {total_masks} 箇所",
            state="complete",
            expanded=False,
        )

    st.session_state.mask_status  = "done"
    st.session_state.mask_results = results
    st.session_state.mask_summary = {
        "total":        len(results),
        "success":      success,
        "failed":       len(results) - success,
        "masked_count": total_masks,
    }
    st.rerun()


def _render_sharepoint_tab(opts: dict):
    """SharePoint URL タブ"""
    src_url, src_user, src_pass, src_token, src_cid, src_csecret = render_source_section()
    dst_url = render_destination_section()

    col_l, col_c, col_r = st.columns([2, 3, 2])
    with col_c:
        run = st.button(
            "🛡️　マスキングを開始する",
            type="primary",
            use_container_width=True,
            key="mask_sp_run",
        )

    if run:
        errors = []
        if not src_url:
            errors.append("取得元 SharePoint URL を入力してください。")
        if not (opts.get("url") or opts.get("ip") or opts.get("password")):
            errors.append("マスキング対象を1つ以上選択してください。")
        # 認証情報チェック
        auth_mode = st.session_state.get("mask_auth_mode", "")
        if "トークン" in auth_mode and not src_token:
            errors.append("アクセストークンを入力してください。")
        elif "Azure" in auth_mode and not (src_cid and src_csecret):
            errors.append("クライアント ID とシークレットを入力してください。")
        elif "パスワード" in auth_mode and not (src_user and src_pass):
            errors.append("ユーザー名とパスワードを入力してください。")

        if errors:
            for e in errors:
                st.error(e)
        else:
            _execute_masking(
                src_url, src_user, src_pass, src_token, src_cid, src_csecret,
                dst_url, opts,
            )

    render_status_panel()


def _execute_masking(src_url, src_user, src_pass, src_token, src_cid, src_csecret,
                     dst_url, opts):
    """マスキング処理を同期実行しセッション状態を更新する"""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.masking import agent as masking_agent

    logs: list[dict] = []
    results: list[dict] = []

    def _cb(level: str, msg: str):
        logs.append({"level": level, "msg": msg})

    st.session_state.mask_status  = "running"
    st.session_state.mask_logs    = logs
    st.session_state.mask_results = []

    # st.status で処理中ブロックを表示
    with st.status("🛡️ マスキング処理中...", expanded=True) as status_box:
        try:
            results = masking_agent.run(
                src_url=src_url,
                src_user=src_user,
                src_pass=src_pass,
                src_token=src_token,
                src_client_id=src_cid,
                src_client_secret=src_csecret,
                dst_url=dst_url,
                opts=opts,
                callback=lambda lv, msg: (
                    logs.append({"level": lv, "msg": msg}),
                    st.write(msg),
                ),
            )

            success = sum(1 for r in results if r["status"] == "success")
            failed  = sum(1 for r in results if r["status"] != "success")
            total_masks = sum(r["mask_count"] for r in results)

            st.session_state.mask_status  = "done"
            st.session_state.mask_logs    = logs
            st.session_state.mask_results = results
            st.session_state.mask_summary = {
                "total":        len(results),
                "success":      success,
                "failed":       failed,
                "masked_count": total_masks,
            }
            status_box.update(
                label=f"✅ 完了 — {success} 件成功 / マスク {total_masks} 箇所",
                state="complete",
                expanded=False,
            )

        except Exception as e:
            st.session_state.mask_status    = "error"
            st.session_state.mask_error_msg = str(e)
            st.session_state.mask_logs      = logs
            status_box.update(label=f"❌ エラー: {e}", state="error")

    st.rerun()


def render_download_panel():
    """処理完了後のダウンロードパネル（メモリ上バイト / ローカルファイル 両対応）"""
    results = st.session_state.get("mask_results", [])
    if not results:
        return

    success_results = [r for r in results if r["status"] == "success"]
    if not success_results:
        return

    # サマリ指標
    summary = st.session_state.get("mask_summary", {})
    if summary:
        c1, c2, c3, c4 = st.columns(4)
        _metric_card(c1, "処理ファイル数", str(summary.get("total", 0)),        MC["accent"])
        _metric_card(c2, "成功",           str(summary.get("success", 0)),      MC["success"])
        _metric_card(c3, "失敗",           str(summary.get("failed", 0)),       MC["danger"] if summary.get("failed") else MC["text_muted"])
        _metric_card(c4, "マスク箇所数",   str(summary.get("masked_count", 0)), MC["accent2"])
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
<div class="mask-card">
  <div class="mask-card-title">ダウンロード</div>
""", unsafe_allow_html=True)

    for r in success_results:
        out_name = r["out_name"]
        mask_cnt = r["mask_count"]

        # バイトの取得：メモリ優先 → ローカルファイルへフォールバック
        file_bytes = r.get("file_bytes") or b""
        if not file_bytes and r.get("local_path"):
            try:
                with open(r["local_path"], "rb") as f:
                    file_bytes = f.read()
            except FileNotFoundError:
                st.warning(f"ファイルが見つかりません: {r['local_path']}")
                continue

        if not file_bytes:
            continue

        mime = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            if out_name.endswith(".docx") else
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if out_name.endswith(".xlsx") else
            "application/octet-stream"
        )

        col_name, col_cnt, col_dl = st.columns([4, 2, 2])
        with col_name:
            st.markdown(
                f'<div style="padding:8px 0;color:{MC["text"]};font-size:0.9rem">'
                f'📄 {out_name}</div>',
                unsafe_allow_html=True,
            )
        with col_cnt:
            st.markdown(
                f'<div style="padding:8px 0;color:{MC["text_muted"]};font-size:0.85rem">'
                f'マスク {mask_cnt} 件</div>',
                unsafe_allow_html=True,
            )
        with col_dl:
            st.download_button(
                label="⬇ ダウンロード",
                data=file_bytes,
                file_name=out_name,
                mime=mime,
                key=f"dl_{out_name}",
            )

    st.markdown("</div>", unsafe_allow_html=True)
