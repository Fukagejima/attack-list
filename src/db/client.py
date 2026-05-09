"""Supabase クライアントのシングルトン"""
from __future__ import annotations
import streamlit as st

_client = None


def get_supabase():
    """Supabase クライアントを返す（初回のみ初期化）"""
    global _client
    if _client is not None:
        return _client

    try:
        from supabase import create_client
        # Streamlit Cloud では st.secrets、ローカルでは環境変数から取得
        try:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
        except Exception:
            import os
            url = os.getenv("SUPABASE_URL", "")
            key = os.getenv("SUPABASE_KEY", "")

        if not url or not key:
            return None

        _client = create_client(url, key)
        return _client
    except Exception:
        return None


def is_db_enabled() -> bool:
    """DBが使える状態かチェック"""
    return get_supabase() is not None
