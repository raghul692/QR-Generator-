"""
QRMaster Pro — Public Dynamic QR Redirection Endpoint.

Handles GET /r/{short_code} for real-time redirection, password verification,
expiration handling, and scan analytics recording.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Form, Header, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.dynamic_qr_service import dynamic_qr_service

router = APIRouter(tags=["Dynamic QR Redirection"])


@router.get("/r/{short_code}")
def redirect_dynamic_qr(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db),
    user_agent: Optional[str] = Header(None),
    referer: Optional[str] = Header(None),
):
    """Handle public scan of dynamic QR code."""
    dyn = dynamic_qr_service.get_by_code(db, short_code)
    if not dyn:
        return HTMLResponse(
            status_code=404,
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>QR Code Not Found</title><meta name="viewport" content="width=device-width, initial-scale=1">
            <style>body{font-family:system-ui;display:grid;place-items:center;height:100vh;background:#f3f4f6;margin:0;padding:1rem;}
            .card{background:white;padding:2.5rem;border-radius:1rem;box-shadow:0 10px 25px rgba(0,0,0,0.1);text-align:center;max-width:400px;}
            h1{color:#ef4444;margin-bottom:0.5rem;}p{color:#4b5563;}</style>
            </head>
            <body>
                <div class="card">
                    <h1>404 — Not Found</h1>
                    <p>The requested QR code does not exist or has been removed.</p>
                </div>
            </body>
            </html>
            """,
        )

    if not dyn.is_active or dynamic_qr_service.is_expired(dyn):
        return HTMLResponse(
            status_code=410,
            content=f"""
            <!DOCTYPE html>
            <html>
            <head><title>QR Code Expired</title><meta name="viewport" content="width=device-width, initial-scale=1">
            <style>body{{font-family:system-ui;display:grid;place-items:center;height:100vh;background:#f3f4f6;margin:0;padding:1rem;}}
            .card{{background:white;padding:2.5rem;border-radius:1rem;box-shadow:0 10px 25px rgba(0,0,0,0.1);text-align:center;max-width:400px;}}
            h1{{color:#f59e0b;margin-bottom:0.5rem;}}p{{color:#4b5563;}}</style>
            </head>
            <body>
                <div class="card">
                    <h1>QR Code Inactive / Expired</h1>
                    <p>The QR code <strong>"{dyn.title}"</strong> has expired or is currently inactive.</p>
                </div>
            </body>
            </html>
            """,
        )

    # Password protection check
    if dyn.password_hash:
        return HTMLResponse(
            status_code=200,
            content=f"""
            <!DOCTYPE html>
            <html>
            <head><title>Protected QR Code</title><meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: system-ui, -apple-system, sans-serif; display: grid; place-items: center; height: 100vh; background: #0f172a; color: white; margin: 0; padding: 1rem; }}
                .card {{ background: #1e293b; padding: 2.5rem; border-radius: 1rem; border: 1px solid #334155; text-align: center; max-width: 380px; width: 100%; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }}
                h2 {{ color: #38bdf8; margin-top: 0; }}
                p {{ color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.5rem; }}
                input {{ width: 100%; padding: 0.8rem 1rem; border-radius: 0.5rem; border: 1px solid #475569; background: #0f172a; color: white; margin-bottom: 1rem; box-sizing: border-box; font-size: 1rem; }}
                button {{ width: 100%; padding: 0.85rem; border-radius: 0.5rem; border: none; background: #4f46e5; color: white; font-weight: 600; font-size: 1rem; cursor: pointer; transition: background 0.2s; }}
                button:hover {{ background: #4338ca; }}
            </style>
            </head>
            <body>
                <div class="card">
                    <h2>🔒 Password Protected</h2>
                    <p>Enter the password to access <strong>{dyn.title}</strong></p>
                    <form action="/r/{short_code}/unlock" method="POST">
                        <input type="password" name="password" placeholder="Enter password" required autofocus />
                        <button type="submit">Unlock & Continue &rarr;</button>
                    </form>
                </div>
            </body>
            </html>
            """,
        )

    # Log scan
    ip = request.client.host if request.client else None
    dynamic_qr_service.log_scan(db, dyn, ip_address=ip, user_agent_str=user_agent, referer=referer)

    return RedirectResponse(url=dyn.target_url, status_code=307)


@router.post("/r/{short_code}/unlock")
def unlock_dynamic_qr(
    short_code: str,
    request: Request,
    password: str = Form(...),
    db: Session = Depends(get_db),
    user_agent: Optional[str] = Header(None),
    referer: Optional[str] = Header(None),
):
    """Handle password submission for protected dynamic QR."""
    dyn = dynamic_qr_service.get_by_code(db, short_code)
    if not dyn or not dyn.is_active or dynamic_qr_service.is_expired(dyn):
        return HTMLResponse("Invalid or Expired QR Code", status_code=400)

    if not dynamic_qr_service.verify_password(dyn, password):
        return HTMLResponse(
            status_code=401,
            content=f"""
            <!DOCTYPE html>
            <html>
            <head><title>Access Denied</title><meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: system-ui; display: grid; place-items: center; height: 100vh; background: #0f172a; color: white; margin: 0; }}
                .card {{ background: #1e293b; padding: 2rem; border-radius: 1rem; text-align: center; max-width: 360px; }}
                h2 {{ color: #ef4444; }} a {{ color: #38bdf8; text-decoration: none; font-weight: 600; }}
            </style>
            </head>
            <body>
                <div class="card">
                    <h2>❌ Incorrect Password</h2>
                    <p>The password you entered is incorrect.</p>
                    <p><a href="/r/{short_code}">&larr; Try Again</a></p>
                </div>
            </body>
            </html>
            """,
        )

    # Log scan
    ip = request.client.host if request.client else None
    dynamic_qr_service.log_scan(db, dyn, ip_address=ip, user_agent_str=user_agent, referer=referer)

    return RedirectResponse(url=dyn.target_url, status_code=307)
