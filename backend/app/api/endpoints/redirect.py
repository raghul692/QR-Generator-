"""
QRMaster Pro — Public Dynamic QR Redirection Endpoint.

Handles GET /r/{short_code} for real-time redirection, password verification,
expiration handling, max scans limit, UTM pass-through, retargeting pixel interstitials,
and scan analytics recording.
"""
from __future__ import annotations

import json
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from fastapi import APIRouter, Depends, Form, Header, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import ActivityLog, CustomDomain, DynamicQR
from app.services.dynamic_qr_service import dynamic_qr_service

router = APIRouter(tags=["Dynamic QR Redirection"])


def is_safe_redirect_url(url: str) -> bool:
    """
    Validate target redirect URL to prevent Open Redirect phishing and loopback probes.
    Enforces http/https schemes and disallows private loopback/metadata addresses.
    """
    if not url or not isinstance(url, str):
        return False
    clean = url.strip()
    if not (clean.startswith("http://") or clean.startswith("https://")):
        return False
    lower = clean.lower()
    for blocked in ["localhost", "127.0.0.1", "169.254.169.254", "0.0.0.0", "::1"]:
        if f"://{blocked}" in lower or f"@{blocked}" in lower:
            return False
    return True


def resolve_request_domain(request: Request, db: Session) -> Optional[CustomDomain]:
    """Check if incoming request host corresponds to an active verified custom branded domain."""
    host = request.headers.get("host", "").split(":")[0].strip().lower()
    if not host or host in {"localhost", "127.0.0.1", "0.0.0.0"}:
        return None
    return db.query(CustomDomain).filter(CustomDomain.domain == host, CustomDomain.status == "verified").first()


def check_max_scans_exceeded(dyn: DynamicQR, db: Session) -> bool:
    """Check if scan count has reached or exceeded max_scans limit, deactivating if reached."""
    if dyn.max_scans is not None and dyn.scan_count >= dyn.max_scans:
        if dyn.is_active:
            dyn.is_active = False
            db.commit()
        return True
    return False


def make_expired_response(title: str, reason: str = "has expired or is currently inactive") -> HTMLResponse:
    """Generate standardized HTTP 410 response for inactive/expired dynamic QR codes."""
    return HTMLResponse(
        status_code=410,
        content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>QR Code Inactive / Expired</title><meta name="viewport" content="width=device-width, initial-scale=1">
        <style>body{{font-family:system-ui;display:grid;place-items:center;height:100vh;background:#f3f4f6;margin:0;padding:1rem;}}
        .card{{background:white;padding:2.5rem;border-radius:1rem;box-shadow:0 10px 25px rgba(0,0,0,0.1);text-align:center;max-width:400px;}}
        h1{{color:#f59e0b;margin-bottom:0.5rem;}}p{{color:#4b5563;}}</style>
        </head>
        <body>
            <div class="card">
                <h1>QR Code Inactive / Expired</h1>
                <p>The QR code <strong>"{title}"</strong> {reason}.</p>
            </div>
        </body>
        </html>
        """,
    )


def append_utm_parameters(url: str, dyn: DynamicQR) -> str:
    """Append utm_source, utm_medium, utm_campaign query parameters to the target URL."""
    params: dict[str, str] = {}
    if dyn.utm_source:
        params["utm_source"] = dyn.utm_source
    if dyn.utm_medium:
        params["utm_medium"] = dyn.utm_medium
    if dyn.utm_campaign:
        params["utm_campaign"] = dyn.utm_campaign

    if not params:
        return url

    parsed = urlparse(url)
    query_dict = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query_dict.update(params)
    return urlunparse(parsed._replace(query=urlencode(query_dict)))


def build_retargeting_interstitial(destination: str, dyn: DynamicQR) -> HTMLResponse:
    """Build an interstitial HTML page executing Meta Pixel / Google Tag before redirecting."""
    meta_snippet = ""
    if dyn.meta_pixel_id:
        meta_snippet = f"""
        <script>
        !function(f,b,e,v,n,t,s)
        {{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
        n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
        if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
        n.queue=[];t=b.createElement(e);t.async=!0;
        t.src=v;s=b.getElementsByTagName(e)[0];
        s.parentNode.insertBefore(t,s)}}(window, document,'script',
        'https://connect.facebook.net/en_US/fbevents.js');
        fbq('init', '{dyn.meta_pixel_id}');
        fbq('track', 'PageView');
        </script>
        """

    google_snippet = ""
    if dyn.google_tag_id:
        google_snippet = f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={dyn.google_tag_id}"></script>
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{dyn.google_tag_id}');
        </script>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="1;url={destination}">
    <title>Redirecting...</title>
    {meta_snippet}
    {google_snippet}
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; display: grid; place-items: center; height: 100vh; background: #0f172a; color: white; margin: 0; }}
        .loader {{ border: 4px solid #1e293b; border-top: 4px solid #38bdf8; border-radius: 50%; width: 40px; height: 40px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        p {{ color: #94a3b8; font-size: 0.95rem; }}
        a {{ color: #38bdf8; text-decoration: none; }}
    </style>
</head>
<body>
    <div style="text-align: center;">
        <div class="loader"></div>
        <p>Redirecting you safely...</p>
        <p><a href="{destination}">Click here if you are not redirected automatically.</a></p>
    </div>
    <script>
        setTimeout(function() {{
            window.location.href = "{destination}";
        }}, 600);
    </script>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=200)


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

    # 1. Domain host scoping check
    matched_domain = resolve_request_domain(request, db)
    if matched_domain and dyn.workspace_id != matched_domain.workspace_id:
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
                    <p>This QR code does not belong to this custom domain.</p>
                </div>
            </body>
            </html>
            """,
        )

    # 2. Max scans limit check
    if check_max_scans_exceeded(dyn, db):
        return make_expired_response(dyn.title, "has reached its maximum scan limit")

    # 3. Expiration and active check
    if not dyn.is_active or dynamic_qr_service.is_expired(dyn):
        return make_expired_response(dyn.title)

    # 3. Password protection check
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

    # 4. Log scan
    ip = request.client.host if request.client else None
    dynamic_qr_service.log_scan(db, dyn, ip_address=ip, user_agent_str=user_agent, referer=referer)

    # Check if this scan reached max limit
    if dyn.max_scans is not None and dyn.scan_count >= dyn.max_scans:
        dyn.is_active = False
        db.commit()

    # 5. Resolve OS, Geo-fenced, and Scheduled destination URL
    country_code = (
        request.headers.get("cf-ipcountry")
        or request.headers.get("x-country-code")
        or request.query_params.get("geo")
    )
    destination = dynamic_qr_service.resolve_destination_url(
        dyn,
        user_agent_str=user_agent,
        country_code=country_code,
    )

    # 6. UTM pass-through
    destination = append_utm_parameters(destination, dyn)

    if not is_safe_redirect_url(destination):
        return HTMLResponse("Invalid or unsafe destination URL", status_code=400)

    # 7. Retargeting pixel interstitial check
    if dyn.meta_pixel_id or dyn.google_tag_id:
        return build_retargeting_interstitial(destination, dyn)

    return RedirectResponse(url=destination, status_code=307)


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
    if not dyn:
        return HTMLResponse("QR Code Not Found", status_code=404)

    if check_max_scans_exceeded(dyn, db):
        return make_expired_response(dyn.title, "has reached its maximum scan limit")

    if not dyn.is_active or dynamic_qr_service.is_expired(dyn):
        return HTMLResponse("Invalid or Expired QR Code", status_code=400)

    if not dynamic_qr_service.verify_password(dyn, password):
        ip = request.client.host if request.client else None
        masked_ip = dynamic_qr_service._mask_ip(ip) if ip else None
        try:
            activity = ActivityLog(
                action="failed_password_attempt",
                module="dynamic_qr",
                details=json.dumps({"short_code": short_code, "dynamic_id": dyn.id, "title": dyn.title}),
                ip_address=masked_ip,
            )
            db.add(activity)
            db.commit()
        except Exception:
            db.rollback()

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

    if dyn.max_scans is not None and dyn.scan_count >= dyn.max_scans:
        dyn.is_active = False
        db.commit()

    country_code = (
        request.headers.get("cf-ipcountry")
        or request.headers.get("x-country-code")
        or request.query_params.get("geo")
    )
    destination = dynamic_qr_service.resolve_destination_url(
        dyn,
        user_agent_str=user_agent,
        country_code=country_code,
    )
    destination = append_utm_parameters(destination, dyn)

    if not is_safe_redirect_url(destination):
        return HTMLResponse("Invalid or unsafe destination URL", status_code=400)

    if dyn.meta_pixel_id or dyn.google_tag_id:
        return build_retargeting_interstitial(destination, dyn)

    return RedirectResponse(url=destination, status_code=307)
