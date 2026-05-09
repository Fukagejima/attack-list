"""
SharePoint ファイル取得・アップロードクライアント
Microsoft Graph API ベース（共有リンク・通常URL 両対応）
"""
from __future__ import annotations
import base64
import io
import os
import re
from urllib.parse import urlparse, unquote, parse_qs

import requests

try:
    from office365.sharepoint.client_context import ClientContext
    from office365.runtime.auth.user_credential import UserCredential
    _HAS_O365 = True
except ImportError:
    _HAS_O365 = False

try:
    import msal
    _HAS_MSAL = True
except ImportError:
    _HAS_MSAL = False

SUPPORTED_EXTS = {'.docx', '.xlsx', '.pptx'}
GRAPH_BASE     = "https://graph.microsoft.com/v1.0"


# ── URL ユーティリティ ────────────────────────────────────────────────────────

def is_sharing_link(url: str) -> bool:
    """/:f:/ や /:b:/ 形式の SharePoint 共有リンクかどうか（例: /:f:/s/site/token）"""
    return bool(re.search(r'/:[a-z]+:', url, re.I))


def _encode_for_graph_shares(url: str) -> str:
    """
    共有URLを Graph API の shareId 形式にエンコード
    MS Docs: base64url(url) → 先頭に u! を付与
    """
    b64 = base64.b64encode(url.encode('utf-8')).decode()
    safe = b64.replace('+', '-').replace('/', '_').rstrip('=')
    return f"u!{safe}"


def _extract_site_url(scheme: str, netloc: str, path: str) -> str:
    parts = path.split('/')
    for kw in ('sites', 'teams', 'personal'):
        if kw in parts:
            idx = parts.index(kw)
            if idx + 1 < len(parts):
                return f"{scheme}://{netloc}" + '/'.join(parts[:idx + 2])
    return f"{scheme}://{netloc}"


def parse_sharepoint_url(url: str) -> tuple[str, str]:
    """
    SharePoint URL からサイトURLとサーバー相対パスを返す。
    共有リンク形式の場合はサイトURLのみ（パスは Graph API で解決）。
    """
    parsed = urlparse(url)
    scheme, netloc = parsed.scheme or 'https', parsed.netloc
    qs = parse_qs(parsed.query)

    # 形式A: ?id= パラメータ
    if 'id' in qs:
        rel_path = unquote(qs['id'][0])
        site_url = _extract_site_url(scheme, netloc, parsed.path)
        return site_url, rel_path

    # 形式B: 共有リンク /:f:/s/ /:b:/s/
    if is_sharing_link(url):
        m = re.match(r'(https?://[^/]+/:[a-z]:[a-z]/([^/]+))', url, re.I)
        site_name = url.split('/:')[0].rsplit('/', 1)[-1] if '/' in url else ''
        site_url  = f"{scheme}://{netloc}/sites/{site_name}" if site_name else f"{scheme}://{netloc}"
        return site_url, '/'   # rel_path は Graph API で解決

    # 形式C: 直接パス
    decoded_path = unquote(parsed.path)
    decoded_path = re.sub(r'/Forms/AllItems\.aspx$', '', decoded_path, flags=re.I)
    decoded_path = re.sub(r'/AllItems\.aspx$',       '', decoded_path, flags=re.I)
    site_url  = _extract_site_url(scheme, netloc, decoded_path)
    site_path = site_url.replace(f"{scheme}://{netloc}", '')
    rel_path  = decoded_path[len(site_path):] if decoded_path.startswith(site_path) else decoded_path
    return site_url, rel_path or '/'


# ── Graph API ヘルパー ────────────────────────────────────────────────────────

def _gh(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def _parse_graph_items(items: list) -> list[dict]:
    results = []
    for item in items:
        name = item.get('name', '')
        ext  = os.path.splitext(name)[1].lower()
        if ext in SUPPORTED_EXTS:
            results.append({
                'name':                 name,
                'size':                 item.get('size', 0),
                'server_relative_url':  item.get('@microsoft.graph.downloadUrl', ''),
            })
    return results


def _resolve_sharing_link(sharing_url: str, token: str) -> tuple[str, str]:
    """
    共有リンクのリダイレクトを追跡して実際のフォルダ URL を取得し
    (site_url, rel_path) を返す。
    リダイレクト先の ?id= パラメータからサーバー相対パスを抽出する。
    """
    for headers in [
        {'Authorization': f'Bearer {token}'},
        {},  # 認証なしでも試みる（共有リンクはパブリックアクセス可能な場合がある）
    ]:
        try:
            resp = requests.get(
                sharing_url,
                headers=headers,
                allow_redirects=True,
                timeout=30,
            )
            final_url = resp.url
            # ?id= が含まれていれば成功
            if final_url and '?id=' in final_url:
                return parse_sharepoint_url(final_url)
            # リダイレクト先が元と異なり、SharePoint ドメインならそのまま解析
            if final_url and final_url != sharing_url and 'sharepoint.com' in final_url:
                site_url, rel = parse_sharepoint_url(final_url)
                if rel and rel != '/':
                    return site_url, rel
        except Exception:
            pass
    return parse_sharepoint_url(sharing_url)


# ── MSAL 認証ヘルパー ─────────────────────────────────────────────────────────

def _get_msal_ropc_token(site_url: str, username: str, password: str) -> str | None:
    if not _HAS_MSAL:
        return None
    m = re.match(r'https?://([^.]+)\.sharepoint\.com', site_url, re.I)
    tenant = f"{m.group(1)}.onmicrosoft.com" if m else 'common'
    app    = msal.PublicClientApplication(
        client_id='9bc3ab49-b65d-410a-85ad-de819febfddc',
        authority=f"https://login.microsoftonline.com/{tenant}",
    )
    result = app.acquire_token_by_username_password(
        username=username, password=password,
        scopes=[f"{site_url}/.default"],
    )
    return result.get('access_token')


def _get_apponly_token(site_url: str, client_id: str, client_secret: str) -> str | None:
    if not _HAS_MSAL:
        return None
    m = re.match(r'https?://([^.]+)\.sharepoint\.com', site_url, re.I)
    tenant = f"{m.group(1)}.onmicrosoft.com" if m else 'common'
    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=f"https://login.microsoftonline.com/{tenant}",
    )
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    return result.get('access_token')


def _rest_list_files(site_url: str, rel_path: str, token: str) -> list[dict]:
    """
    SharePoint REST API でフォルダ内ファイルを列挙する。
    rel_path が '/' の場合はルートドキュメントライブラリを対象にする。
    """
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json;odata=verbose',
    }

    # rel_path が '/' や空の場合は Shared Documents を試みる
    if not rel_path or rel_path == '/':
        # サイトのドキュメントライブラリ一覧を取得して最初のものを使う
        libs_url = f"{site_url}/_api/web/lists?$filter=BaseTemplate eq 101&$select=Title,RootFolder/ServerRelativeUrl&$expand=RootFolder"
        try:
            r = requests.get(libs_url, headers=headers, timeout=30)
            r.raise_for_status()
            libs = r.json().get('d', {}).get('results', [])
            if libs:
                rel_path = libs[0].get('RootFolder', {}).get('ServerRelativeUrl', '/Shared Documents')
        except Exception:
            rel_path = '/Shared Documents'

    encoded = requests.utils.quote(rel_path, safe='/')
    url = f"{site_url}/_api/web/GetFolderByServerRelativeUrl('{encoded}')/Files?$select=Name,Length,ServerRelativeUrl"

    results = []
    while url:
        try:
            resp = requests.get(url, headers=headers, timeout=60)
            resp.raise_for_status()
            data  = resp.json().get('d', {})
            items = data.get('results', [])
            for item in items:
                name = item.get('Name', '')
                ext  = os.path.splitext(name)[1].lower()
                if ext in SUPPORTED_EXTS:
                    results.append({
                        'name':                name,
                        'size':                int(item.get('Length', 0)),
                        'server_relative_url': item.get('ServerRelativeUrl', ''),
                    })
            # ページネーション
            url = data.get('__next')
        except Exception as e:
            raise RuntimeError(f"SharePoint REST ファイル一覧取得エラー ({url}): {e}") from e

    return results


# ── メインクライアント ─────────────────────────────────────────────────────────

class SharePointClient:
    def __init__(
        self,
        url:           str,
        username:      str = '',
        password:      str = '',
        token:         str = '',   # デバイスコードフローや手動で取得したトークン
        client_id:     str = '',
        client_secret: str = '',
    ):
        self.url           = url
        self.username      = username
        self.password      = password
        self._client_id    = client_id
        self._client_secret= client_secret
        self.site_url, self.rel_path = parse_sharepoint_url(url)
        self._ctx   = None
        # Bearer / device code トークン（先頭の "Bearer " を除去して保持）
        self._token = token.strip().removeprefix('Bearer').strip() if token else None

    def _try_apponly(self) -> bool:
        if not (self._client_id and self._client_secret):
            return False
        try:
            t = _get_apponly_token(self.site_url, self._client_id, self._client_secret)
            if t:
                self._token = t
                return True
        except Exception:
            pass
        return False

    def _try_o365(self) -> bool:
        if not (_HAS_O365 and self.username and self.password):
            return False
        try:
            ctx = ClientContext(self.site_url).with_credentials(
                UserCredential(self.username, self.password)
            )
            ctx.web.get().execute_query()
            self._ctx = ctx
            return True
        except Exception:
            return False

    def _try_ropc(self) -> bool:
        if not (self.username and self.password):
            return False
        try:
            t = _get_msal_ropc_token(self.site_url, self.username, self.password)
            if t:
                self._token = t
                return True
        except Exception:
            pass
        return False

    def _ensure_auth(self):
        if self._ctx or self._token:
            return
        if self._try_apponly(): return
        if self._try_o365():    return
        if self._try_ropc():    return
        raise ConnectionError(
            "SharePoint 認証に失敗しました。\n\n"
            "「🔐 ブラウザでログイン（推奨）」認証方式を選択し、\n"
            "「Microsoft ログインを開始」ボタンから認証してください。"
        )

    # ── ファイル一覧 ──────────────────────────────────────────────────────────
    def list_files(self) -> list[dict]:
        self._ensure_auth()

        site_url = self.site_url
        rel_path = self.rel_path

        if self._token:
            # 共有リンクはリダイレクト追跡で実際のフォルダパスを解決
            if is_sharing_link(self.url):
                site_url, rel_path = _resolve_sharing_link(self.url, self._token)

            return _rest_list_files(site_url, rel_path, self._token)

        # office365 フォールバック
        folder = self._ctx.web.get_folder_by_server_relative_url(rel_path)
        files  = folder.files
        self._ctx.load(files)
        self._ctx.execute_query()
        return [
            {
                'name':                f.properties['Name'],
                'size':                f.properties.get('Length', 0),
                'server_relative_url': f.properties['ServerRelativeUrl'],
            }
            for f in files
            if os.path.splitext(f.properties['Name'])[1].lower() in SUPPORTED_EXTS
        ]

    # ── ダウンロード ─────────────────────────────────────────────────────────
    def download_file(self, server_relative_url: str) -> bytes:
        self._ensure_auth()

        if self._token:
            encoded = requests.utils.quote(server_relative_url)
            api_url = f"{self.site_url}/_api/web/GetFileByServerRelativeUrl('{encoded}')/$value"
            resp = requests.get(
                api_url,
                headers={'Authorization': f'Bearer {self._token}'},
                timeout=120,
            )
            resp.raise_for_status()
            return resp.content

        buf = io.BytesIO()
        (self._ctx.web
            .get_file_by_server_relative_url(server_relative_url)
            .download(buf)
            .execute_query())
        return buf.getvalue()

    # ── アップロード ─────────────────────────────────────────────────────────
    def upload_file(self, folder_rel_path: str, file_name: str, content: bytes) -> None:
        self._ensure_auth()

        if self._token:
            encoded = requests.utils.quote(folder_rel_path)
            api_url = (
                f"{self.site_url}/_api/web/GetFolderByServerRelativeUrl('{encoded}')"
                f"/Files/add(url='{requests.utils.quote(file_name)}',overwrite=true)"
            )
            resp = requests.post(
                api_url,
                data=content,
                headers={
                    'Authorization': f'Bearer {self._token}',
                    'Accept': 'application/json;odata=verbose',
                    'Content-Type': 'application/octet-stream',
                },
                timeout=120,
            )
            resp.raise_for_status()
            return

        folder = self._ctx.web.get_folder_by_server_relative_url(folder_rel_path)
        folder.upload_file(file_name, content).execute_query()
