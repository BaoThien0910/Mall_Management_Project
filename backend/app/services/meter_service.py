# File: app/services/meter_service.py
"""
Service xử lý Nhập chỉ số điện nước từng mặt bằng.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.chisodiennuoc import ChiSoDienNuoc
from app.models.matbang import MatBang
from app.schemas.chisodiennuoc import ChiSoDienNuocCreate, ChiSoFilter
from app.services.audit_service import write_audit_log


# ── Helpers ───────────────────────────────────────────────────────────────────

def _gen_machs(db: Session) -> str:
    """Sinh mã chỉ số điện nước duy nhất."""
    while True:
        ma = "CHS" + uuid.uuid4().hex[:8].upper()
        if not db.get(ChiSoDienNuoc, ma):
            return ma


def _get_chiso_or_404(db: Session, machs: str) -> ChiSoDienNuoc:
    chs = db.get(ChiSoDienNuoc, machs)
    if not chs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy chỉ số điện nước mã: {machs}",
        )
    return chs


# ── Business logic ────────────────────────────────────────────────────────────

def create_chi_so(
    db: Session,
    data: ChiSoDienNuocCreate,
    matk: str,
    manv: str | None,
) -> ChiSoDienNuoc:
    """
    Nhập chỉ số điện nước cho một mặt bằng trong một tháng/năm.

    Ràng buộc:
    - Mặt bằng phải tồn tại
    - Năm không ở tương lai
    - Không trùng (mamb + thang + nam)
    - Chỉ số cuối kỳ >= đầu kỳ (validate trong schema)
    """
    # Kiểm tra mặt bằng tồn tại
    if not db.get(MatBang, data.mamb):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy mặt bằng mã: {data.mamb}",
        )

    # Năm không ở tương lai
    if data.nam > date.today().year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Năm nhập liệu không được ở tương lai",
        )

    # Kiểm tra trùng (mamb + thang + nam)
    dup_stmt = select(func.count()).where(
        ChiSoDienNuoc.mamb == data.mamb,
        ChiSoDienNuoc.thang == data.thang,
        ChiSoDienNuoc.nam == data.nam,
    )
    if db.execute(dup_stmt).scalar_one() > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Mặt bằng '{data.mamb}' đã có chỉ số điện nước "
                f"tháng {data.thang}/{data.nam}"
            ),
        )

    dien_tieu_thu = data.chi_so_dien_cuoi_ky - data.chi_so_dien_dau_ky
    nuoc_tieu_thu = data.chi_so_nuoc_cuoi_ky - data.chi_so_nuoc_dau_ky
    machs = _gen_machs(db)

    chs = ChiSoDienNuoc(
        machs=machs,
        mamb=data.mamb,
        thang=data.thang,
        nam=data.nam,
        chi_so_dien_dau_ky=data.chi_so_dien_dau_ky,
        chi_so_dien_cuoi_ky=data.chi_so_dien_cuoi_ky,
        chi_so_nuoc_dau_ky=data.chi_so_nuoc_dau_ky,
        chi_so_nuoc_cuoi_ky=data.chi_so_nuoc_cuoi_ky,
        dien_tieu_thu=dien_tieu_thu,
        nuoc_tieu_thu=nuoc_tieu_thu,
        manv_nhap=manv,
        thoi_gian_nhap=datetime.now(),
    )
    db.add(chs)
    db.commit()
    db.refresh(chs)

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="CREATE",
        doi_tuong="CHISO_DIEN_NUOC",
        ma_doi_tuong=machs,
        noi_dung=(
            f"Nhập chỉ số điện nước mặt bằng '{data.mamb}' "
            f"tháng {data.thang}/{data.nam}"
        ),
    )

    return chs


def get_chi_so_detail(db: Session, machs: str) -> ChiSoDienNuoc:
    """Lấy chi tiết một bản ghi chỉ số điện nước."""
    return _get_chiso_or_404(db, machs)


def list_chi_so(db: Session, filters: ChiSoFilter) -> dict[str, Any]:
    """Lấy danh sách chỉ số điện nước có phân trang và lọc."""
    stmt = select(ChiSoDienNuoc)

    if filters.mamb:
        stmt = stmt.where(ChiSoDienNuoc.mamb == filters.mamb)
    if filters.thang:
        stmt = stmt.where(ChiSoDienNuoc.thang == filters.thang)
    if filters.nam:
        stmt = stmt.where(ChiSoDienNuoc.nam == filters.nam)
    if filters.manv_nhap:
        stmt = stmt.where(ChiSoDienNuoc.manv_nhap == filters.manv_nhap)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (filters.page - 1) * filters.page_size
    items = list(db.execute(stmt.offset(offset).limit(filters.page_size)).scalars().all())

    return {"total": total, "page": filters.page, "page_size": filters.page_size, "items": items}
