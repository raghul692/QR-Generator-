"""
QRMaster Pro — Digital Menu API Router.

Endpoints for managing digital restaurant menus (CRUD under /api/v1/menus)
and public mobile menu rendering under /m/{id}.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import DigitalMenu
from app.schemas import (
    DigitalMenuCreate,
    DigitalMenuOut,
    DigitalMenuUpdate,
    MessageResponse,
)

router = APIRouter(prefix="/menus", tags=["Digital Menus"])
public_router = APIRouter(tags=["Digital Menus Public"])


def _render_menu_html(menu: DigitalMenu) -> str:
    """Render a mobile-optimized restaurant digital menu view."""
    sections: List[Dict[str, Any]] = []
    if menu.sections_json:
        try:
            sections = json.loads(menu.sections_json)
        except Exception:
            sections = []

    sections_html = ""
    for sec in sections:
        sec_title = sec.get("title") or sec.get("name") or "Category"
        items = sec.get("items", [])
        items_html = ""
        for item in items:
            name = item.get("name", "Item")
            price = item.get("price", "")
            desc = item.get("description", "")
            tags = item.get("dietary_tags") or item.get("tags") or []
            tags_html = "".join([f'<span class="badge">{t}</span>' for t in tags])

            items_html += f"""
            <div class="menu-item">
                <div class="item-head">
                    <span class="item-name">{name}</span>
                    <span class="item-price">{menu.currency} {price}</span>
                </div>
                {f'<p class="item-desc">{desc}</p>' if desc else ''}
                {f'<div class="tags">{tags_html}</div>' if tags_html else ''}
            </div>
            """

        sections_html += f"""
        <section class="section">
            <h2 class="sec-title">{sec_title}</h2>
            {items_html}
        </section>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{menu.title} — Digital Menu</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #fdfbf7;
            color: #1c1917;
            padding: 1.5rem 1rem 3rem;
            display: flex;
            justify-content: center;
        }}
        .menu-card {{
            width: 100%;
            max-width: 500px;
        }}
        .header {{ text-align: center; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 2px dashed #e7e5e4; }}
        h1 {{ font-size: 1.75rem; font-weight: 800; color: #431407; margin-bottom: 0.5rem; }}
        .desc {{ font-size: 0.95rem; color: #78716c; }}
        .section {{ margin-bottom: 2rem; }}
        .sec-title {{
            font-size: 1.2rem;
            font-weight: 700;
            color: #b45309;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
            padding-bottom: 0.25rem;
            border-bottom: 1px solid #fed7aa;
        }}
        .menu-item {{
            background: #ffffff;
            padding: 1rem 1.25rem;
            border-radius: 0.75rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid #f5f5f4;
        }}
        .item-head {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.25rem; }}
        .item-name {{ font-size: 1.05rem; font-weight: 600; color: #1c1917; }}
        .item-price {{ font-size: 1rem; font-weight: 700; color: #b45309; }}
        .item-desc {{ font-size: 0.85rem; color: #78716c; line-height: 1.4; margin-top: 0.25rem; }}
        .tags {{ display: flex; gap: 0.4rem; margin-top: 0.5rem; flex-wrap: wrap; }}
        .badge {{ background: #fef3c7; color: #92400e; font-size: 0.7rem; font-weight: 600; padding: 0.2rem 0.5rem; border-radius: 9999px; }}
        .footer {{ text-align: center; font-size: 0.75rem; color: #a8a29e; margin-top: 2rem; }}
    </style>
</head>
<body>
    <div class="menu-card">
        <div class="header">
            <h1>{menu.title}</h1>
            {f'<p class="desc">{menu.description}</p>' if menu.description else ''}
        </div>
        {sections_html}
        <div class="footer">Digital Menu powered by QRMaster Pro</div>
    </div>
</body>
</html>"""


def _serve_menu(menu: DigitalMenu, request: Request):
    """Serve either JSON or rendered HTML based on request headers/query."""
    accept_header = request.headers.get("accept", "").lower()
    is_json = "application/json" in accept_header or request.query_params.get("format") == "json"
    if is_json:
        return {
            "id": menu.id,
            "title": menu.title,
            "description": menu.description,
            "currency": menu.currency,
            "sections_json": menu.sections_json,
            "is_active": menu.is_active,
            "created_at": menu.created_at.isoformat() if menu.created_at else None,
        }
    return HTMLResponse(content=_render_menu_html(menu), status_code=200)


# --------------------------------------------------------------------------- #
#  CRUD Endpoints (/api/v1/menus)
# --------------------------------------------------------------------------- #
@router.get("", response_model=List[DigitalMenuOut])
def list_menus(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List all digital menus."""
    query = db.query(DigitalMenu)
    if is_active is not None:
        query = query.filter(DigitalMenu.is_active == is_active)
    return query.order_by(DigitalMenu.created_at.desc()).all()


@router.post("", response_model=DigitalMenuOut, status_code=status.HTTP_201_CREATED)
def create_menu(
    req: DigitalMenuCreate,
    db: Session = Depends(get_db),
):
    """Create a new digital menu."""
    sections_json = req.sections_json
    if req.sections is not None:
        sections_json = json.dumps(req.sections)

    menu = DigitalMenu(
        title=req.title.strip(),
        description=req.description.strip() if req.description else None,
        currency=req.currency or "USD",
        sections_json=sections_json,
        is_active=req.is_active,
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


@router.get("/{menu_id}", response_model=DigitalMenuOut)
def get_menu(menu_id: int, db: Session = Depends(get_db)):
    """Get a digital menu by primary key ID."""
    menu = db.query(DigitalMenu).filter(DigitalMenu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Digital menu not found")
    return menu


@router.put("/{menu_id}", response_model=DigitalMenuOut)
def update_menu(
    menu_id: int,
    req: DigitalMenuUpdate,
    db: Session = Depends(get_db),
):
    """Update a digital menu."""
    menu = db.query(DigitalMenu).filter(DigitalMenu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Digital menu not found")

    if req.title is not None:
        menu.title = req.title.strip()
    if req.description is not None:
        menu.description = req.description.strip() if req.description else None
    if req.currency is not None:
        menu.currency = req.currency
    if req.sections is not None:
        menu.sections_json = json.dumps(req.sections)
    elif req.sections_json is not None:
        menu.sections_json = req.sections_json
    if req.is_active is not None:
        menu.is_active = req.is_active

    db.commit()
    db.refresh(menu)
    return menu


@router.delete("/{menu_id}", response_model=MessageResponse)
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    """Delete a digital menu."""
    menu = db.query(DigitalMenu).filter(DigitalMenu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Digital menu not found")
    db.delete(menu)
    db.commit()
    return MessageResponse(message="Digital menu deleted successfully")


# --------------------------------------------------------------------------- #
#  Public Endpoints (/m/{id})
# --------------------------------------------------------------------------- #
@router.get("/m/{menu_id}")
def get_menu_public_prefixed(
    menu_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Public menu accessor under /api/v1/menus/m/{id}."""
    menu = db.query(DigitalMenu).filter(DigitalMenu.id == menu_id, DigitalMenu.is_active == True).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found or inactive")
    return _serve_menu(menu, request)


@public_router.get("/m/{menu_id}")
def get_menu_public_root(
    menu_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Public menu endpoint mounted at root /m/{id}."""
    menu = db.query(DigitalMenu).filter(DigitalMenu.id == menu_id, DigitalMenu.is_active == True).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found or inactive")
    return _serve_menu(menu, request)
