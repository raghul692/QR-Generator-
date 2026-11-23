"""
QRMaster Pro — Landing Page API Router.

Endpoints for managing mobile-first landing pages (CRUD under /api/v1/landing-pages)
and public mobile landing page rendering under /p/{slug}.
"""
from __future__ import annotations

import json
import re
import secrets
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import LandingPage
from app.schemas import (
    LandingPageCreate,
    LandingPageOut,
    LandingPageUpdate,
    MessageResponse,
)

router = APIRouter(prefix="/landing-pages", tags=["Landing Pages"])
public_router = APIRouter(tags=["Landing Pages Public"])


def _slugify(text: str) -> str:
    """Generate a clean URL slug from title."""
    clean = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    slug_base = re.sub(r"[\s-]+", "-", clean)
    if not slug_base:
        slug_base = "page"
    return f"{slug_base[:60]}-{secrets.token_hex(3)}"


def _render_landing_html(page: LandingPage) -> str:
    """Render a modern, responsive mobile landing page."""
    social_links: List[Dict[str, Any]] = []
    if page.social_links_json:
        try:
            social_links = json.loads(page.social_links_json)
        except Exception:
            social_links = []

    social_buttons_html = ""
    for s in social_links:
        label = s.get("label") or s.get("platform") or "Link"
        url = s.get("url", "#")
        social_buttons_html += f"""
        <a href="{url}" target="_blank" rel="noopener noreferrer" class="link-btn secondary">
            <span>{label}</span> &rarr;
        </a>
        """

    action_btn_html = ""
    if page.button_text and page.button_url:
        action_btn_html = f"""
        <a href="{page.button_url}" target="_blank" rel="noopener noreferrer" class="link-btn primary">
            {page.button_text}
        </a>
        """

    theme_bg = "#0f172a" if page.theme == "dark" else "#f8fafc"
    card_bg = "#1e293b" if page.theme == "dark" else "#ffffff"
    text_color = "#f8fafc" if page.theme == "dark" else "#0f172a"
    sub_color = "#94a3b8" if page.theme == "dark" else "#64748b"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page.title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: {theme_bg};
            color: {text_color};
            display: flex;
            justify-content: center;
            min-height: 100vh;
            padding: 2rem 1rem;
        }}
        .container {{
            width: 100%;
            max-width: 480px;
            background: {card_bg};
            border-radius: 1.5rem;
            padding: 2.5rem 1.75rem;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            text-align: center;
            height: fit-content;
        }}
        .avatar {{
            width: 80px;
            height: 80px;
            background: #2563eb;
            color: white;
            border-radius: 50%;
            display: grid;
            place-items: center;
            font-size: 2rem;
            font-weight: 700;
            margin: 0 auto 1.25rem;
        }}
        h1 {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .headline {{ font-size: 1rem; font-weight: 500; color: #2563eb; margin-bottom: 0.75rem; }}
        .desc {{ font-size: 0.95rem; color: {sub_color}; line-height: 1.5; margin-bottom: 1.75rem; }}
        .link-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 0.875rem 1.25rem;
            border-radius: 0.75rem;
            text-decoration: none;
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.75rem;
            transition: transform 0.15s ease, opacity 0.15s ease;
        }}
        .link-btn:active {{ transform: scale(0.98); }}
        .link-btn.primary {{
            background: #2563eb;
            color: #ffffff;
        }}
        .link-btn.secondary {{
            background: rgba(37, 99, 235, 0.1);
            color: #2563eb;
            border: 1px solid rgba(37, 99, 235, 0.2);
            justify-content: space-between;
        }}
        .footer {{ margin-top: 2rem; font-size: 0.75rem; color: {sub_color}; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="avatar">{page.title[:1].upper()}</div>
        <h1>{page.title}</h1>
        {f'<p class="headline">{page.headline}</p>' if page.headline else ''}
        {f'<p class="desc">{page.description}</p>' if page.description else ''}
        {action_btn_html}
        {social_buttons_html}
        <div class="footer">Powered by QRMaster Pro</div>
    </div>
</body>
</html>"""


def _serve_page(page: LandingPage, request: Request):
    """Serve either JSON or rendered HTML based on request headers/params."""
    accept_header = request.headers.get("accept", "").lower()
    is_json = "application/json" in accept_header or request.query_params.get("format") == "json"
    if is_json:
        return {
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "theme": page.theme,
            "headline": page.headline,
            "description": page.description,
            "button_text": page.button_text,
            "button_url": page.button_url,
            "social_links_json": page.social_links_json,
            "is_published": page.is_published,
            "created_at": page.created_at.isoformat() if page.created_at else None,
        }
    return HTMLResponse(content=_render_landing_html(page), status_code=200)


# --------------------------------------------------------------------------- #
#  CRUD Endpoints (/api/v1/landing-pages)
# --------------------------------------------------------------------------- #
@router.get("", response_model=List[LandingPageOut])
def list_landing_pages(
    is_published: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List all landing pages."""
    query = db.query(LandingPage)
    if is_published is not None:
        query = query.filter(LandingPage.is_published == is_published)
    return query.order_by(LandingPage.created_at.desc()).all()


@router.post("", response_model=LandingPageOut, status_code=status.HTTP_201_CREATED)
def create_landing_page(
    req: LandingPageCreate,
    db: Session = Depends(get_db),
):
    """Create a new mobile landing page."""
    slug = req.slug.strip() if req.slug else _slugify(req.title)
    existing = db.query(LandingPage).filter(LandingPage.slug == slug).first()
    if existing:
        slug = f"{slug}-{secrets.token_hex(2)}"

    social_json = req.social_links_json
    if req.social_links is not None:
        social_json = json.dumps(req.social_links)

    page = LandingPage(
        title=req.title.strip(),
        slug=slug,
        theme=req.theme or "default",
        headline=req.headline.strip() if req.headline else None,
        description=req.description.strip() if req.description else None,
        button_text=req.button_text.strip() if req.button_text else None,
        button_url=req.button_url.strip() if req.button_url else None,
        social_links_json=social_json,
        is_published=req.is_published,
    )
    db.add(page)
    db.commit()
    db.refresh(page)
    return page


@router.get("/{page_id}", response_model=LandingPageOut)
def get_landing_page(page_id: int, db: Session = Depends(get_db)):
    """Get a landing page by primary key ID."""
    page = db.query(LandingPage).filter(LandingPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing page not found")
    return page


@router.put("/{page_id}", response_model=LandingPageOut)
def update_landing_page(
    page_id: int,
    req: LandingPageUpdate,
    db: Session = Depends(get_db),
):
    """Update a landing page."""
    page = db.query(LandingPage).filter(LandingPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing page not found")

    if req.title is not None:
        page.title = req.title.strip()
    if req.slug is not None:
        page.slug = req.slug.strip()
    if req.theme is not None:
        page.theme = req.theme
    if req.headline is not None:
        page.headline = req.headline.strip() if req.headline else None
    if req.description is not None:
        page.description = req.description.strip() if req.description else None
    if req.button_text is not None:
        page.button_text = req.button_text.strip() if req.button_text else None
    if req.button_url is not None:
        page.button_url = req.button_url.strip() if req.button_url else None
    if req.social_links is not None:
        page.social_links_json = json.dumps(req.social_links)
    elif req.social_links_json is not None:
        page.social_links_json = req.social_links_json
    if req.is_published is not None:
        page.is_published = req.is_published

    db.commit()
    db.refresh(page)
    return page


@router.delete("/{page_id}", response_model=MessageResponse)
def delete_landing_page(page_id: int, db: Session = Depends(get_db)):
    """Delete a landing page."""
    page = db.query(LandingPage).filter(LandingPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing page not found")
    db.delete(page)
    db.commit()
    return MessageResponse(message="Landing page deleted successfully")


# --------------------------------------------------------------------------- #
#  Public Endpoints (/p/{slug})
# --------------------------------------------------------------------------- #
@router.get("/p/{slug}")
def get_landing_page_public_prefixed(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Public landing page accessor under /api/v1/landing-pages/p/{slug}."""
    page = db.query(LandingPage).filter(LandingPage.slug == slug, LandingPage.is_published == True).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing page not found or unpublished")
    return _serve_page(page, request)


@public_router.get("/p/{slug}")
def get_landing_page_public_root(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Public landing page endpoint mounted at root /p/{slug}."""
    page = db.query(LandingPage).filter(LandingPage.slug == slug, LandingPage.is_published == True).first()
    if not page:
        raise HTTPException(status_code=404, detail="Landing page not found or unpublished")
    return _serve_page(page, request)
