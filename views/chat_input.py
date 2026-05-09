"""
AIチャット形式の情報収集ビュー
- 途中スキップ機能
- 既存アタックリストCSVアップロード
- アイコンなし
"""
from __future__ import annotations
import json
import re
import streamlit as st
import anthropic
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL
from utils.styles import C
from src.parser.attack_list_parser import parse_csv, format_context_for_claude

def _get_client():
    """APIクライアントを都度生成（キーの遅延読み込み対応）"""
    from config.settings import ANTHROPIC_API_KEY as _KEY
    return anthropic.Anthropic(api_key=_KEY)


_CHAT_SYSTEM = """あなたは営業戦略アシスタントです。
ユーザーと自然な日本語で会話しながら、以下の情報を収集してください。

【収集する情報】
1. company_name           : 会社名
2. service_name           : サービス名・製品名
3. strengths              : 強み・差別化ポイント（できれば3つ以上）
4. existing_industry      : 現在の主要取引先業界
5. target_revenue_scale   : ターゲット企業の売上規模（例：100億円以上、10〜100億円、規模問わず など）
6. target_size            : ターゲット企業の従業員規模（大企業・中堅・中小など）
7. companies_per_industry : 業界あたり出力企業数（デフォルト10社）

【会話のルール】
- 質問は1回につき1つだけ
- ユーザーの回答が短い場合は「もう少し詳しく教えてください」と促す
- 強みは最低3つ引き出す（「他にはありますか？」と促す）
- existing_industryとtarget_revenue_scaleは必ず聞く
- すべて収集できたら確認サマリーを出し「この内容で分析を始めますか？」と聞く
- フレンドリーかつプロフェッショナルなトーン

【各応答の末尾に必ず以下のSTATUSブロックを付ける（非表示処理するので必ず入れること）】
[STATUS]{"company_name":null,"service_name":null,"strengths":null,"existing_industry":null,"target_revenue_scale":null,"target_size":null,"companies_per_industry":10}[/STATUS]
→ 収集できた項目はnullから実際の値に更新すること

【完了シグナル】
ユーザーが確認OKを出したら、以下の形式のみ出力する（他のテキスト不要）:
[COLLECTED]
{"company_name":"...","service_name":"...","strengths":"...","existing_industry":"...","target_revenue_scale":"...","target_size":"...","companies_per_industry":10}
[/COLLECTED]"""


def _call_claude(messages: list[dict]) -> str:
    resp = _get_client().messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=_CHAT_SYSTEM,
        messages=messages,
    )
    return resp.content[0].text


def _extract_status(text: str) -> dict:
    """[STATUS]{...}[/STATUS] から現在収集済みフィールドを取得"""
    m = re.search(r"\[STATUS\](\{.*?\})\[/STATUS\]", text, re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except Exception:
        return {}


def _extract_collected(text: str) -> dict | None:
    """[COLLECTED]{...}[/COLLECTED] から最終データを取得"""
    m = re.search(r"\[COLLECTED\]\s*(\{.*?\})\s*\[/COLLECTED\]", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def _clean_display(text: str) -> str:
    """STATUSとCOLLECTEDブロックを除去して表示用テキストを返す"""
    text = re.sub(r"\[STATUS\].*?\[/STATUS\]", "", text, flags=re.DOTALL)
    text = re.sub(r"\[COLLECTED\].*?\[/COLLECTED\]", "", text, flags=re.DOTALL)
    return text.strip()


def _finalize_with_partial(partial: dict) -> dict:
    """スキップ時：収集済みの部分データを使って user_input を組み立てる"""
    return {
        "company_name":           partial.get("company_name") or "（未入力）",
        "service_name":           partial.get("service_name") or "（未入力）",
        "strengths":              partial.get("strengths")    or "（未入力）",
        "existing_industry":      partial.get("existing_industry") or "（未入力）",
        "target_revenue_scale":   partial.get("target_revenue_scale") or "規模問わず",
        "company_size_own":       partial.get("target_size") or "規模問わず",
        "target_company_size":    [partial.get("target_size") or "規模問わず"],
        "companies_per_industry": int(partial.get("companies_per_industry") or 10),
    }


def _field_label(key: str) -> str:
    return {
        "company_name":           "会社名",
        "service_name":           "サービス名",
        "strengths":              "強み",
        "existing_industry":      "主要取引先業界",
        "target_revenue_scale":   "売上規模",
        "target_size":            "従業員規模",
        "companies_per_industry": "出力企業数/業界",
    }.get(key, key)


def render():
    # ── セッション初期化 ──────────────────────────────────────────────────────
    for key, default in [
        ("chat_messages", []),
        ("chat_done",     False),
        ("chat_partial",  {}),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── 既存アタックリスト アップロード ───────────────────────────────────────
    with st.expander("既存アタックリストをアップロード（オプション）", expanded=False):
        st.caption("CSVをアップロードすると、既存顧客の傾向を加味した分析が可能になります。")
        uploaded = st.file_uploader(
            "CSVファイルを選択",
            type=["csv"],
            key="attack_list_upload",
            label_visibility="collapsed",
        )
        if uploaded:
            try:
                df, summary = parse_csv(uploaded.read())
                st.session_state.existing_list_summary  = summary
                st.session_state.existing_list_context  = format_context_for_claude(summary)
                st.success(f"読み込み完了（{len(df)}社）")

                # サマリー表示
                col1, col2, col3 = st.columns(3)
                with col1:
                    if "industry_distribution" in summary:
                        top = list(summary["industry_distribution"].items())[:4]
                        st.markdown("**業界分布**")
                        for k, v in top:
                            st.caption(f"・{k}: {v}社")
                with col2:
                    if "status_distribution" in summary:
                        st.markdown("**ステータス**")
                        for k, v in list(summary["status_distribution"].items())[:4]:
                            st.caption(f"・{k}: {v}社")
                with col3:
                    if "listed_distribution" in summary:
                        st.markdown("**上場区分**")
                        for k, v in list(summary["listed_distribution"].items())[:3]:
                            st.caption(f"・{k}: {v}社")
            except Exception as e:
                st.error(f"読み込みエラー: {e}")
        elif "existing_list_context" in st.session_state:
            st.info("アップロード済みのデータを使用中です。")

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # ── 説明バー ──────────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {C['border']};
border-left:3px solid {C['accent']};border-radius:8px;
padding:10px 16px;margin-bottom:14px">
<span style="color:{C['text']};font-size:0.88rem">
AIとの会話で自社・サービス情報を入力してください。
途中で「この情報で進む」ボタンを押せばいつでも次のステップに進めます。
</span>
</div>
""", unsafe_allow_html=True)

    # ── ウェルカムメッセージ初期化 ────────────────────────────────────────────
    if not st.session_state.chat_messages:
        with st.spinner(""):
            try:
                first = _call_claude([{"role": "user", "content": "はじめます"}])
            except Exception:
                first = "こんにちは。営業アタックリスト作成をお手伝いします。まず御社の会社名を教えてください。"
        st.session_state.chat_messages = [{"role": "assistant", "content": first}]
        # 初回STATUSも更新
        st.session_state.chat_partial = _extract_status(first)
        st.rerun()

    # ── 収集状況パネル ────────────────────────────────────────────────────────
    partial = st.session_state.chat_partial
    required_keys = ["company_name", "service_name", "strengths", "existing_industry"]
    filled = [k for k in required_keys if partial.get(k) not in (None, "")]
    all_required_filled = len(filled) == len(required_keys)

    if partial:
        items_html = ""
        for key in ["company_name", "service_name", "strengths", "existing_industry", "target_revenue_scale", "target_size"]:
            val = partial.get(key)
            if val and val != "null":
                items_html += f'<span style="background:{C["surface2"]};border:1px solid {C["border"]};border-radius:4px;padding:2px 8px;font-size:0.78rem;color:{C["text"]};margin:2px">{_field_label(key)}: {str(val)[:20]}</span> '
            else:
                items_html += f'<span style="border:1px dashed {C["border"]};border-radius:4px;padding:2px 8px;font-size:0.78rem;color:{C["text_muted"]};margin:2px">{_field_label(key)}: 未入力</span> '
        st.markdown(f"""
<div style="background:{C['surface']};border:1px solid {C['border']};border-radius:8px;
padding:10px 14px;margin-bottom:10px;display:flex;flex-wrap:wrap;gap:4px;align-items:center">
<span style="color:{C['text_muted']};font-size:0.78rem;margin-right:6px">収集状況</span>
{items_html}
</div>
""", unsafe_allow_html=True)

    # ── チャット履歴 ──────────────────────────────────────────────────────────
    chat_container = st.container(height=380)
    with chat_container:
        for msg in st.session_state.chat_messages:
            content = _clean_display(msg["content"])
            if not content:
                continue
            with st.chat_message(msg["role"], avatar=None):
                st.markdown(content)

    # ── 完了後のアクション ────────────────────────────────────────────────────
    if st.session_state.chat_done:
        st.success("情報収集が完了しました。")
        col1, col2 = st.columns([1, 2])
        with col2:
            if st.button("業界3C分析へ進む", use_container_width=True, type="primary"):
                st.session_state.page = "heatmap"
                st.session_state.current_step = 3
                st.session_state.industry_analysis = []
                st.session_state.attack_list = []
                st.session_state.selected_industries = []
                st.rerun()
        with col1:
            if st.button("入力をやり直す", use_container_width=True):
                st.session_state.chat_messages = []
                st.session_state.chat_done = False
                st.session_state.user_input = {}
                st.session_state.chat_partial = {}
                st.rerun()
        return

    # ── スキップ / チャット入力 ───────────────────────────────────────────────
    col_input, col_skip = st.columns([4, 1])

    with col_input:
        user_text = st.chat_input("メッセージを入力...", key="chat_main_input")

    with col_skip:
        skip_min_keys = ["company_name", "service_name", "existing_industry", "target_revenue_scale"]
        skip_disabled = not all(
            partial.get(k) not in (None, "", "null") for k in skip_min_keys
        )
        if st.button(
            "この情報で進む",
            use_container_width=True,
            disabled=skip_disabled,
            help="会社名・サービス名・主要取引先業界が入力されると有効になります",
        ):
            st.session_state.user_input = _finalize_with_partial(partial)
            st.session_state.chat_done = True
            st.rerun()

    if skip_disabled:
        missing = [_field_label(k) for k in skip_min_keys
                   if partial.get(k) in (None, "", "null")]
        st.caption(f"未入力: {' / '.join(missing)}")

    # ── ユーザー入力処理 ──────────────────────────────────────────────────────
    if user_text:
        st.session_state.chat_messages.append({"role": "user", "content": user_text})
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.chat_messages
        ]
        with st.spinner(""):
            try:
                reply = _call_claude(api_messages)
            except Exception as e:
                reply = f"エラーが発生しました: {e}"

        st.session_state.chat_messages.append({"role": "assistant", "content": reply})

        # STATUS更新
        new_partial = _extract_status(reply)
        if new_partial:
            # null以外の値だけ上書き
            for k, v in new_partial.items():
                if v is not None and v != "null":
                    st.session_state.chat_partial[k] = v

        # 完了シグナル確認
        collected = _extract_collected(reply)
        if collected:
            st.session_state.user_input = {
                "company_name":           collected.get("company_name", ""),
                "service_name":           collected.get("service_name", ""),
                "strengths":              collected.get("strengths", ""),
                "existing_industry":      collected.get("existing_industry", ""),
                "target_revenue_scale":   collected.get("target_revenue_scale", "規模問わず"),
                "company_size_own":       collected.get("target_size", "規模問わず"),
                "target_company_size":    [collected.get("target_size", "規模問わず")],
                "companies_per_industry": int(collected.get("companies_per_industry", 10)),
            }
            st.session_state.chat_done = True

        st.rerun()
