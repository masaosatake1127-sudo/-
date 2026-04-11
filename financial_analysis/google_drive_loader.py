"""
Google Drive ファイルローダー

Google Drive 上の PDF / Excel / Word ファイルを直接読み込み、財務分析を実行します。

対応する共有方法:
  1. 【共有リンク（公開）】 "リンクを知っている全員" で共有されているファイル
     → 認証不要でそのまま利用可能

  2. 【サービスアカウント】 非公開ファイルを組織内で自動処理したい場合
     → Google Cloud のサービスアカウントキー(JSON)が必要

対応する URL 形式:
  - https://drive.google.com/file/d/FILE_ID/view?usp=sharing
  - https://drive.google.com/open?id=FILE_ID
  - https://docs.google.com/spreadsheets/d/FILE_ID/...  (Google スプレッドシート → xlsx に変換)
  - https://docs.google.com/document/d/FILE_ID/...     (Google ドキュメント → docx に変換)

使い方:
    # 公開ファイル（認証不要）
    loader = GoogleDriveLoader()
    data = loader.load_from_url(
        "https://drive.google.com/file/d/xxxxx/view?usp=sharing",
        company_name="株式会社〇〇",
    )

    # サービスアカウントで非公開ファイルを取得
    loader = GoogleDriveLoader(credentials_path="service_account.json")
    data = loader.load_from_url("https://drive.google.com/file/d/xxxxx/view")
"""

import io
import os
import re
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

import requests

from .models import FinancialData
from .file_loader import load_financial_data

# Google Drive / Docs の URL パターン
_DRIVE_FILE_RE = re.compile(
    r"drive\.google\.com/(?:file/d/|open\?id=)([A-Za-z0-9_-]+)"
)
_SHEETS_RE = re.compile(
    r"docs\.google\.com/spreadsheets/d/([A-Za-z0-9_-]+)"
)
_DOCS_RE = re.compile(
    r"docs\.google\.com/document/d/([A-Za-z0-9_-]+)"
)

# ダウンロード URL のテンプレート
_DRIVE_DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id={file_id}"
_SHEETS_EXPORT_URL = (
    "https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
)
_DOCS_EXPORT_URL = (
    "https://docs.google.com/document/d/{file_id}/export?format=docx"
)


class GoogleDriveLoader:
    """
    Google Drive からファイルをダウンロードして財務分析を行うローダー。

    Args:
        credentials_path: サービスアカウントキー JSON のパス（非公開ファイル用）
                          省略時は公開ファイルのみ対応（認証なし）
    """

    def __init__(self, credentials_path: Optional[str] = None):
        self._credentials_path = credentials_path
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "financial-analysis-tool/1.0"})

        if credentials_path:
            self._service = self._build_drive_service(credentials_path)
        else:
            self._service = None

    # ------------------------------------------------------------------
    # 公開 API
    # ------------------------------------------------------------------

    def load_from_url(
        self,
        url: str,
        company_name: str = "",
        period: str = "",
        unit: float = 1.0,
        sheet_name: Optional[str] = None,
    ) -> FinancialData:
        """
        Google Drive の共有 URL からファイルをダウンロードして財務分析を行う。

        Args:
            url:          Google Drive の共有 URL
            company_name: 企業名（省略時はファイル名）
            period:       会計期間（例: "2024年3月期"）
            unit:         金額単位の倍率（千円=1000, 百万円=1000000）
            sheet_name:   Excel のシート名（省略時は自動選択）
        """
        file_id, file_type = self._parse_url(url)

        print(f"Google Drive からダウンロード中... (ID: {file_id})")

        if self._service:
            # サービスアカウント経由
            content, filename = self._download_with_api(file_id, file_type)
        else:
            # 直接ダウンロード（公開ファイル）
            content, filename = self._download_public(file_id, file_type)

        if not company_name:
            company_name = Path(filename).stem

        return self._analyze_content(
            content=content,
            filename=filename,
            company_name=company_name,
            period=period,
            unit=unit,
            sheet_name=sheet_name,
        )

    def load_from_file_id(
        self,
        file_id: str,
        file_type: str = "auto",
        company_name: str = "",
        period: str = "",
        unit: float = 1.0,
        sheet_name: Optional[str] = None,
    ) -> FinancialData:
        """
        Google Drive のファイル ID を直接指定して読み込む。

        Args:
            file_id:   Google Drive のファイル ID
            file_type: "pdf" / "excel" / "word" / "sheets" / "docs" / "auto"
        """
        print(f"Google Drive からダウンロード中... (ID: {file_id})")

        if self._service:
            content, filename = self._download_with_api(file_id, file_type)
        else:
            content, filename = self._download_public(file_id, file_type)

        if not company_name:
            company_name = Path(filename).stem

        return self._analyze_content(
            content=content,
            filename=filename,
            company_name=company_name,
            period=period,
            unit=unit,
            sheet_name=sheet_name,
        )

    # ------------------------------------------------------------------
    # URL パース
    # ------------------------------------------------------------------

    def _parse_url(self, url: str):
        """URL から (file_id, file_type) を返す"""
        m = _SHEETS_RE.search(url)
        if m:
            return m.group(1), "sheets"

        m = _DOCS_RE.search(url)
        if m:
            return m.group(1), "docs"

        m = _DRIVE_FILE_RE.search(url)
        if m:
            return m.group(1), "drive"

        raise ValueError(
            f"Google Drive の URL を認識できませんでした: {url}\n"
            "対応形式:\n"
            "  https://drive.google.com/file/d/FILE_ID/view?usp=sharing\n"
            "  https://docs.google.com/spreadsheets/d/FILE_ID/edit\n"
            "  https://docs.google.com/document/d/FILE_ID/edit"
        )

    # ------------------------------------------------------------------
    # ダウンロード（認証なし・公開ファイル）
    # ------------------------------------------------------------------

    def _download_public(self, file_id: str, file_type: str):
        """公開ファイルを直接ダウンロードする"""
        if file_type == "sheets":
            url = _SHEETS_EXPORT_URL.format(file_id=file_id)
            filename = f"{file_id}.xlsx"
        elif file_type == "docs":
            url = _DOCS_EXPORT_URL.format(file_id=file_id)
            filename = f"{file_id}.docx"
        else:
            url = _DRIVE_DOWNLOAD_URL.format(file_id=file_id)
            filename = f"{file_id}.tmp"

        resp = self._session.get(url, stream=True, timeout=60)

        # 大容量ファイルのウイルススキャン警告ページへの対処
        if "Content-Disposition" not in resp.headers and "text/html" in resp.headers.get(
            "Content-Type", ""
        ):
            confirm_token = self._extract_confirm_token(resp.text)
            if confirm_token:
                url = f"{url}&confirm={confirm_token}"
                resp = self._session.get(url, stream=True, timeout=60)
            else:
                raise ValueError(
                    "ファイルをダウンロードできませんでした。\n"
                    "ファイルの共有設定を「リンクを知っている全員が閲覧可能」に変更してください。\n"
                    "または --credentials でサービスアカウントキーを指定してください。"
                )

        resp.raise_for_status()

        # Content-Disposition からファイル名を取得
        cd = resp.headers.get("Content-Disposition", "")
        fn_match = re.search(r'filename[*]?=["\']?([^"\';\n]+)', cd)
        if fn_match:
            filename = fn_match.group(1).strip().strip('"\'')
            # RFC 5987 形式（filename*=UTF-8''...）のデコード
            if filename.startswith("UTF-8''"):
                from urllib.parse import unquote
                filename = unquote(filename[7:])

        # Content-Type からも拡張子を推測
        ct = resp.headers.get("Content-Type", "")
        if filename.endswith(".tmp"):
            filename = self._guess_filename(file_id, ct)

        return resp.content, filename

    @staticmethod
    def _extract_confirm_token(html: str) -> Optional[str]:
        """大容量ファイルダウンロードの confirm トークンを HTML から抽出する"""
        m = re.search(r'confirm=([^&"\']+)', html)
        return m.group(1) if m else None

    @staticmethod
    def _guess_filename(file_id: str, content_type: str) -> str:
        """Content-Type からファイル名・拡張子を推測する"""
        ct_map = {
            "application/pdf": ".pdf",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
            "application/vnd.ms-excel": ".xls",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/msword": ".doc",
        }
        for mime, ext in ct_map.items():
            if mime in content_type:
                return f"{file_id}{ext}"
        return f"{file_id}.bin"

    # ------------------------------------------------------------------
    # ダウンロード（サービスアカウント）
    # ------------------------------------------------------------------

    def _build_drive_service(self, credentials_path: str):
        """Google Drive API サービスオブジェクトを構築する"""
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        scopes = ["https://www.googleapis.com/auth/drive.readonly"]
        creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=scopes
        )
        return build("drive", "v3", credentials=creds)

    def _download_with_api(self, file_id: str, file_type: str):
        """Google Drive API 経由でファイルをダウンロードする"""
        from googleapiclient.http import MediaIoBaseDownload

        # ファイルのメタデータを取得
        meta = self._service.files().get(fileId=file_id, fields="name,mimeType").execute()
        mime_type = meta.get("mimeType", "")
        filename = meta.get("name", file_id)

        # Google Workspace ファイルはエクスポートが必要
        export_mime = {
            "application/vnd.google-apps.spreadsheet": (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ".xlsx",
            ),
            "application/vnd.google-apps.document": (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ".docx",
            ),
        }

        buf = io.BytesIO()
        if mime_type in export_mime:
            export_mime_type, ext = export_mime[mime_type]
            if not filename.endswith(ext):
                filename += ext
            request = self._service.files().export_media(
                fileId=file_id, mimeType=export_mime_type
            )
        else:
            request = self._service.files().get_media(fileId=file_id)

        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        return buf.getvalue(), filename

    # ------------------------------------------------------------------
    # コンテンツ → FinancialData
    # ------------------------------------------------------------------

    def _analyze_content(
        self,
        content: bytes,
        filename: str,
        company_name: str,
        period: str,
        unit: float,
        sheet_name: Optional[str],
    ) -> FinancialData:
        """バイトコンテンツを一時ファイルに書き出してローダーに渡す"""
        suffix = Path(filename).suffix.lower()
        if not suffix or suffix == ".bin":
            raise ValueError(
                f"ファイル形式を判定できませんでした: {filename}\n"
                "対応形式: .pdf / .xlsx / .xls / .docx"
            )

        # 一時ファイルに書き出して既存ローダーに渡す
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            print(f"ダウンロード完了: {filename} ({len(content):,} bytes)")
            return load_financial_data(
                tmp_path,
                company_name=company_name,
                period=period,
                unit=unit,
                sheet_name=sheet_name,
            )
        finally:
            os.unlink(tmp_path)
