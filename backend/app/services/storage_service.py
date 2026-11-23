"""
QRMaster Pro — Storage Service.

Provides unified file persistence supporting local disk storage and Supabase Object Storage.
Safely stores relative paths in database records rather than machine-local absolute paths.
"""
from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Optional, Set
import httpx

from app.config import settings
from app.utils.logger import logger


# Maximum allowed upload file size: 15 MB
MAX_UPLOAD_SIZE = 15 * 1024 * 1024

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg", ".svg", ".webp"}
ALLOWED_IMPORT_EXTENSIONS: Set[str] = {".csv", ".xlsx", ".xls"}


class StorageService:
    """Service abstraction for persistent file storage."""

    def __init__(self) -> None:
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY
        self.default_bucket = settings.SUPABASE_STORAGE_BUCKET

    @property
    def is_supabase_configured(self) -> bool:
        """Check if Supabase Storage credentials are present."""
        return bool(self.supabase_url and self.supabase_key)

    def validate_file(
        self,
        filename: str,
        size_bytes: int,
        allowed_extensions: Optional[Set[str]] = None,
        max_bytes: int = MAX_UPLOAD_SIZE,
    ) -> None:
        """Validate filename extension and file size."""
        if size_bytes > max_bytes:
            raise ValueError(f"File size ({size_bytes} bytes) exceeds limit of {max_bytes} bytes.")

        ext = Path(filename).suffix.lower()
        if allowed_extensions and ext not in allowed_extensions:
            raise ValueError(f"File extension '{ext}' is not permitted. Allowed: {', '.join(allowed_extensions)}")

    def save_asset(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str] = None,
        bucket: str = "qr-assets",
    ) -> str:
        """
        Save an asset to Supabase Storage (if configured) or local generated_qr directory.
        Returns the relative storage path or remote object key.
        """
        if not content_type:
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        if self.is_supabase_configured:
            remote_key = f"{bucket}/{filename}"
            try:
                upload_url = f"{self.supabase_url.rstrip('/')}/storage/v1/object/{bucket}/{filename}"
                headers = {
                    "Authorization": f"Bearer {self.supabase_key}",
                    "apikey": self.supabase_key,
                    "Content-Type": content_type,
                    "x-upsert": "true",
                }
                with httpx.Client(timeout=30.0) as client:
                    resp = client.post(upload_url, content=file_bytes, headers=headers)
                    if resp.status_code in (200, 201):
                        logger.info(f"Uploaded asset to Supabase Storage: {remote_key}")
                        return remote_key
                    logger.warning(f"Supabase upload returned {resp.status_code}: {resp.text}")
            except Exception as exc:
                logger.error(f"Supabase storage upload failed, falling back to local: {exc}")

        # Local filesystem fallback
        local_path = settings.generated_qr_path / filename
        local_path.write_bytes(file_bytes)
        return filename

    def read_asset(self, path_or_key: str, bucket: str = "qr-assets") -> Optional[bytes]:
        """Read asset bytes from remote or local storage."""
        if path_or_key.startswith(f"{bucket}/") and self.is_supabase_configured:
            remote_name = path_or_key[len(f"{bucket}/"):]
            try:
                download_url = f"{self.supabase_url.rstrip('/')}/storage/v1/object/authenticated/{bucket}/{remote_name}"
                headers = {
                    "Authorization": f"Bearer {self.supabase_key}",
                    "apikey": self.supabase_key,
                }
                with httpx.Client(timeout=30.0) as client:
                    resp = client.get(download_url, headers=headers)
                    if resp.status_code == 200:
                        return resp.content
            except Exception as exc:
                logger.warning(f"Could not read from Supabase Storage: {exc}")

        # Check local paths
        candidates = [
            Path(path_or_key),
            settings.generated_qr_path / path_or_key,
            settings.exports_path / path_or_key,
        ]
        for p in candidates:
            if p.exists() and p.is_file():
                return p.read_bytes()

        return None

    def delete_asset(self, path_or_key: str, bucket: str = "qr-assets") -> bool:
        """Delete asset from remote or local storage."""
        if path_or_key.startswith(f"{bucket}/") and self.is_supabase_configured:
            remote_name = path_or_key[len(f"{bucket}/"):]
            try:
                url = f"{self.supabase_url.rstrip('/')}/storage/v1/object/{bucket}"
                headers = {
                    "Authorization": f"Bearer {self.supabase_key}",
                    "apikey": self.supabase_key,
                }
                with httpx.Client(timeout=30.0) as client:
                    client.request("DELETE", url, json={"prefixes": [remote_name]}, headers=headers)
            except Exception as exc:
                logger.warning(f"Could not delete remote object: {exc}")

        candidates = [
            Path(path_or_key),
            settings.generated_qr_path / path_or_key,
            settings.exports_path / path_or_key,
        ]
        for p in candidates:
            if p.exists() and p.is_file():
                try:
                    p.unlink()
                    return True
                except Exception:
                    pass
        return False


# Singleton instance
storage_service = StorageService()
