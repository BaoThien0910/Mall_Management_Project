# File: app/services/financial_report_service.py
"""
Service xử lý Lập và quản lý báo cáo tài chính (công nợ & doanh số).
"""

from __future__ import annotations

import json
import uuid
from datetime import date
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.baocaotaichinh import BaoCaoTaiChinh
from app.models.congno import CongNo
from app.models.hoadon import HoaDon
from app.schemas.baocaotaichinh import (
    BaoCaoCongNoCreate,
    BaoCaoDoanhSoCreate,
    BaoCaoFilter,
)
from app.constants.statuses import (
    TrangThaiBaoCao,
    LoaiBaoCao,
    TrangThaiCongNo,
    TrangThaiHoaDon,
)
from app.services.audit_service import write_audit_log


# ── Helpers ───────────────────────────────────────────────────────────────────

def _gen_mabctc(db: Session) -> str:
    while True:
        ma = "BCTC" + uuid.uuid4().hex[:6].upper()
        if not db.get(BaoCaoTaiChinh, ma):
            return ma


def _get_bctc_or_404(db: Session, mabctc: str) -> BaoCaoTaiChinh:
    bc = db.get(BaoCaoTaiChinh, mabctc)
    if not bc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy báo cáo mã: {mabctc}",
        )
    return bc


def _tinh_tong_cong_no(
    db: Session, thang: int, nam: int
) -> dict[str, float]:
    """
    Tính các chỉ số tổng hợp từ bảng CONGNO cho một kỳ tháng/năm.
    Trả về dict chứa tổng_cong_no, tong_da_thanh_toan, tong_chua_thanh_toan, tong_qua_han.
    """
    def _sum_by_status(trang_thai: str) -> float:
        stmt = select(func.sum(CongNo.tong_tien)).where(
            CongNo.thang == thang,
            CongNo.nam == nam,
            CongNo.trang_thai == trang_thai,
        )
        result = db.execute(stmt).scalar_one_or_none()
        return float(result) if result else 0.0

    tong = _sum_by_status(TrangThaiCongNo.CHUA_THANH_TOAN) + \
           _sum_by_status(TrangThaiCongNo.DA_THANH_TOAN) + \
           _sum_by_status(TrangThaiCongNo.QUA_HAN)

    return {
        "tong_cong_no": tong,
        "tong_da_thanh_toan": _sum_by_status(TrangThaiCongNo.DA_THANH_TOAN),
        "tong_chua_thanh_toan": _sum_by_status(TrangThaiCongNo.CHUA_THANH_TOAN),
        "tong_qua_han": _sum_by_status(TrangThaiCongNo.QUA_HAN),
    }


def _tinh_doanh_so(db: Session, thang: int, nam: int) -> float:
    """
    Tính doanh số từ hóa đơn thanh toán thành công trong kỳ.
    Lọc theo thoi_gian_giao_dich cùng tháng/năm.
    """
    stmt = (
        select(func.sum(HoaDon.so_tien_thanh_toan))
        .join(CongNo, HoaDon.macn == CongNo.macn)
        .where(
            CongNo.thang == thang,
            CongNo.nam == nam,
            HoaDon.trang_thai_giao_dich == TrangThaiHoaDon.THANH_CONG,
        )
    )
    result = db.execute(stmt).scalar_one_or_none()
    return float(result) if result else 0.0


# ── Business logic ────────────────────────────────────────────────────────────

def lap_bao_cao_cong_no(
    db: Session,
    data: BaoCaoCongNoCreate,
    matk: str,
) -> BaoCaoTaiChinh:
    """
    Lập báo cáo công nợ cho một kỳ tháng/năm.

    - Phải có ít nhất một bản ghi công nợ trong kỳ
    - Tính tự động: tổng công nợ, đã TT, chưa TT, quá hạn
    - Trạng thái mặc định: 'Bản nháp'
    """
    thang, nam = data.thang, data.nam

    # Kiểm tra có công nợ của kỳ chưa
    count_stmt = select(func.count()).where(
        CongNo.thang == thang, CongNo.nam == nam
    )
    if db.execute(count_stmt).scalar_one() == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chưa có dữ liệu công nợ tháng {thang}/{nam} để lập báo cáo",
        )

    tong_hop = _tinh_tong_cong_no(db, thang, nam)
    noi_dung_dict = {
        **({"ghi_chu": data.noi_dung_tong_hop} if data.noi_dung_tong_hop else {}),
        **tong_hop,
    }

    mabctc = _gen_mabctc(db)
    bc = BaoCaoTaiChinh(
        mabctc=mabctc,
        loai_bao_cao=LoaiBaoCao.CONG_NO,
        thang=thang,
        nam=nam,
        nguoi_lap=matk,
        ngay_lap=date.today(),
        noi_dung_tong_hop=json.dumps(noi_dung_dict, ensure_ascii=False),
        tong_gia_tri=tong_hop["tong_cong_no"],
        trang_thai=TrangThaiBaoCao.BAN_NHAP,
    )
    db.add(bc)
    db.commit()
    db.refresh(bc)

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="CREATE",
        doi_tuong="BAOCAO_CONGNO",
        ma_doi_tuong=mabctc,
        noi_dung=f"Lập báo cáo công nợ tháng {thang}/{nam}",
    )

    return bc


def lap_bao_cao_doanh_so(
    db: Session,
    data: BaoCaoDoanhSoCreate,
    matk: str,
) -> BaoCaoTaiChinh:
    """
    Lập báo cáo doanh số cho một kỳ tháng/năm.

    - Doanh số lấy từ hóa đơn thanh toán thành công trong kỳ
    - Trạng thái mặc định: 'Bản nháp'
    """
    thang, nam = data.thang, data.nam

    tong_doanh_so = _tinh_doanh_so(db, thang, nam)
    noi_dung_dict: dict[str, Any] = {
        "tong_doanh_so": tong_doanh_so,
    }
    if data.noi_dung_tong_hop:
        noi_dung_dict["ghi_chu"] = data.noi_dung_tong_hop

    mabctc = _gen_mabctc(db)
    bc = BaoCaoTaiChinh(
        mabctc=mabctc,
        loai_bao_cao=LoaiBaoCao.DOANH_SO,
        thang=thang,
        nam=nam,
        nguoi_lap=matk,
        ngay_lap=date.today(),
        noi_dung_tong_hop=json.dumps(noi_dung_dict, ensure_ascii=False),
        tong_gia_tri=tong_doanh_so,
        trang_thai=TrangThaiBaoCao.BAN_NHAP,
    )
    db.add(bc)
    db.commit()
    db.refresh(bc)

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="CREATE",
        doi_tuong="BAOCAO_DOANH_SO",
        ma_doi_tuong=mabctc,
        noi_dung=f"Lập báo cáo doanh số tháng {thang}/{nam}",
    )

    return bc


def ban_hanh_bao_cao(
    db: Session,
    mabctc: str,
    matk: str,
) -> BaoCaoTaiChinh:
    """
    Ban hành báo cáo tài chính.
    Chỉ báo cáo ở trạng thái 'Bản nháp' mới được ban hành.
    """
    bc = _get_bctc_or_404(db, mabctc)

    if bc.trang_thai != TrangThaiBaoCao.BAN_NHAP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Báo cáo '{mabctc}' không ở trạng thái 'Bản nháp'",
        )

    bc.trang_thai = TrangThaiBaoCao.DA_BAN_HANH
    db.commit()
    db.refresh(bc)

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="PUBLISH",
        doi_tuong="BAOCAO_TAICHINH",
        ma_doi_tuong=mabctc,
        noi_dung=f"Ban hành báo cáo tài chính '{mabctc}'",
    )

    return bc


def list_bao_cao(
    db: Session,
    filters: BaoCaoFilter,
) -> dict[str, Any]:
    """Lấy danh sách báo cáo tài chính có phân trang và lọc."""
    stmt = select(BaoCaoTaiChinh)

    if filters.loai_bao_cao:
        stmt = stmt.where(BaoCaoTaiChinh.loai_bao_cao == filters.loai_bao_cao)
    if filters.thang:
        stmt = stmt.where(BaoCaoTaiChinh.thang == filters.thang)
    if filters.nam:
        stmt = stmt.where(BaoCaoTaiChinh.nam == filters.nam)
    if filters.trang_thai:
        stmt = stmt.where(BaoCaoTaiChinh.trang_thai == filters.trang_thai)
    if filters.nguoi_lap:
        stmt = stmt.where(BaoCaoTaiChinh.nguoi_lap == filters.nguoi_lap)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (filters.page - 1) * filters.page_size
    items = list(db.execute(stmt.offset(offset).limit(filters.page_size)).scalars().all())

    return {"total": total, "page": filters.page, "page_size": filters.page_size, "items": items}
