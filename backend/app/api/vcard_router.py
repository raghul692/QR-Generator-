"""
QRMaster Pro — vCard API Router.

Endpoints for generating and downloading RFC 6350 / v3.0 compliant vCard files (.vcf).
Supports frontend vcardAPI operations.
"""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query, Response, status
from pydantic import BaseModel

from app.schemas import VCardGenerateRequest, VCardGenerateResponse
from app.services.vcard_service import vcard_service

router = APIRouter(prefix="/vcard", tags=["vCard"])


class VCardParseRequest(BaseModel):
    vcf: str


@router.post("/generate", response_model=VCardGenerateResponse, status_code=status.HTTP_200_OK)
def generate_vcard(req: VCardGenerateRequest):
    """Generate RFC 6350 / v3.0 VCF content from structured contact details."""
    data = req.model_dump(exclude_unset=True)
    vcf = vcard_service.generate(data)
    first = (req.first_name or "").strip()
    last = (req.last_name or "").strip()
    base_name = f"{first}_{last}".strip("_") or "contact"
    filename = f"{base_name}.vcf"
    return VCardGenerateResponse(vcf=vcf, filename=filename, encoded_data=vcf)


@router.post("/download")
def download_vcard(req: VCardGenerateRequest):
    """Download generated vCard as a .vcf file attachment."""
    data = req.model_dump(exclude_unset=True)
    vcf = vcard_service.generate(data)
    first = (req.first_name or "").strip()
    last = (req.last_name or "").strip()
    base_name = f"{first}_{last}".strip("_") or "contact"
    filename = f"{base_name}.vcf"
    return Response(
        content=vcf,
        media_type="text/vcard",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/parse", response_model=Dict[str, Any])
def parse_vcard(req: VCardParseRequest):
    """Parse raw vCard (.vcf) string into structured contact fields."""
    parsed = vcard_service.parse(req.vcf)
    if not parsed:
        raise HTTPException(status_code=400, detail="Invalid or unparseable vCard content")
    return parsed
