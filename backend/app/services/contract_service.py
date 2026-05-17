# File: app/services/contract_service.py
"""
Service xử lý nghiệp vụ Quản lý Hợp đồng.
"""

from __future__ import annotations

from typing import Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.hopdong import HopDong
from app.models.matbang import MatBang
from app.models.khachthue import KhachThue
from app.models.yc_thuethem import YeuCauThueThem
from app.schemas.hopdong import HopDongCreate, HopDongFilter
from app.constants.statuses import (
    TrangThaiHopDong,
    TrangThaiMatBang,
    TrangThaiYeuCau,
)
from app.services.audit_service import write_audit_log


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_hopdong_or_404(db: Session, mahd: str) -> HopDong:
    """Lấy hợp đồng theo mã, raise 404 nếu không tồn tại."""
    hd = db.get(HopDong, mahd)
    if not hd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hợp đồng với mã: {mahd}",
        )
    return hd


def _assert_khachthue_exists(db: Session, makh: str) -> None:
    """Kiểm tra khách thuê tồn tại."""
    kt = db.get(KhachThue, makh)
    if not kt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy khách thuê với mã: {makh}",
        )


def _assert_matbang_exists(db: Session, mamb: str) -> MatBang:
    """Kiểm tra mặt bằng tồn tại và trả về object."""
    mb = db.get(MatBang, mamb)
    if not mb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy mặt bằng với mã: {mamb}",
        )
    return mb


def _assert_no_active_contract(db: Session, mamb: str) -> None:
    """Đảm bảo mặt bằng chưa có hợp đồng đang hiệu lực."""
    stmt = select(func.count()).where(
        HopDong.mamb == mamb,
        HopDong.trangthai == TrangThaiHopDong.DANG_HIEU_LUC,
    )
    count = db.execute(stmt).scalar_one()
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mặt bằng đang có hợp đồng hiệu lực, không thể tạo hợp đồng mới",
        )


def _validate_yeu_cau_lien_ket(
    db: Session,
    mayc: str,
    makh: str,
    mamb: str,
) -> YeuCauThueThem:
    """
    Kiểm tra yêu cầu thuê thêm hợp lệ để liên kết với hợp đồng mới:
    - Phải tồn tại
    - Đang ở trạng thái 'Đã duyệt - Chờ số hóa hợp đồng'
    - Phải thuộc đúng khách thuê và mặt bằng
    """
    yc = db.get(YeuCauThueThem, mayc)
    if not yc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy yêu cầu thuê thêm mã: {mayc}",
        )
    if yc.trangthai != TrangThaiYeuCau.DA_DUYET_CHO_SO_HOA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Yêu cầu '{mayc}' không ở trạng thái "
                f"'{TrangThaiYeuCau.DA_DUYET_CHO_SO_HOA}'"
            ),
        )
    if yc.makh != makh:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yêu cầu thuê thêm không thuộc khách thuê của hợp đồng",
        )
    if yc.mamb != mamb:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mặt bằng trong yêu cầu thuê thêm không khớp với hợp đồng",
        )
    return yc


# ── Business logic ────────────────────────────────────────────────────────────

def create_hopdong(
    db: Session,
    data: HopDongCreate,
    matk: str,
) -> HopDong:
    """
    Tạo hợp đồng thuê mặt bằng.

    Quy trình:
    1. Kiểm tra mã hợp đồng duy nhất
    2. Kiểm tra khách thuê, mặt bằng tồn tại
    3. Kiểm tra không có hợp đồng hiệu lực cùng mặt bằng
    4. Nếu có mayc: validate yêu cầu thuê thêm
    5. Tạo hợp đồng
    6. Nếu trạng thái 'Đang hiệu lực': cập nhật mặt bằng → 'Đang thuê'
    7. Nếu có mayc: cập nhật yêu cầu → 'Đã tạo hợp đồng'
    8. Commit transaction
    """
    # 1. Mã hợp đồng duy nhất
    if db.get(HopDong, data.mahd):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Mã hợp đồng '{data.mahd}' đã tồn tại",
        )

    # 2. Kiểm tra khách thuê & mặt bằng
    _assert_khachthue_exists(db, data.makh)
    mb = _assert_matbang_exists(db, data.mamb)

    # 3. Không trùng hợp đồng hiệu lực
    if data.trangthai == TrangThaiHopDong.DANG_HIEU_LUC:
        _assert_no_active_contract(db, data.mamb)

    # 4. Validate yêu cầu thuê thêm nếu có
    yc: YeuCauThueThem | None = None
    if data.mayc:
        yc = _validate_yeu_cau_lien_ket(db, data.mayc, data.makh, data.mamb)

    # 5. Tạo hợp đồng
    hd = HopDong(**data.model_dump())
    db.add(hd)

    # 6. Cập nhật trạng thái mặt bằng
    if data.trangthai == TrangThaiHopDong.DANG_HIEU_LUC:
        mb.trangthai = TrangThaiMatBang.DANG_THUE

    # 7. Cập nhật yêu cầu thuê thêm
    if yc:
        yc.trangthai = TrangThaiYeuCau.DA_TAO_HOP_DONG

    # 8. Commit
    db.commit()
    db.refresh(hd)

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="CREATE",
        doi_tuong="HOPDONG",
        ma_doi_tuong=hd.mahd,
        noi_dung=(
            f"Tạo hợp đồng '{hd.mahd}' cho khách thuê '{hd.makh}' "
            f"- mặt bằng '{hd.mamb}'"
        ),
    )

    return hd


def get_hopdong_detail(db: Session, mahd: str) -> HopDong:
    """Lấy chi tiết hợp đồng."""
    return _get_hopdong_or_404(db, mahd)


def get_hopdong_cua_toi(db: Session, makh: str) -> list[HopDong]:
    """Lấy tất cả hợp đồng của khách thuê hiện tại."""
    stmt = select(HopDong).where(HopDong.makh == makh)
    return list(db.execute(stmt).scalars().all())


def list_hopdong(
    db: Session,
    filters: HopDongFilter,
) -> dict[str, Any]:
    """Lấy danh sách hợp đồng có phân trang và lọc."""
    stmt = select(HopDong)

    if filters.makh:
        stmt = stmt.where(HopDong.makh == filters.makh)
    if filters.mamb:
        stmt = stmt.where(HopDong.mamb == filters.mamb)
    if filters.trangthai:
        stmt = stmt.where(HopDong.trangthai == filters.trangthai)
    if filters.ngaybatdau_tu:
        stmt = stmt.where(HopDong.ngaybatdau >= filters.ngaybatdau_tu)
    if filters.ngaybatdau_den:
        stmt = stmt.where(HopDong.ngaybatdau <= filters.ngaybatdau_den)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (filters.page - 1) * filters.page_size
    stmt = stmt.offset(offset).limit(filters.page_size)
    items = list(db.execute(stmt).scalars().all())

    return {
        "total": total,
        "page": filters.page,
        "page_size": filters.page_size,
        "items": items,
    }
