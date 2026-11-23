"""
QRMaster Pro — QR Design Templates API Router.

Endpoints for retrieving built-in design presets and managing custom templates.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import QRTemplate
from app.utils.logger import logger

router = APIRouter(prefix="/templates", tags=["QR Templates"])


class CreateTemplateRequest(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    config: Dict[str, Any] = Field(..., description="QRCustomization options dictionary")


@router.get("", response_model=List[Dict[str, Any]], summary="List all design templates")
def list_templates(db: Session = Depends(get_db)):
    """Return all available design templates (built-in presets and user templates)."""
    templates = db.query(QRTemplate).order_by(QRTemplate.is_builtin.desc(), QRTemplate.id.asc()).all()
    results = []
    for t in templates:
        try:
            cfg = json.loads(t.config_json)
        except Exception:
            cfg = {}
        results.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "is_builtin": t.is_builtin,
            "config": cfg,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        })
    return results


@router.get("/{template_id}", response_model=Dict[str, Any], summary="Get template by ID")
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Return a single template by ID."""
    t = db.query(QRTemplate).filter(QRTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
    try:
        cfg = json.loads(t.config_json)
    except Exception:
        cfg = {}
    return {
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "is_builtin": t.is_builtin,
        "config": cfg,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED, summary="Create a custom template")
def create_template(req: CreateTemplateRequest, db: Session = Depends(get_db)):
    """Save current customization as a reusable template."""
    existing = db.query(QRTemplate).filter(QRTemplate.name == req.name.strip()).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"A template named '{req.name}' already exists.")

    tmpl = QRTemplate(
        name=req.name.strip(),
        description=req.description.strip() if req.description else None,
        config_json=json.dumps(req.config, ensure_ascii=False),
        is_builtin=False,
    )
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    logger.info(f"Created custom template id={tmpl.id}, name={tmpl.name}")
    return {
        "id": tmpl.id,
        "name": tmpl.name,
        "description": tmpl.description,
        "is_builtin": tmpl.is_builtin,
        "config": req.config,
        "created_at": tmpl.created_at.isoformat() if tmpl.created_at else None,
    }


@router.delete("/{template_id}", response_model=Dict[str, str], summary="Delete a custom template")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a custom template. Built-in templates cannot be deleted."""
    t = db.query(QRTemplate).filter(QRTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    if t.is_builtin:
        raise HTTPException(status_code=400, detail="Built-in system templates cannot be deleted.")

    db.delete(t)
    db.commit()
    logger.info(f"Deleted custom template id={template_id}")
    return {"message": f"Template {template_id} deleted successfully"}
