"""
QRMaster Pro — API Dependencies & Authentication.

Provides:
- Header authentication for developer API keys (`X-API-Key`).
- Supabase JWT Bearer token authentication (`Authorization: Bearer <token>`).
- Multi-tenant workspace scoping (`X-Workspace-Id`).
- Role-based access control (RBAC) verification (`Owner`, `Admin`, `Editor`, `Viewer`).
"""
from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.models import APIKey, Workspace, WorkspaceMember
from app.utils.jwt_auth import decode_jwt_token
from app.utils.logger import logger

LEGACY_DEFAULT_USER = {
    "id": "usr_legacy_default",
    "email": "admin@qrmaster.local",
    "role": "authenticated",
}

LEGACY_DEFAULT_WORKSPACE = "ws_legacy_default"


def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key", description="Developer API Key (qrm_live_...)"),
    db: Session = Depends(get_db),
) -> APIKey:
    """
    FastAPI dependency to enforce API key authentication on protected endpoints.
    Verifies key format, hashed secret match, and active status.
    Updates last_used_at timestamp.
    """
    if not x_api_key or not x_api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required 'X-API-Key' header",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    clean_key = x_api_key.strip()
    key_hash = hashlib.sha256(clean_key.encode("utf-8")).hexdigest()

    key_record = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    if not key_record:
        logger.warning("Rejected API request: Invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not key_record.is_active:
        logger.warning(f"Rejected API request: Revoked API key '{key_record.key_prefix}...'")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key has been revoked or deactivated",
        )

    # Track usage
    try:
        key_record.last_used_at = datetime.now()
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning(f"Could not update last_used_at for key {key_record.id}: {exc}")

    return key_record


def require_api_key_scope(required_scope: str):
    """
    Dependency factory to enforce granular API key scope permissions.
    Grants access if key has explicit scope or 'admin'.
    """
    def _scope_checker(key_record: APIKey = Depends(verify_api_key)) -> APIKey:
        scopes_str = getattr(key_record, "scopes", "qr:read,qr:write,analytics:read") or ""
        assigned_scopes = [s.strip().lower() for s in scopes_str.split(",") if s.strip()]
        if "admin" in assigned_scopes or required_scope.lower() in assigned_scopes:
            return key_record

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"API key missing required scope '{required_scope}'. Granted scopes: {assigned_scopes}",
        )

    return _scope_checker


def get_current_user(
    authorization: Optional[str] = Header(None, description="Bearer <jwt_token>"),
) -> Dict[str, Any]:
    """
    FastAPI dependency to extract and verify the authenticated Supabase user.
    Falls back gracefully to legacy default user for backward compatibility
    and local tests when no Authorization header is provided.
    """
    if not authorization or not authorization.strip():
        return LEGACY_DEFAULT_USER

    token = authorization.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    secret = settings.SUPABASE_JWT_SECRET
    # Decode token (verifies signature if secret is configured)
    payload = decode_jwt_token(
        token,
        secret=secret,
        verify_signature=bool(secret),
        verify_exp=True,
    )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub") or payload.get("user_id") or "usr_authenticated"
    email = payload.get("email", "")
    role = payload.get("role", "authenticated")

    return {
        "id": str(user_id),
        "email": str(email),
        "role": str(role),
        "payload": payload,
    }


def get_current_workspace(
    x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-Id", description="Target Workspace ID"),
    workspace_id: Optional[str] = Query(None, description="Target Workspace ID Query Param"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> str:
    """
    FastAPI dependency to resolve the active tenant workspace ID.
    Defaults to 'ws_legacy_default' if not specified.
    """
    target_id = x_workspace_id or workspace_id or LEGACY_DEFAULT_WORKSPACE
    target_id = target_id.strip()

    if target_id == LEGACY_DEFAULT_WORKSPACE:
        return LEGACY_DEFAULT_WORKSPACE

    # Verify workspace exists and user has membership or is owner
    ws = db.query(Workspace).filter(Workspace.id == target_id, Workspace.is_active == True).first()
    if not ws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{target_id}' not found or inactive",
        )

    user_id = current_user.get("id")
    if user_id == ws.owner_id:
        return target_id

    member = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == target_id, WorkspaceMember.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this workspace",
        )

    return target_id


def require_role(allowed_roles: List[str]):
    """
    Role-Based Access Control (RBAC) dependency factory.
    Verifies that the current user has one of the allowed roles within the active workspace.
    """
    def _role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
        workspace_id: str = Depends(get_current_workspace),
        db: Session = Depends(get_db),
    ) -> str:
        user_id = current_user.get("id")

        if workspace_id == LEGACY_DEFAULT_WORKSPACE or user_id == "usr_legacy_default":
            return "owner"

        ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not ws:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

        if ws.owner_id == user_id:
            return "owner"

        member = (
            db.query(WorkspaceMember)
            .filter(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == user_id)
            .first()
        )
        if not member:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        clean_roles = [r.lower() for r in allowed_roles]
        if member.role.lower() not in clean_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: requires {allowed_roles}, but user is '{member.role}'",
            )

        return member.role

    return _role_checker
