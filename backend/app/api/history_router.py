"""
QRMaster Pro — QR History API Router.

Endpoints for listing, searching, filtering, updating, deleting, and
toggling favorites on QR history records.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas import MessageResponse, QRHistoryUpdate
from app.services.history_service import history_service

router = APIRouter(prefix="/history", tags=["QR History"])


@router.get("/", summary="List QR history with search, filter, sort, pagination")
def list_history(
    search: str | None = Query(default=None),
    qr_type: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    is_favorite: bool | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total, total_pages = history_service.list_history(
        db, search=search, qr_type=qr_type, category_id=category_id,
        is_favorite=is_favorite, date_from=date_from, date_to=date_to,
        sort_by=sort_by, sort_order=sort_order, page=page, page_size=page_size,
    )
    return {"items": items, "total": total, "page": page,
            "page_size": page_size, "total_pages": total_pages}


@router.get("/{history_id}", summary="Get a single QR history record")
def get_history(history_id: int, db: Session = Depends(get_db)):
    result = history_service.get(db, history_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"QR history {history_id} not found")
    return result


@router.patch("/{history_id}", summary="Update a QR history record")
def update_history(history_id: int, req: QRHistoryUpdate, db: Session = Depends(get_db)):
    result = history_service.update(
        db, history_id, title=req.title,
        category_id=req.category_id, is_favorite=req.is_favorite,
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"QR history {history_id} not found")
    return result


@router.delete("/{history_id}", response_model=MessageResponse,
               summary="Delete a QR history record")
def delete_history(history_id: int, db: Session = Depends(get_db)):
    success = history_service.delete(db, history_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"QR history {history_id} not found")
    return MessageResponse(message=f"QR history {history_id} deleted", success=True)


@router.post("/{history_id}/favorite", summary="Toggle favorite status")
def toggle_favorite(history_id: int, db: Session = Depends(get_db)):
    result = history_service.toggle_favorite(db, history_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"QR history {history_id} not found")
    return {"id": history_id, "is_favorite": result}