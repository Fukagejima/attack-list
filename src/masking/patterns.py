"""
マスキング対象の正規表現パターン定義
プロンプト仕様: IP / URL / FQDN / Account / Password
"""
import re

# ── IPv4: 192.168.1.1, 10.0.0.1/24, 172.16.0.1:8080 ────────────────────────
_IPV4 = (
    r'\b'
    r'(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}'
    r'(?:25[0-5]|2[0-4]\d|[01]?\d\d?)'
    r'(?:/\d{1,2})?'          # CIDR
    r'(?::\d{1,5})?'          # port
    r'\b'
)

# ── IPv6: 簡略版（完全展開・短縮両対応）────────────────────────────────────
_IPV6 = (
    r'(?:'
    r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}'          # full
    r'|(?:[0-9a-fA-F]{1,4}:){1,7}:'                        # trailing ::
    r'|:(?::[0-9a-fA-F]{1,4}){1,7}'                        # leading ::
    r'|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}'
    r'|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}'
    r'|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}'
    r'|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}'
    r'|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}'
    r')'
    r'(?:/\d{1,3})?'  # CIDR
)

# ── URL: http/https/ftp（クエリ・パス・フラグメント含む）────────────────────
_URL = r'(?:https?|ftp)://[^\s<>"\')\]　-鿿]+'

# ── FQDN: example.com, server.internal, sub.domain.co.jp ────────────────────
_TLDS = (
    r'(?:com|net|org|edu|gov|mil|int'
    r'|jp|co\.jp|ac\.jp|go\.jp|ne\.jp|or\.jp|gr\.jp|ed\.jp|lg\.jp'
    r'|io|dev|app|cloud|ai|tech|info|biz'
    r'|azure|amazonaws|windows|microsoftonline|sharepoint'
    r'|local|internal|intra|corp|lan)'
)
_FQDN = (
    r'\b'
    r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)'
    r'+' + _TLDS + r'\b'
)

# ── Email: user@example.com ──────────────────────────────────────────────────
_EMAIL = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'

# ── GUID: 550e8400-e29b-41d4-a716-446655440000 ──────────────────────────────
_GUID = r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'

# ── Password value: "password: secret123" → keep label, mask value ──────────
# マッチグループ1=ラベル部分, グループ2=値部分
_PASSWORD = (
    r'(?P<label>'
    r'(?:password|passwd|pwd|pass|secret'
    r'|パスワード|パスワード値|パスワード文字列)'
    r'\s*[:：=]\s*'
    r')'
    r'(?P<value>\S+)'
)

RE = {
    'ipv4':     re.compile(_IPV4),
    'ipv6':     re.compile(_IPV6, re.IGNORECASE),
    'url':      re.compile(_URL, re.IGNORECASE),
    'fqdn':     re.compile(_FQDN, re.IGNORECASE),
    'email':    re.compile(_EMAIL, re.IGNORECASE),
    'guid':     re.compile(_GUID, re.IGNORECASE),
    'password': re.compile(_PASSWORD, re.IGNORECASE),
}

LABEL = {
    'ipv4':     '[MASKED_IP]',
    'ipv6':     '[MASKED_IP]',
    'url':      '[MASKED_URL]',
    'fqdn':     '[MASKED_FQDN]',
    'email':    '[MASKED_ACCOUNT]',
    'guid':     '[MASKED_ACCOUNT]',
    'password': None,  # partial replacement
}


def apply_masks(text: str, opts: dict) -> tuple[str, int]:
    """
    テキストにマスキングを適用する。
    opts: {'url': bool, 'ip': bool, 'password': bool}
    return: (masked_text, count_of_replacements)
    """
    if not text:
        return text, 0

    count = 0

    # 1. Password（先に処理してURL/FQDNとの誤爆を防ぐ）
    if opts.get('password'):
        def _pw_replace(m):
            nonlocal count
            count += 1
            return m.group('label') + '[MASKED_PASSWORD]'
        text = RE['password'].sub(_pw_replace, text)

    # 2. URL（FQDN より先に処理して二重マスク防止）
    if opts.get('url'):
        def _url_replace(m):
            nonlocal count
            count += 1
            return '[MASKED_URL]'
        text = RE['url'].sub(_url_replace, text)

    # 3. Email / GUID（URL の一部として既にマスク済みのものは再ヒットしない）
    if opts.get('url'):  # account は URL オプションに含める
        def _email_replace(m):
            nonlocal count
            count += 1
            return '[MASKED_ACCOUNT]'
        text = RE['email'].sub(_email_replace, text)

        def _guid_replace(m):
            nonlocal count
            count += 1
            return '[MASKED_ACCOUNT]'
        text = RE['guid'].sub(_guid_replace, text)

    # 4. IPv4 / IPv6
    if opts.get('ip'):
        def _ip4_replace(m):
            nonlocal count
            count += 1
            return '[MASKED_IP]'
        text = RE['ipv4'].sub(_ip4_replace, text)

        def _ip6_replace(m):
            nonlocal count
            count += 1
            return '[MASKED_IP]'
        text = RE['ipv6'].sub(_ip6_replace, text)

    # 5. FQDN（URL/IP マスク後の残りを処理）
    if opts.get('url'):
        def _fqdn_replace(m):
            nonlocal count
            count += 1
            return '[MASKED_FQDN]'
        text = RE['fqdn'].sub(_fqdn_replace, text)

    return text, count
