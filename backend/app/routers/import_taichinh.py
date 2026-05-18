# File: app/routers/import_taichinh.py
"""
Router Import dữ liệu tài chính từ Excel.
Phân quyền: TP_KDTC, NV_KDTC
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.import_taichinh import (
    DuLieuImportResponse,
    ImportKetQuaResponse,
    ImportTaiChinhFilter,
)
from app.services import excel_import_service
from app.constants.roles import NV_KDTC, TP_KDTC

router = APIRouter(prefix="/api/v1/import-tai-chinh", tags=["Import tài chính"])

ROLES_IMPORT = {TP_KDTC, NV_KDTC}


def _require_roles(current_user: Any, allowed: set[str]) -> None:
    if current_user.mavaitro not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )


# ── POST /api/v1/import-tai-chinh ─────────────────────────────────────────────

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def import_excel(
    file: UploadFile = File(..., description="File Excel (.xlsx) dữ liệu tài chính"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Import dữ liệu tài chính từ file Excel."""
    _require_roles(current_user, ROLES_IMPORT)

    if not file.filename or not file.filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ chấp nhận file định dạng .xlsx",
        )

    content = await file.read()
    result = excel_import_service.import_excel_tai_chinh(
        db=db,
        file_content=content,
        ten_file=file.filename,
        matk=current_user.matk,
        manv=current_user.manv,
    )

    return {
        "success": True,
        "message": f"Import hoàn tất: {result.so_dong_hop_le}/{result.tong_dong} dòng hợp lệ",
        "data": result.model_dump(),
    }


# ── GET /api/v1/import-tai-chinh ──────────────────────────────────────────────

@router.get("", response_model=dict)
def list_import(
    mahd: str | None = Query(None),
    thang: int | None = Query(None, ge=1, le=12),
    nam: int | None = Query(None, ge=2000),
    trang_thai: str | None = Query(None),
    manv_import: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Danh sách bản ghi import tài chính (có phân trang, lọc)."""
    _require_roles(current_user, ROLES_IMPORT)

    filters = ImportTaiChinhFilter(
        mahd=mahd,
        thang=thang,
        nam=nam,
        trang_thai=trang_thai,
        manv_import=manv_import,
        page=page,
        page_size=page_size,
    )
    result = excel_import_service.list_import_tai_chinh(db, filters)

    return {
        "success": True,
        "message": "Lấy danh sách import tài chính thành công",
        "data": {
            **result,
            "items": [
                DuLieuImportResponse.model_validate(item).model_dump()
                for item in result["items"]
            ],
        },
    }
