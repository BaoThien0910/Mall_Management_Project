# File: app/services/rent_request_service.py
"""
Service xử lý nghiệp vụ Yêu cầu thuê thêm mặt bằng.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.yc_thuethem import YeuCauThueThem
from app.models.hopdong import HopDong
from app.models.matbang import MatBang
from app.schemas.yc_thuethem import YeuCauThuaThemCreate, YeuCauDuyetBody, YeuCauFilter
from app.constants.statuses import (
    TrangThaiHopDong,
    TrangThaiMatBang,
    TrangThaiYeuCau,
)
from app.services.audit_service import write_audit_log


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_yeucau_or_404(db: Session, mayc: str) -> YeuCauThueThem:
    """Lấy yêu cầu theo mã, raise 404 nếu không tồn tại."""
    yc = db.get(YeuCauThueThem, mayc)
    if not yc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy yêu cầu thuê thêm với mã: {mayc}",
        )
    return yc


def _assert_has_active_contract(db: Session, makh: str) -> None:
    """
    Khách thuê phải có ít nhất một hợp đồng đang hiệu lực
    mới được phép gửi yêu cầu thuê thêm.
    """
    stmt = select(func.count()).where(
        HopDong.makh == makh,
        HopDong.trangthai == TrangThaiHopDong.DANG_HIEU_LUC,
    )
    count = db.execute(stmt).scalar_one()
    if count == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Bạn không có hợp đồng đang hiệu lực. "
                "Chỉ khách thuê hiện hữu mới được gửi yêu cầu thuê thêm."
            ),
        )


def _assert_matbang_con_trong(db: Session, mamb: str) -> None:
    """Mặt bằng được yêu cầu phải đang ở trạng thái 'Còn trống'."""
    mb = db.get(MatBang, mamb)
    if not mb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy mặt bằng với mã: {mamb}",
        )
    if mb.trangthai != TrangThaiMatBang.CON_TRONG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mặt bằng '{mamb}' không ở trạng thái 'Còn trống'",
        )


def _assert_no_pending_request(db: Session, makh: str, mamb: str) -> None:
    """
    Không được gửi nhiều yêu cầu đang 'Chờ duyệt'
    cho cùng một mặt bằng.
    """
    stmt = select(func.count()).where(
        YeuCauThueThem.makh == makh,
        YeuCauThueThem.mamb == mamb,
        YeuCauThueThem.trangthai == TrangThaiYeuCau.CHO_DUYET,
    )
    count = db.execute(stmt).scalar_one()
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Bạn đã có yêu cầu đang chờ duyệt cho mặt bằng '{mamb}'"
            ),
        )


def _generate_mayc(db: Session) -> str:
    """Sinh mã yêu cầu tự động (YC + 8 ký tự UUID)."""
    while True:
        mayc = "YC" + uuid.uuid4().hex[:8].upper()
        if not db.get(YeuCauThueThem, mayc):
            return mayc


# ── Business logic ────────────────────────────────────────────────────────────

def create_yeu_cau(
    db: Session,
    data: YeuCauThuaThemCreate,
    makh: str,
    matk: str,
) -> YeuCauThueThem:
    """
    Khách thuê gửi yêu cầu thuê thêm mặt bằng.

    Ràng buộc:
    - Khách thuê có hợp đồng đang hiệu lực
    - Mặt bằng còn trống
    - Chưa có yêu cầu chờ duyệt cho mặt bằng này
    """
    _assert_has_active_contract(db, makh)
    _assert_matbang_con_trong(db, data.mamb)
    _assert_no_pending_request(db, makh, data.mamb)

    mayc = _generate_mayc(db)
    ngayyeucau = data.ngayyeucau or date.today()

    yc = YeuCauThueThem(
        mayc=mayc,
        makh=makh,
        mamb=data.mamb,
        ngayyeucau=ngayyeucau,
        trangthai=TrangThaiYeuCau.CHO_DUYET,
        ghichu=data.ghichu,
    )
    db.add(yc)
    db.commit()
    db.refresh(yc)

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="CREATE",
        doi_tuong="YEUCAU_THUETHEM",
        ma_doi_tuong=mayc,
        noi_dung=f"Khách thuê '{makh}' gửi yêu cầu thuê thêm mặt bằng '{data.mamb}'",
    )

    return yc


def list_yeu_cau_cua_toi(
    db: Session,
    makh: str,
    filters: YeuCauFilter,
) -> dict[str, Any]:
    """Khách thuê xem danh sách yêu cầu của chính mình."""
    stmt = select(YeuCauThueThem).where(YeuCauThueThem.makh == makh)

    if filters.trangthai:
        stmt = stmt.where(YeuCauThueThem.trangthai == filters.trangthai)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (filters.page - 1) * filters.page_size
    stmt = stmt.offset(offset).limit(filters.page_size)
    items = list(db.execute(stmt).scalars().all())

    return {"total": total, "page": filters.page, "page_size": filters.page_size, "items": items}


def list_yeu_cau_all(
    db: Session,
    filters: YeuCauFilter,
) -> dict[str, Any]:
    """Ban Quản Lý xem toàn bộ yêu cầu thuê thêm."""
    stmt = select(YeuCauThueThem)

    if filters.trangthai:
        stmt = stmt.where(YeuCauThueThem.trangthai == filters.trangthai)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (filters.page - 1) * filters.page_size
    stmt = stmt.offset(offset).limit(filters.page_size)
    items = list(db.execute(stmt).scalars().all())

    return {"total": total, "page": filters.page, "page_size": filters.page_size, "items": items}


def duyet_yeu_cau(
    db: Session,
    mayc: str,
    body: YeuCauDuyetBody,
    matk: str,
) -> YeuCauThueThem:
    """
    Ban Quản Lý duyệt hoặc từ chối yêu cầu thuê thêm.

    - Chỉ duyệt yêu cầu đang 'Chờ duyệt'
    - Duyệt → 'Đã duyệt - Chờ số hóa hợp đồng'
    - Từ chối → 'Từ chối' + bắt buộc có lý do
    """
    yc = _get_yeucau_or_404(db, mayc)

    if yc.trangthai != TrangThaiYeuCau.CHO_DUYET:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Yêu cầu '{mayc}' đang ở trạng thái '{yc.trangthai}', "
                "không thể xét duyệt"
            ),
        )

    if body.ket_qua == "DUYET":
        yc.trangthai = TrangThaiYeuCau.DA_DUYET_CHO_SO_HOA
        yc.ghi_chu_cho_kdtc = body.ghi_chu_cho_kdtc
        hanh_dong_log = "APPROVE"
        noi_dung_log = f"Duyệt yêu cầu thuê thêm '{mayc}'"
    else:  # TU_CHOI
        yc.trangthai = TrangThaiYeuCau.TU_CHOI
        yc.ly_do_tu_choi = body.ly_do_tu_choi
        yc.ghi_chu_cho_kdtc = body.ghi_chu_cho_kdtc
        hanh_dong_log = "REJECT"
        noi_dung_log = (
            f"Từ chối yêu cầu thuê thêm '{mayc}'. "
            f"Lý do: {body.ly_do_tu_choi}"
        )

    db.commit()
    db.refresh(yc)

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong=hanh_dong_log,
        doi_tuong="YEUCAU_THUETHEM",
        ma_doi_tuong=mayc,
        noi_dung=noi_dung_log,
    )

    return yc
