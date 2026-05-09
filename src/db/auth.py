"""ユーザー認証・管理"""
from __future__ import annotations
from src.db.client import get_supabase

try:
    import bcrypt
    _BCRYPT_OK = True
except Exception:
    _BCRYPT_OK = False


def _hash_password(password: str) -> str:
    if _BCRYPT_OK:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    import hashlib, os
    salt = os.urandom(16).hex()
    return salt + ":" + hashlib.sha256((salt + password).encode()).hexdigest()


def _verify_password(password: str, hashed: str) -> bool:
    import hashlib
    try:
        # bcrypt形式 ($2b$ または $2a$)
        if hashed.startswith("$2"):
            if _BCRYPT_OK:
                return bcrypt.checkpw(password.encode(), hashed.encode())
            return False
        # TEMP:sha256形式（初期セットアップ用）
        if hashed.startswith("TEMP:"):
            h = hashed[5:]
            return hashlib.sha256(password.encode()).hexdigest() == h
        # salt:sha256形式（bcryptなし環境）
        if ":" in hashed:
            salt, h = hashed.split(":", 1)
            return hashlib.sha256((salt + password).encode()).hexdigest() == h
        return False
    except Exception:
        return False


def login(username: str, password: str) -> dict | None:
    """
    ログイン認証。成功時はユーザー情報dict、失敗時はNoneを返す。
    1. Supabase usersテーブルで照合
    2. ユーザーが見つからない or DB接続失敗 → 環境変数(APP_USERNAME/APP_PASSWORD)でフォールバック
    """
    sb = get_supabase()
    if sb is None:
        return _legacy_login(username, password)

    try:
        res = sb.table("users").select("*").eq("username", username).eq("is_active", True).execute()
        if res.data:
            user = res.data[0]
            if _verify_password(password, user["password_hash"]):
                return user
            # DBにユーザーはいるがパスワードが違う → 認証失敗
            return None
        # DBにユーザーが存在しない → 環境変数フォールバック
        return _legacy_login(username, password)
    except Exception:
        return _legacy_login(username, password)


def _legacy_login(username: str, password: str) -> dict | None:
    """DBなし時のフォールバック（.envのID/PW）"""
    import os
    app_user = os.getenv("APP_USERNAME", "admin")
    app_pass = os.getenv("APP_PASSWORD", "password123")
    if username == app_user and password == app_pass:
        return {"id": "local", "username": username, "display_name": username, "role": "admin"}
    return None


def create_user(username: str, password: str, display_name: str, role: str = "member") -> tuple[bool, str]:
    """
    ユーザー作成。(成功フラグ, メッセージ) を返す。
    """
    sb = get_supabase()
    if sb is None:
        return False, "データベースが設定されていません"

    try:
        # 重複チェック
        existing = sb.table("users").select("id").eq("username", username).execute()
        if existing.data:
            return False, f"ユーザー名 '{username}' はすでに使用されています"

        hashed = _hash_password(password)
        sb.table("users").insert({
            "username": username,
            "password_hash": hashed,
            "display_name": display_name or username,
            "role": role,
            "is_active": True,
        }).execute()
        return True, f"ユーザー '{display_name or username}' を作成しました"
    except Exception as e:
        return False, f"エラー: {e}"


def list_users() -> list[dict]:
    """全ユーザー一覧を返す"""
    sb = get_supabase()
    if sb is None:
        return []
    try:
        res = sb.table("users").select("id, username, display_name, role, is_active, created_at").order("created_at").execute()
        return res.data or []
    except Exception:
        return []


def toggle_user_active(user_id: str, is_active: bool) -> bool:
    """ユーザーの有効/無効を切り替え"""
    sb = get_supabase()
    if sb is None:
        return False
    try:
        sb.table("users").update({"is_active": is_active}).eq("id", user_id).execute()
        return True
    except Exception:
        return False


def delete_user(user_id: str) -> bool:
    """ユーザーを削除"""
    sb = get_supabase()
    if sb is None:
        return False
    try:
        sb.table("users").delete().eq("id", user_id).execute()
        return True
    except Exception:
        return False
