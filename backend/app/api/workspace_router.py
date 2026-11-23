"""
QRMaster Pro — Team Workspaces & RBAC API Router.

Endpoints for managing multi-tenant workspaces, membership rosters,
and role-based permissions (Owner, Admin, Editor, Viewer).
"""
from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import (
    LEGACY_DEFAULT_WORKSPACE,
    get_current_user,
    get_current_workspace,
)
from app.database.session import get_db
from app.models import Workspace, WorkspaceMember

router = APIRouter(prefix="/workspaces", tags=["Workspaces & RBAC"])

VALID_ROLES = {"owner", "admin", "editor", "viewer"}


# ---- Pydantic Schemas ----
class WorkspaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=100)
    plan: str = Field(default="enterprise", max_length=50)


class WorkspaceUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    plan: Optional[str] = Field(None, max_length=50)


class MemberAddRequest(BaseModel):
    user_id: str = Field(..., min_length=2, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    role: str = Field(default="member")


class MemberUpdateRoleRequest(BaseModel):
    role: str = Field(...)


def _slugify(text: str) -> str:
    """Generate a clean URL slug from text."""
    slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", slug)


def _check_admin_permission(ws: Workspace, user_id: str, db: Session) -> bool:
    """Check if user is owner or admin of the workspace."""
    if ws.owner_id == user_id or user_id == "usr_legacy_default":
        return True
    member = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == ws.id, WorkspaceMember.user_id == user_id)
        .first()
    )
    if not member:
        return False
    return member.role.lower() in {"owner", "admin"}


@router.get("")
def list_user_workspaces(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all workspaces the current user has access to."""
    user_id = current_user.get("id")

    # Ensure legacy default workspace exists idempotently
    legacy_ws = db.query(Workspace).filter(Workspace.id == LEGACY_DEFAULT_WORKSPACE).first()
    if not legacy_ws:
        legacy_ws = Workspace(
            id=LEGACY_DEFAULT_WORKSPACE,
            name="Default Workspace",
            slug="default-workspace",
            owner_id="usr_legacy_default",
            plan="enterprise",
            is_active=True,
        )
        db.add(legacy_ws)
        db.commit()

    # Fetch memberships
    memberships = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.user_id == user_id)
        .all()
    )
    member_ws_ids = {m.workspace_id for m in memberships}

    # Fetch owned or member workspaces, plus legacy default
    workspaces = (
        db.query(Workspace)
        .filter(
            (Workspace.owner_id == user_id)
            | (Workspace.id.in_(member_ws_ids))
            | (Workspace.id == LEGACY_DEFAULT_WORKSPACE)
        )
        .all()
    )

    role_map = {m.workspace_id: m.role for m in memberships}

    results = []
    for w in workspaces:
        user_role = "owner" if w.owner_id == user_id else role_map.get(w.id, "viewer")
        results.append({
            "id": w.id,
            "name": w.name,
            "slug": w.slug,
            "owner_id": w.owner_id,
            "plan": w.plan,
            "is_active": w.is_active,
            "role": user_role,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        })

    return {"workspaces": results, "total": len(results)}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_workspace(
    data: WorkspaceCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new tenant workspace and assign current user as Owner."""
    user_id = current_user.get("id", "usr_legacy_default")
    user_email = current_user.get("email", "")

    slug_val = _slugify(data.slug if data.slug else data.name)
    existing = db.query(Workspace).filter(Workspace.slug == slug_val).first()
    if existing:
        slug_val = f"{slug_val}-{uuid.uuid4().hex[:6]}"

    ws_id = f"ws_{uuid.uuid4().hex[:12]}"
    workspace = Workspace(
        id=ws_id,
        name=data.name.strip(),
        slug=slug_val,
        owner_id=user_id,
        plan=data.plan,
        is_active=True,
    )
    db.add(workspace)

    # Add owner to membership roster
    member = WorkspaceMember(
        workspace_id=ws_id,
        user_id=user_id,
        email=user_email,
        role="owner",
    )
    db.add(member)
    db.commit()
    db.refresh(workspace)

    return {
        "status": "success",
        "workspace": {
            "id": workspace.id,
            "name": workspace.name,
            "slug": workspace.slug,
            "owner_id": workspace.owner_id,
            "plan": workspace.plan,
            "role": "owner",
        },
    }


@router.get("/{workspace_id}")
def get_workspace_details(
    workspace_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed workspace information including member roster."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    user_id = current_user.get("id")
    has_perm = _check_admin_permission(ws, user_id, db)
    # Also allow if member
    is_member = (
        has_perm
        or db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == ws.id, WorkspaceMember.user_id == user_id)
        .first()
        is not None
        or workspace_id == LEGACY_DEFAULT_WORKSPACE
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="Access denied to this workspace")

    members = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id).all()
    member_list = [
        {
            "id": m.id,
            "user_id": m.user_id,
            "email": m.email,
            "role": m.role,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in members
    ]

    return {
        "id": ws.id,
        "name": ws.name,
        "slug": ws.slug,
        "owner_id": ws.owner_id,
        "plan": ws.plan,
        "is_active": ws.is_active,
        "members": member_list,
        "members_count": len(member_list),
    }


@router.put("/{workspace_id}")
def update_workspace(
    workspace_id: str,
    data: WorkspaceUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update workspace name or plan (Owner or Admin only)."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    user_id = current_user.get("id")
    if not _check_admin_permission(ws, user_id, db):
        raise HTTPException(status_code=403, detail="Only workspace Owners or Admins can modify settings")

    if data.name:
        ws.name = data.name.strip()
    if data.plan:
        ws.plan = data.plan.strip()

    db.commit()
    db.refresh(ws)
    return {"status": "success", "workspace": {"id": ws.id, "name": ws.name, "plan": ws.plan}}


@router.delete("/{workspace_id}")
def delete_workspace(
    workspace_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a workspace (Owner only). Legacy default workspace is protected."""
    if workspace_id == LEGACY_DEFAULT_WORKSPACE:
        raise HTTPException(status_code=400, detail="Cannot delete legacy default workspace")

    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    user_id = current_user.get("id")
    if ws.owner_id != user_id and user_id != "usr_legacy_default":
        raise HTTPException(status_code=403, detail="Only the workspace Owner can delete this workspace")

    db.delete(ws)
    db.commit()
    return {"status": "success", "message": f"Workspace '{workspace_id}' deleted successfully"}


@router.get("/{workspace_id}/members")
def list_workspace_members(
    workspace_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List members of a workspace."""
    members = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id).all()
    return {
        "members": [
            {
                "id": m.id,
                "user_id": m.user_id,
                "email": m.email,
                "role": m.role,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in members
        ],
        "total": len(members),
    }


@router.post("/{workspace_id}/members", status_code=status.HTTP_201_CREATED)
def add_workspace_member(
    workspace_id: str,
    data: MemberAddRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Invite or add a user to the workspace with specified role (Admin/Owner only)."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    user_id = current_user.get("id")
    if not _check_admin_permission(ws, user_id, db):
        raise HTTPException(status_code=403, detail="Only workspace Owners or Admins can add members")

    clean_role = data.role.strip().lower()
    if clean_role not in VALID_ROLES:
        clean_role = "viewer"

    existing = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == data.user_id)
        .first()
    )
    if existing:
        existing.role = clean_role
        if data.email:
            existing.email = data.email
        db.commit()
        return {"status": "success", "message": "Member role updated", "member_id": existing.id}

    new_member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=data.user_id.strip(),
        email=data.email.strip() if data.email else None,
        role=clean_role,
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return {
        "status": "success",
        "member": {
            "id": new_member.id,
            "workspace_id": new_member.workspace_id,
            "user_id": new_member.user_id,
            "email": new_member.email,
            "role": new_member.role,
        },
    }


@router.patch("/{workspace_id}/members/{target_user_id}")
def update_workspace_member_role(
    workspace_id: str,
    target_user_id: str,
    data: MemberUpdateRoleRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change role of a workspace member (Admin/Owner only)."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    user_id = current_user.get("id")
    if not _check_admin_permission(ws, user_id, db):
        raise HTTPException(status_code=403, detail="Only workspace Owners or Admins can modify member roles")

    clean_role = data.role.strip().lower()
    if clean_role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {VALID_ROLES}")

    member = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == target_user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found in workspace")

    member.role = clean_role
    db.commit()
    return {"status": "success", "member_id": member.id, "new_role": clean_role}


@router.delete("/{workspace_id}/members/{target_user_id}")
def remove_workspace_member(
    workspace_id: str,
    target_user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a member from the workspace (Admin/Owner only). Cannot remove workspace owner."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if ws.owner_id == target_user_id:
        raise HTTPException(status_code=400, detail="Cannot remove the workspace owner")

    user_id = current_user.get("id")
    if not _check_admin_permission(ws, user_id, db):
        raise HTTPException(status_code=403, detail="Only workspace Owners or Admins can remove members")

    member = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == target_user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    db.delete(member)
    db.commit()
    return {"status": "success", "message": f"User '{target_user_id}' removed from workspace"}
