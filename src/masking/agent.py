"""
マスキングエージェント オーケストレーター
SharePoint からファイルを取得 → マスク → 保存先へアップロード
"""
from __future__ import annotations
import os
import io
from datetime import datetime
from typing import Callable

from .sharepoint_client import SharePointClient
from .word_masker import mask_word
from .excel_masker import mask_excel
from .ppt_masker import mask_ppt

# ローカル保存先
_OUTPUT_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'output', 'masked'
)

# ファイル拡張子 → 処理関数 / 出力拡張子
_PROCESSORS = {
    '.docx': (mask_word,  '.docx'),
    '.xlsx': (mask_excel, '.xlsx'),
    '.pptx': (mask_ppt,   '.docx'),  # PPT は Word で出力
}

Log = Callable[[str, str], None]  # (level, message)


def _log(callback: Log, level: str, msg: str):
    ts = datetime.now().strftime('%H:%M:%S')
    callback(level, f'[{ts}]  {msg}')


def _ensure_output_dir() -> str:
    os.makedirs(_OUTPUT_ROOT, exist_ok=True)
    return _OUTPUT_ROOT


def run(
    src_url:       str,
    src_user:      str = '',
    src_pass:      str = '',
    src_token:     str = '',
    src_client_id: str = '',
    src_client_secret: str = '',
    dst_url:       str = '',
    opts:          dict = None,
    callback:      Log = None,
) -> list[dict]:
    """
    メイン実行関数。
    return: list of result dicts
      {'name', 'out_name', 'ext', 'status', 'mask_count', 'local_path', 'error'}
    """
    opts     = opts or {}
    callback = callback or (lambda lv, msg: None)
    results  = []
    out_dir  = _ensure_output_dir()

    # ── ① ソース接続・ファイル一覧取得 ────────────────────────────────────────
    _log(callback, 'info', f'接続中: {src_url}')
    try:
        src_client = SharePointClient(
            src_url,
            username=src_user,
            password=src_pass,
            token=src_token,
            client_id=src_client_id,
            client_secret=src_client_secret,
        )
        files = src_client.list_files()
        _log(callback, 'success', f'対象ファイル {len(files)} 件を検出')
    except Exception as e:
        _log(callback, 'error', f'ソース接続エラー: {e}')
        raise

    if not files:
        _log(callback, 'warn', '対象ファイルが見つかりませんでした（Word/Excel/PPT のみ対象）')
        return results

    # ── ② 保存先クライアント（エラーでも処理は続行） ──────────────────────────
    dst_client = None
    dst_rel_path = None
    if dst_url:
        try:
            dst_client = SharePointClient(
                dst_url,
                username=src_user,
                password=src_pass,
                token=src_token,
                client_id=src_client_id,
                client_secret=src_client_secret,
            )
            dst_rel_path = dst_client.rel_path
            _log(callback, 'info', f'保存先確認: {dst_url}')
        except Exception as e:
            _log(callback, 'warn', f'保存先接続失敗（ローカル保存のみ）: {e}')

    # ── ③ ファイルごとに処理 ──────────────────────────────────────────────────
    for idx, file_info in enumerate(files, 1):
        name = file_info['name']
        server_url = file_info['server_relative_url']
        ext = os.path.splitext(name)[1].lower()

        if ext not in _PROCESSORS:
            continue

        _log(callback, 'info', f'[{idx}/{len(files)}] 処理開始: {name}')

        result = {
            'name': name,
            'out_name': '',
            'ext': ext,
            'status': 'error',
            'mask_count': 0,
            'local_path': '',
            'error': '',
        }

        try:
            # ダウンロード
            _log(callback, 'info', f'  ダウンロード中...')
            file_bytes = src_client.download_file(server_url)
            _log(callback, 'info', f'  {len(file_bytes):,} bytes 取得')

            # マスキング
            _log(callback, 'info', f'  マスキング処理中...')
            processor, out_ext = _PROCESSORS[ext]
            masked_bytes, mask_count = processor(file_bytes, opts)
            _log(callback, 'info', f'  マスク箇所: {mask_count} 件')

            # 出力ファイル名（元ファイル名 + _masked）
            stem = os.path.splitext(name)[0]
            out_name = f'{stem}_masked{out_ext}'
            result['out_name'] = out_name
            result['mask_count'] = mask_count

            # ローカル保存
            local_path = os.path.join(out_dir, out_name)
            with open(local_path, 'wb') as f:
                f.write(masked_bytes)
            result['local_path'] = local_path
            _log(callback, 'success', f'  ローカル保存: {local_path}')

            # 保存先 SharePoint へアップロード
            if dst_client and dst_rel_path:
                try:
                    dst_client.upload_file(dst_rel_path, out_name, masked_bytes)
                    _log(callback, 'success', f'  SharePoint アップロード完了: {out_name}')
                except Exception as e:
                    _log(callback, 'warn', f'  SharePoint アップロード失敗（ローカル保存は完了）: {e}')

            result['status'] = 'success'
            _log(callback, 'success', f'✅ {name} → {out_name}  (マスク {mask_count} 件)')

        except Exception as e:
            result['error'] = str(e)
            _log(callback, 'error', f'❌ {name}: {e}')

        results.append(result)

    # ── ④ サマリ ──────────────────────────────────────────────────────────────
    success = sum(1 for r in results if r['status'] == 'success')
    failed  = sum(1 for r in results if r['status'] != 'success')
    total_masks = sum(r['mask_count'] for r in results)
    _log(callback, 'info', f'─── 完了: 成功 {success} / 失敗 {failed} / マスク {total_masks} 件 ───')

    return results
