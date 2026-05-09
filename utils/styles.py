"""全ページ共通 CSS インジェクション"""
import streamlit as st

# カラーパレット
C = {
    "bg":           "#0b1628",   # メイン背景（深紺）
    "surface":      "#142040",   # カード・コンテナ背景
    "surface2":     "#1c2d57",   # 一段明るいサーフェス
    "border":       "#2a3f6f",   # ボーダー
    "accent":       "#4f8ef7",   # アクセントブルー
    "accent2":      "#f0c040",   # ゴールドアクセント
    "text":         "#e8eef8",   # メインテキスト
    "text_muted":   "#7a90b8",   # サブテキスト
    "success":      "#3ecf8e",   # 緑
    "warning":      "#f0c040",   # 黄
    "danger":       "#f06060",   # 赤
    "white":        "#ffffff",
}

def inject_global_css():
    st.markdown(f"""
<style>
/* ═══════════════════════════════════════════════════
   ベース・背景
═══════════════════════════════════════════════════ */
html, body, .stApp {{
    background-color: {C['bg']} !important;
    color: {C['text']} !important;
    font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', 'Segoe UI', sans-serif;
}}

/* メインコンテンツエリア */
section[data-testid="stMain"] > div {{
    background-color: {C['bg']} !important;
}}

/* サイドバー */
[data-testid="stSidebar"] {{
    background-color: {C['surface']} !important;
    border-right: 1px solid {C['border']} !important;
}}
[data-testid="stSidebar"] * {{
    color: {C['text']} !important;
}}
[data-testid="stSidebar"] a {{
    color: {C['accent']} !important;
}}
[data-testid="stSidebarNav"] span {{
    color: {C['text']} !important;
}}

/* ═══════════════════════════════════════════════════
   テキスト
═══════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 {{
    color: {C['white']} !important;
    font-weight: 700 !important;
}}
h1 {{ border-bottom: 2px solid {C['accent']} !important; padding-bottom: 10px; }}
p, span, label, div {{
    color: {C['text']} !important;
}}
.stCaption, [data-testid="stCaptionContainer"] * {{
    color: {C['text_muted']} !important;
}}

/* ═══════════════════════════════════════════════════
   ボタン
═══════════════════════════════════════════════════ */
[data-testid="stButton"] button {{
    background-color: {C['surface2']} !important;
    color: {C['text']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 6px !important;
    transition: all 0.2s !important;
}}
[data-testid="stButton"] button:hover {{
    background-color: {C['accent']} !important;
    border-color: {C['accent']} !important;
    color: {C['white']} !important;
}}
/* プライマリボタン */
[data-testid="stButton"] button[kind="primary"],
button[data-testid="baseButton-primary"] {{
    background: linear-gradient(135deg, {C['accent']}, #2563d4) !important;
    color: {C['white']} !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(79,142,247,0.35) !important;
}}
[data-testid="stButton"] button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {{
    box-shadow: 0 4px 20px rgba(79,142,247,0.55) !important;
    transform: translateY(-1px) !important;
}}

/* ═══════════════════════════════════════════════════
   入力フォーム
═══════════════════════════════════════════════════ */
[data-testid="stTextInput"] input,
[data-testid="stTextAreaRootElement"] textarea,
[data-testid="stSelectbox"] select,
[data-testid="stMultiSelect"] input {{
    background-color: {C['surface2']} !important;
    color: {C['text']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 6px !important;
}}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextAreaRootElement"] textarea:focus {{
    border-color: {C['accent']} !important;
    box-shadow: 0 0 0 2px rgba(79,142,247,0.25) !important;
}}
/* セレクトボックス・マルチセレクト */
[data-baseweb="select"] > div,
[data-baseweb="multi-select"] > div {{
    background-color: {C['surface2']} !important;
    border-color: {C['border']} !important;
    color: {C['text']} !important;
}}
[data-baseweb="popover"] ul,
[data-baseweb="menu"] {{
    background-color: {C['surface']} !important;
    border: 1px solid {C['border']} !important;
}}
[data-baseweb="option"]:hover {{
    background-color: {C['accent']} !important;
}}
/* タグ（multiselect選択済み） */
[data-baseweb="tag"] {{
    background-color: {C['accent']} !important;
    color: {C['white']} !important;
}}

/* ═══════════════════════════════════════════════════
   メトリクス
═══════════════════════════════════════════════════ */
[data-testid="stMetric"] {{
    background-color: {C['surface']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
}}
[data-testid="stMetricLabel"] * {{
    color: {C['text_muted']} !important;
    font-size: 0.82rem !important;
}}
[data-testid="stMetricValue"] * {{
    color: {C['white']} !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}}

/* ═══════════════════════════════════════════════════
   データフレーム・テーブル
═══════════════════════════════════════════════════ */
[data-testid="stDataFrame"] iframe {{
    border-radius: 8px !important;
}}
.stDataFrame {{
    border: 1px solid {C['border']} !important;
    border-radius: 8px !important;
}}

/* ═══════════════════════════════════════════════════
   アラート・通知
═══════════════════════════════════════════════════ */
[data-testid="stAlert"] {{
    border-radius: 8px !important;
    border-width: 1px !important;
}}
[data-testid="stAlert"][data-baseweb="notification"] {{
    background-color: rgba(79,142,247,0.12) !important;
    border-color: {C['accent']} !important;
}}
.stSuccess {{
    background-color: rgba(62,207,142,0.12) !important;
    border-color: {C['success']} !important;
    color: {C['success']} !important;
}}
.stWarning {{
    background-color: rgba(240,192,64,0.12) !important;
    border-color: {C['warning']} !important;
}}
.stError {{
    background-color: rgba(240,96,96,0.12) !important;
    border-color: {C['danger']} !important;
}}
.stInfo {{
    background-color: rgba(79,142,247,0.10) !important;
    border-color: {C['accent']} !important;
}}

/* ═══════════════════════════════════════════════════
   エクスパンダー
═══════════════════════════════════════════════════ */
[data-testid="stExpander"] {{
    background-color: {C['surface']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 8px !important;
    margin-bottom: 6px !important;
}}
[data-testid="stExpander"] summary {{
    color: {C['text']} !important;
}}
[data-testid="stExpander"] summary:hover {{
    color: {C['accent']} !important;
}}

/* ═══════════════════════════════════════════════════
   スライダー
═══════════════════════════════════════════════════ */
[data-testid="stSlider"] [role="slider"] {{
    background-color: {C['accent']} !important;
}}
[data-testid="stSlider"] [data-testid="stSliderTrack"] {{
    background-color: {C['surface2']} !important;
}}

/* ═══════════════════════════════════════════════════
   プログレスバー
═══════════════════════════════════════════════════ */
[data-testid="stProgress"] > div > div {{
    background: linear-gradient(90deg, {C['accent']}, {C['accent2']}) !important;
    border-radius: 4px !important;
}}
[data-testid="stProgress"] > div {{
    background-color: {C['surface2']} !important;
    border-radius: 4px !important;
}}

/* ═══════════════════════════════════════════════════
   区切り線
═══════════════════════════════════════════════════ */
hr {{
    border-color: {C['border']} !important;
    margin: 16px 0 !important;
}}

/* ═══════════════════════════════════════════════════
   トグル
═══════════════════════════════════════════════════ */
[data-testid="stToggle"] span[aria-checked="true"] {{
    background-color: {C['accent']} !important;
}}

/* ═══════════════════════════════════════════════════
   スクロールバー
═══════════════════════════════════════════════════ */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {C['bg']}; }}
::-webkit-scrollbar-thumb {{
    background: {C['border']};
    border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{ background: {C['accent']}; }}
</style>
""", unsafe_allow_html=True)


# ── 再利用可能なUIコンポーネント ──────────────────────────────────────────────

def page_header(icon: str, title: str, subtitle: str = ""):
    """統一ページヘッダー"""
    st.markdown(f"""
<div style="
    padding: 20px 24px 14px;
    margin-bottom: 20px;
    background: linear-gradient(135deg, {C['surface']} 0%, {C['surface2']} 100%);
    border-radius: 12px;
    border-left: 4px solid {C['accent']};
">
    <h1 style="margin:0; font-size:1.7rem; color:{C['white']} !important; border:none !important; padding:0 !important;">
        {icon} {title}
    </h1>
    {"" if not subtitle else f'<p style="margin:6px 0 0; color:{C["text_muted"]}; font-size:0.92rem;">{subtitle}</p>'}
</div>
""", unsafe_allow_html=True)


def info_card(label: str, value: str, icon: str = "", color: str = ""):
    """情報カード"""
    col = color or C['accent']
    st.markdown(f"""
<div style="
    background:{C['surface']};
    border:1px solid {C['border']};
    border-top: 3px solid {col};
    border-radius:10px;
    padding:14px 16px;
    margin-bottom:8px;
">
    <div style="color:{C['text_muted']};font-size:0.78rem;margin-bottom:4px">{icon} {label}</div>
    <div style="color:{C['white']};font-size:1.1rem;font-weight:600">{value}</div>
</div>
""", unsafe_allow_html=True)


def step_progress(current: int):
    """ステップ進捗バー（旧: columns版、後方互換）"""
    render_step_nav(current)


def render_step_nav(current: int):
    """上部ステップナビゲーションバー（アイコンなし）"""
    steps = [
        ("ログイン",        1),
        ("情報入力",        2),
        ("業界3C分析",     3),
        ("アタックリスト", 4),
    ]
    items_html = ""
    for label, step_no in steps:
        if step_no < current:
            cls = "step-done"
            badge = "✓"
        elif step_no == current:
            cls = "step-active"
            badge = str(step_no)
        else:
            cls = "step-inactive"
            badge = str(step_no)

        arrow = '<div class="step-arrow">›</div>' if step_no < 4 else ""
        items_html += f"""
<div class="step-item {cls}">
  <div class="step-badge">{badge}</div>
  <div class="step-label">{label}</div>
</div>{arrow}"""

    st.markdown(f"""
<style>
.step-nav {{
  display:flex; align-items:center; justify-content:center;
  gap:0; padding:14px 0 18px; margin-bottom:8px;
}}
.step-item {{
  display:flex; align-items:center; gap:8px;
  padding:8px 18px; border-radius:8px;
  font-size:0.88rem; font-weight:600;
  transition: all 0.2s;
}}
.step-badge {{
  width:24px; height:24px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:0.78rem; font-weight:700; flex-shrink:0;
}}
.step-done   {{ color:{C['success']};  background:rgba(62,207,142,0.10); }}
.step-done .step-badge {{ background:{C['success']}; color:{C['bg']}; }}
.step-active {{ color:{C['white']};    background:{C['accent']}; box-shadow:0 2px 12px rgba(79,142,247,0.4); }}
.step-active .step-badge {{ background:rgba(255,255,255,0.25); color:{C['white']}; }}
.step-inactive {{ color:{C['text_muted']}; background:{C['surface2']}; }}
.step-inactive .step-badge {{ background:{C['border']}; color:{C['text_muted']}; }}
.step-arrow {{
  color:{C['border']}; font-size:1.4rem; padding:0 4px;
  line-height:1; user-select:none;
}}
</style>
<div class="step-nav">{items_html}</div>
""", unsafe_allow_html=True)
