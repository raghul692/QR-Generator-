"""
QRMaster Pro — Authentication API Router.

Provides real production authentication:
- Registration with Argon2id password hashing and personal workspace auto-provisioning
- Login with password verification and signed JWT token issuance
- Enterprise demo 1-click logins for evaluated roles (Admin, Marketing, Auditor)
- Session profile verification (`/me`) with workspace roster introspection
"""
from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import (
    LEGACY_DEFAULT_WORKSPACE,
    get_current_user,
    get_current_workspace,
)
from app.config import settings
from app.database.session import get_db
from app.models import QRMasterUser, Workspace, WorkspaceMember
from app.utils.jwt_auth import create_jwt_token
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["Authentication & Identity"])

_password_hasher = PasswordHasher()

DEMO_ACCOUNTS = {
    "admin": {
        "id": "usr_enterprise_admin",
        "email": "admin@enterprise.qrmaster.pro",
        "name": "Enterprise Admin",
        "role": "owner",
        "workspace_id": "ws_enterprise_corp",
        "workspace_name": "Enterprise Global HQ",
    },
    "marketing": {
        "id": "usr_marketing_lead",
        "email": "marketing@enterprise.qrmaster.pro",
        "name": "Marketing Lead",
        "role": "editor",
        "workspace_id": "ws_marketing_team",
        "workspace_name": "Global Growth & Marketing",
    },
    "auditor": {
        "id": "usr_security_auditor",
        "email": "compliance@enterprise.qrmaster.pro",
        "name": "Security Auditor",
        "role": "viewer",
        "workspace_id": "ws_compliance_audit",
        "workspace_name": "Security & Audit Governance",
    },
}


# ---- Pydantic DTOs ----
class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255, description="User email address")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: Optional[str] = Field(None, max_length=100)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str


class DemoLoginRequest(BaseModel):
    role: str = Field(default="admin", description="admin | marketing | auditor")


def _resolve_jwt_secret() -> str:
    """Resolve active signing secret or safe fallback."""
    return settings.SUPABASE_JWT_SECRET or "qrmaster-default-development-jwt-secret-key-32chars"


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", slug) or "workspace"


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register a new user account")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user, hash password with Argon2id, and provision initial workspace."""
    clean_email = req.email.strip().lower()

    # Check for existing user
    existing = db.query(QRMasterUser).filter(QRMasterUser.email == clean_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    pwd_hash = _password_hasher.hash(req.password)
    user_name = req.name.strip() if req.name else clean_email.split("@")[0].title()

    new_user = QRMasterUser(
        id=user_id,
        email=clean_email,
        password_hash=pwd_hash,
        name=user_name,
        role="authenticated",
        is_active=True,
    )
    db.add(new_user)

    # Provision personal workspace
    ws_id = f"ws_{uuid.uuid4().hex[:12]}"
    ws_name = f"{user_name}'s Workspace"
    ws_slug = f"{_slugify(user_name)}-{uuid.uuid4().hex[:4]}"

    workspace = Workspace(
        id=ws_id,
        name=ws_name,
        slug=ws_slug,
        owner_id=user_id,
        plan="enterprise",
        is_active=True,
    )
    db.add(workspace)

    member = WorkspaceMember(
        workspace_id=ws_id,
        user_id=user_id,
        email=clean_email,
        role="owner",
    )
    db.add(member)
    db.commit()

    token_payload = {
        "sub": user_id,
        "email": clean_email,
        "role": "authenticated",
        "workspace_id": ws_id,
    }
    token = create_jwt_token(token_payload, secret=_resolve_jwt_secret())
    logger.info(f"Registered new user '{clean_email}' (id={user_id}, ws={ws_id})")

    return {
        "token": token,
        "user": {
            "id": user_id,
            "email": clean_email,
            "name": user_name,
            "role": "owner",
        },
        "workspace": {
            "id": ws_id,
            "name": ws_name,
            "slug": ws_slug,
            "plan": "enterprise",
        },
    }


@router.post("/login", summary="Login with email and password")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate email and password, returning signed JWT and workspace context."""
    clean_email = req.email.strip().lower()
    user = db.query(QRMasterUser).filter(QRMasterUser.email == clean_email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        _password_hasher.verify(user.password_hash, req.password)
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    # Resolve user's workspace
    owned_ws = db.query(Workspace).filter(Workspace.owner_id == user.id, Workspace.is_active == True).first()
    active_ws_id = owned_ws.id if owned_ws else LEGACY_DEFAULT_WORKSPACE
    active_ws_name = owned_ws.name if owned_ws else "Default Workspace"
    active_ws_slug = owned_ws.slug if owned_ws else "default-workspace"

    token_payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "workspace_id": active_ws_id,
    }
    token = create_jwt_token(token_payload, secret=_resolve_jwt_secret())
    logger.info(f"User login success: {clean_email}")

    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name or clean_email.split("@")[0],
            "role": "owner" if owned_ws else "member",
        },
        "workspace": {
            "id": active_ws_id,
            "name": active_ws_name,
            "slug": active_ws_slug,
            "plan": getattr(owned_ws, "plan", "enterprise"),
        },
    }


@router.post("/demo", summary="1-click Enterprise Demo Login")
def demo_login(req: DemoLoginRequest, db: Session = Depends(get_db)):
    """Generate authenticated session for instant enterprise preview roles."""
    role_key = req.role.lower().strip()
    profile = DEMO_ACCOUNTS.get(role_key, DEMO_ACCOUNTS["admin"])

    # Ensure demo workspace exists
    ws = db.query(Workspace).filter(Workspace.id == profile["workspace_id"]).first()
    if not ws:
        ws = Workspace(
            id=profile["workspace_id"],
            name=profile["workspace_name"],
            slug=_slugify(profile["workspace_name"]),
            owner_id=profile["id"],
            plan="enterprise",
            is_active=True,
        )
        db.add(ws)
        db.commit()

    token_payload = {
        "sub": profile["id"],
        "email": profile["email"],
        "role": "authenticated",
        "workspace_id": profile["workspace_id"],
    }
    token = create_jwt_token(token_payload, secret=_resolve_jwt_secret())

    return {
        "token": token,
        "user": {
            "id": profile["id"],
            "email": profile["email"],
            "name": profile["name"],
            "role": profile["role"],
        },
        "workspace": {
            "id": ws.id,
            "name": ws.name,
            "slug": ws.slug,
            "plan": ws.plan,
        },
    }


@router.get("/me", summary="Get authenticated profile and workspace roster")
def get_me(
    current_user: Dict[str, Any] = Depends(get_current_user),
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Return user details, active workspace, and workspace memberships."""
    user_id = current_user.get("id")

    # Fetch user memberships
    memberships = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.user_id == user_id)
        .all()
    )

    available_workspaces = []
    # If legacy default user, include legacy default
    if user_id == "usr_legacy_default":
        available_workspaces.append({
            "id": LEGACY_DEFAULT_WORKSPACE,
            "name": "Default Workspace",
            "slug": "default-workspace",
            "role": "owner",
        })

    for m in memberships:
        ws = db.query(Workspace).filter(Workspace.id == m.workspace_id).first()
        if ws and ws.is_active:
            available_workspaces.append({
                "id": ws.id,
                "name": ws.name,
                "slug": ws.slug,
                "role": m.role,
            })

    # Active workspace details
    current_ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    ws_info = {
        "id": workspace_id,
        "name": current_ws.name if current_ws else "Default Workspace",
        "slug": current_ws.slug if current_ws else "default-workspace",
        "plan": getattr(current_ws, "plan", "enterprise"),
    }

    return {
        "user": {
            "id": user_id,
            "email": current_user.get("email"),
            "role": current_user.get("role", "authenticated"),
        },
        "current_workspace": ws_info,
        "workspaces": available_workspaces,
    }
