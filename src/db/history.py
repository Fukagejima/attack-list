"""分析セッション・履歴の保存・読み込み"""
from __future__ import annotations
import json
from datetime import datetime
from src.db.client import get_supabase


def save_session(user_id: str, user_input: dict) -> str | None:
    """
    分析セッションを保存してセッションIDを返す。
    失敗時はNoneを返す（ローカルのみで継続）。
    """
    sb = get_supabase()
    if sb is None:
        return None
    try:
        res = sb.table("analysis_sessions").insert({
            "user_id": user_id,
            "company_name":         user_input.get("company_name", ""),
            "service_name":         user_input.get("service_name", ""),
            "strengths":            user_input.get("strengths", ""),
            "existing_industry":    user_input.get("existing_industry", ""),
            "target_revenue_scale": user_input.get("target_revenue_scale", ""),
            "companies_per_industry": user_input.get("companies_per_industry", 10),
        }).execute()
        return res.data[0]["id"] if res.data else None
    except Exception:
        return None


def save_industry_analysis(session_id: str, analysis: list[dict]) -> bool:
    """業界3C分析結果を保存"""
    sb = get_supabase()
    if sb is None or not session_id:
        return False
    try:
        # 既存を削除して再保存
        sb.table("industry_results").delete().eq("session_id", session_id).execute()
        rows = [{"session_id": session_id, "data": json.dumps(r, ensure_ascii=False)} for r in analysis]
        sb.table("industry_results").insert(rows).execute()
        return True
    except Exception:
        return False


def save_attack_list(session_id: str, attack_list: list[dict], selected_industries: list[str]) -> bool:
    """アタックリストを保存"""
    sb = get_supabase()
    if sb is None or not session_id:
        return False
    try:
        sb.table("attack_list_results").delete().eq("session_id", session_id).execute()
        rows = [{
            "session_id": session_id,
            "selected_industries": json.dumps(selected_industries, ensure_ascii=False),
            "data": json.dumps(r, ensure_ascii=False),
        } for r in attack_list]
        sb.table("attack_list_results").insert(rows).execute()
        return True
    except Exception:
        return False


def load_my_sessions(user_id: str) -> list[dict]:
    """ユーザーの過去セッション一覧を返す"""
    sb = get_supabase()
    if sb is None:
        return []
    try:
        res = (
            sb.table("analysis_sessions")
            .select("id, company_name, service_name, existing_industry, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


def load_session_detail(session_id: str) -> dict:
    """
    セッションIDから分析結果一式を復元する。
    {"user_input": ..., "industry_analysis": [...], "attack_list": [...]} を返す。
    """
    sb = get_supabase()
    if sb is None:
        return {}
    try:
        # セッション基本情報
        s_res = sb.table("analysis_sessions").select("*").eq("id", session_id).execute()
        if not s_res.data:
            return {}
        session = s_res.data[0]

        user_input = {
            "company_name":           session.get("company_name", ""),
            "service_name":           session.get("service_name", ""),
            "strengths":              session.get("strengths", ""),
            "existing_industry":      session.get("existing_industry", ""),
            "target_revenue_scale":   session.get("target_revenue_scale", ""),
            "companies_per_industry": session.get("companies_per_industry", 10),
        }

        # 業界分析
        i_res = sb.table("industry_results").select("data").eq("session_id", session_id).execute()
        industry_analysis = [json.loads(r["data"]) for r in (i_res.data or [])]

        # アタックリスト
        a_res = sb.table("attack_list_results").select("data, selected_industries").eq("session_id", session_id).execute()
        attack_list = [json.loads(r["data"]) for r in (a_res.data or [])]
        selected = json.loads(a_res.data[0]["selected_industries"]) if a_res.data else []

        return {
            "user_input":         user_input,
            "industry_analysis":  industry_analysis,
            "attack_list":        attack_list,
            "selected_industries": selected,
            "created_at":         session.get("created_at", ""),
        }
    except Exception:
        return {}
