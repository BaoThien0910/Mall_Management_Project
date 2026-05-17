# File: app/services/premise_service.py
"""
Service xử lý nghiệp vụ Quản lý Mặt bằng.
"""

from __future__ import annotations

from typing import Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.matbang import MatBang
from app.models.hopdong import HopDong
from app.schemas.matbang import MatBangCreate, MatBangUpdate, MatBangFilter
from app.constants.statuses import TrangThaiMatBang, TrangThaiHopDong
from app.services.audit_service import write_audit_log


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_matbang_or_404(db: Session, mamb: str) -> MatBang:
    """Lấy mặt bằng theo mã, raise 404 nếu không tồn tại."""
    mb = db.get(MatBang, mamb)
    if not mb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy mặt bằng với mã: {mamb}",
        )
    return mb


def _check_active_contract(db: Session, mamb: str) -> bool:
    """Kiểm tra mặt bằng có hợp đồng đang hiệu lực không."""
    stmt = select(func.count()).where(
        HopDong.mamb == mamb,
        HopDong.trangthai == TrangThaiHopDong.DANG_HIEU_LUC,
    )
    count = db.execute(stmt).scalar_one()
    return count > 0


# ── CRUD ──────────────────────────────────────────────────────────────────────

def create_matbang(
    db: Session,
    data: MatBangCreate,
    matk: str,
) -> MatBang:
    """
    Tạo mới mặt bằng.
    Kiểm tra mã mặt bằng chưa tồn tại.
    """
    existing = db.get(MatBang, data.mamb)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Mã mặt bằng '{data.mamb}' đã tồn tại",
        )

    mb = MatBang(**data.model_dump())
    db.add(mb)
    db.commit()
    db.refresh(mb)

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="CREATE",
        doi_tuong="MATBANG",
        ma_doi_tuong=mb.mamb,
        noi_dung=f"Thêm mới mặt bằng '{mb.tenmb}'",
    )

    return mb


def update_matbang(
    db: Session,
    mamb: str,
    data: MatBangUpdate,
    matk: str,
) -> MatBang:
    """
    Cập nhật thông tin mặt bằng.
    Chỉ cập nhật các trường được truyền vào (partial update).
    """
    mb = _get_matbang_or_404(db, mamb)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mb, field, value)

    db.commit()
    db.refresh(mb)

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="UPDATE",
        doi_tuong="MATBANG",
        ma_doi_tuong=mamb,
        noi_dung=f"Cập nhật mặt bằng '{mamb}': {list(update_data.keys())}",
    )

    return mb


def delete_matbang(
    db: Session,
    mamb: str,
    matk: str,
) -> None:
    """
    Xóa mặt bằng.
    Không cho phép xóa nếu đang có hợp đồng hiệu lực.
    """
    mb = _get_matbang_or_404(db, mamb)

    if _check_active_contract(db, mamb):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa mặt bằng đang có hợp đồng hiệu lực",
        )

    db.delete(mb)
    db.commit()

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="DELETE",
        doi_tuong="MATBANG",
        ma_doi_tuong=mamb,
        noi_dung=f"Xóa mặt bằng '{mamb}'",
    )


def get_matbang_detail(db: Session, mamb: str) -> MatBang:
    """Lấy chi tiết một mặt bằng."""
    return _get_matbang_or_404(db, mamb)


def list_matbang(
    db: Session,
    filters: MatBangFilter,
    chi_xem_con_trong: bool = False,
) -> dict[str, Any]:
    """
    Lấy danh sách mặt bằng có phân trang và lọc.
    - chi_xem_con_trong: True khi người dùng là khách thuê
      (chỉ xem mặt bằng 'Còn trống').
    """
    stmt = select(MatBang)

    # Khách thuê chỉ thấy mặt bằng còn trống
    if chi_xem_con_trong:
        stmt = stmt.where(MatBang.trangthai == TrangThaiMatBang.CON_TRONG)
    elif filters.trangthai:
        stmt = stmt.where(MatBang.trangthai == filters.trangthai)

    if filters.tang:
        stmt = stmt.where(MatBang.tang == filters.tang)
    if filters.loaimb:
        stmt = stmt.where(MatBang.loaimb == filters.loaimb)
    if filters.dientich_tu is not None:
        stmt = stmt.where(MatBang.dientich >= filters.dientich_tu)
    if filters.dientich_den is not None:
        stmt = stmt.where(MatBang.dientich <= filters.dientich_den)

    # Đếm tổng
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    # Phân trang
    offset = (filters.page - 1) * filters.page_size
    stmt = stmt.offset(offset).limit(filters.page_size)
    items = list(db.execute(stmt).scalars().all())

    return {
        "total": total,
        "page": filters.page,
        "page_size": filters.page_size,
        "items": items,
    }
