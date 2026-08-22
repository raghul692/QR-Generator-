"""
QRMaster Pro — Categories API Router.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas import MessageResponse, QRCategoryCreate
from app.services.category_service import category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", summary="List all categories")
def list_categories(db: Session = Depends(get_db)):
    return category_service.list(db)


@router.get("/{category_id}", summary="Get a category")
def get_category(category_id: int, db: Session = Depends(get_db)):
    result = category_service.get(db, category_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")
    return result


@router.post("/", summary="Create a category")
def create_category(req: QRCategoryCreate, db: Session = Depends(get_db)):
    return category_service.create(
        db, name=req.name, description=req.description or "",
        icon=req.icon or "", color=req.color or "",
    )


@router.put("/{category_id}", summary="Update a category")
def update_category(category_id: int, req: QRCategoryCreate, db: Session = Depends(get_db)):
    result = category_service.update(
        db, category_id, name=req.name, description=req.description,
        icon=req.icon, color=req.color,
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")
    return result


@router.delete("/{category_id}", response_model=MessageResponse, summary="Delete a category")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    try:
        success = category_service.delete(db, category_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not success:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")
    return MessageResponse(message=f"Category {category_id} deleted", success=True)