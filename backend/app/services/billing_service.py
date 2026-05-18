# File: app/services/billing_service.py
"""
Service xử lý Tính toán công nợ tháng và tra cứu công nợ.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.congno import CongNo
from app.models.hopdong import HopDong
from app.models.chisodiennuoc import ChiSoDienNuoc
from app.models.dulieu_import_taichinh import DuLieuImportTaiChinh
from app.schemas.congno import TinhCongNoInput, CongNoFilter, TinhCongNoKetQuaResponse
from app.constants.statuses import (
    TrangThaiHopDong,
    TrangThaiCongNo,
    TrangThaiImport,
    LoaiKhoanThu,
)
from app.services.audit_service import write_audit_log


# ── Helpers ───────────────────────────────────────────────────────────────────

def _gen_macn(db: Session) -> str:
    """Sinh mã công nợ duy nhất."""
    while True:
        ma = "CN" + uuid.uuid4().hex[:8].upper()
        if not db.get(CongNo, ma):
            return ma


def _get_congno_or_404(db: Session, macn: str) -> CongNo:
    cn = db.get(CongNo, macn)
    if not cn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy công nợ mã: {macn}",
        )
    return cn


def _lay_so_tien_import(
    db: Session,
    mahd: str,
    thang: int,
    nam: int,
    loai_khoan: str,
) -> float:
    """
    Lấy tổng số tiền từ bảng DULIEU_IMPORT_TAICHINH cho một loại khoản
    trong kỳ tháng/năm của hợp đồng. Chỉ lấy các dòng có trạng thái 'Hợp lệ'.
    """
    stmt = select(func.sum(DuLieuImportTaiChinh.so_tien)).where(
        DuLieuImportTaiChinh.mahd == mahd,
        DuLieuImportTaiChinh.thang == thang,
        DuLieuImportTaiChinh.nam == nam,
        DuLieuImportTaiChinh.loai_khoan == loai_khoan,
        DuLieuImportTaiChinh.trang_thai == TrangThaiImport.HOP_LE,
    )
    result = db.execute(stmt).scalar_one_or_none()
    return float(result) if result else 0.0


def _lay_tieu_thu_dien_nuoc(
    db: Session,
    mamb: str,
    thang: int,
    nam: int,
) -> tuple[float, float]:
    """
    Lấy điện tiêu thụ và nước tiêu thụ từ CHISODIENNUOC.
    Trả về (dien_tieu_thu, nuoc_tieu_thu).
    """
    stmt = select(ChiSoDienNuoc).where(
        ChiSoDienNuoc.mamb == mamb,
        ChiSoDienNuoc.thang == thang,
        ChiSoDienNuoc.nam == nam,
    )
    chs = db.execute(stmt).scalar_one_or_none()
    if not chs:
        return 0.0, 0.0
    return float(chs.dien_tieu_thu), float(chs.nuoc_tieu_thu)


def _danh_dau_import_da_dung(
    db: Session,
    mahd: str,
    thang: int,
    nam: int,
) -> None:
    """
    Cập nhật tất cả dòng import 'Hợp lệ' của kỳ này sang 'Đã dùng tính công nợ'.
    """
    stmt = select(DuLieuImportTaiChinh).where(
        DuLieuImportTaiChinh.mahd == mahd,
        DuLieuImportTaiChinh.thang == thang,
        DuLieuImportTaiChinh.nam == nam,
        DuLieuImportTaiChinh.trang_thai == TrangThaiImport.HOP_LE,
    )
    records = list(db.execute(stmt).scalars().all())
    for rec in records:
        rec.trang_thai = TrangThaiImport.DA_DUNG


# ── Business logic ────────────────────────────────────────────────────────────

def tinh_cong_no_thang(
    db: Session,
    data: TinhCongNoInput,
    matk: str,
) -> TinhCongNoKetQuaResponse:
    """
    Tính công nợ tháng cho tất cả hợp đồng đang hiệu lực.

    Quy trình:
    1. Lấy danh sách hợp đồng đang hiệu lực
    2. Với mỗi hợp đồng:
       a. Bỏ qua nếu đã có công nợ kỳ này
       b. Lấy tiền thuê, điện, nước, phí bảo trì, hoàn trả từ import
       c. Lấy tiêu thụ điện/nước từ chỉ số
       d. Tính tổng tiền
       e. Tạo bản ghi CONGNO
       f. Đánh dấu import đã dùng
    3. Commit toàn bộ trong một transaction
    """
    thang, nam = data.thang, data.nam

    if nam > date.today().year or (
        nam == date.today().year and thang > date.today().month
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tính công nợ cho kỳ ở tương lai",
        )

    # Lấy hợp đồng đang hiệu lực
    stmt = select(HopDong).where(HopDong.trangthai == TrangThaiHopDong.DANG_HIEU_LUC)
    hop_dongs = list(db.execute(stmt).scalars().all())

    if not hop_dongs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không có hợp đồng nào đang hiệu lực",
        )

    tao_thanh_cong = 0
    bo_qua_trung = 0
    thieu_du_lieu: list[str] = []
    new_records: list[CongNo] = []

    try:
        for hd in hop_dongs:
            mahd = hd.mahd

            # Kiểm tra đã có công nợ kỳ này chưa
            exist_stmt = select(func.count()).where(
                CongNo.mahd == mahd,
                CongNo.thang == thang,
                CongNo.nam == nam,
            )
            if db.execute(exist_stmt).scalar_one() > 0:
                bo_qua_trung += 1
                continue

            # Lấy dữ liệu tài chính từ import
            tien_thue = _lay_so_tien_import(db, mahd, thang, nam, LoaiKhoanThu.TIEN_THUE)
            phi_bao_tri = _lay_so_tien_import(db, mahd, thang, nam, LoaiKhoanThu.PHI_BAO_TRI)
            tien_hoan_tra = _lay_so_tien_import(db, mahd, thang, nam, LoaiKhoanThu.HOAN_TRA)

            # Lấy tiêu thụ điện nước
            dien_tieu_thu, nuoc_tieu_thu = _lay_tieu_thu_dien_nuoc(
                db, hd.mamb, thang, nam
            )

            # Lấy đơn giá điện/nước từ import nếu có, fallback = tiêu thụ
            tien_dien_import = _lay_so_tien_import(db, mahd, thang, nam, LoaiKhoanThu.TIEN_DIEN)
            tien_nuoc_import = _lay_so_tien_import(db, mahd, thang, nam, LoaiKhoanThu.TIEN_NUOC)

            # Ưu tiên dùng giá từ import; nếu không có thì dùng tiêu thụ trực tiếp
            tien_dien = tien_dien_import if tien_dien_import > 0 else dien_tieu_thu
            tien_nuoc = tien_nuoc_import if tien_nuoc_import > 0 else nuoc_tieu_thu

            # Cảnh báo thiếu dữ liệu (tiền thuê bắt buộc phải có)
            if tien_thue == 0:
                thieu_du_lieu.append(
                    f"{mahd}: thiếu 'Tiền thuê' trong import tháng {thang}/{nam}"
                )
                continue

            tong_tien = tien_thue + tien_dien + tien_nuoc + phi_bao_tri - tien_hoan_tra

            macn = _gen_macn(db)
            cn = CongNo(
                macn=macn,
                mahd=mahd,
                thang=thang,
                nam=nam,
                tien_thue=tien_thue,
                tien_dien=tien_dien,
                tien_nuoc=tien_nuoc,
                phi_bao_tri=phi_bao_tri,
                tien_hoan_tra=tien_hoan_tra,
                tong_tien=tong_tien,
                trang_thai=TrangThaiCongNo.CHUA_THANH_TOAN,
            )
            new_records.append(cn)
            db.add(cn)

            # Đánh dấu import đã dùng
            _danh_dau_import_da_dung(db, mahd, thang, nam)

            tao_thanh_cong += 1

        db.commit()

    except Exception:
        db.rollback()
        raise

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="CALCULATE",
        doi_tuong="CONGNO",
        ma_doi_tuong=f"{thang}/{nam}",
        noi_dung=(
            f"Tính công nợ tháng {thang}/{nam}: "
            f"{tao_thanh_cong} tạo mới, {bo_qua_trung} bỏ qua trùng, "
            f"{len(thieu_du_lieu)} thiếu dữ liệu"
        ),
    )

    return TinhCongNoKetQuaResponse(
        thang=thang,
        nam=nam,
        tong_hop_dong=len(hop_dongs),
        tao_thanh_cong=tao_thanh_cong,
        bo_qua_trung=bo_qua_trung,
        thieu_du_lieu=thieu_du_lieu,
    )


def list_cong_no(
    db: Session,
    filters: CongNoFilter,
) -> dict[str, Any]:
    """Lấy danh sách công nợ có phân trang và lọc (dùng cho nội bộ KDTC)."""
    stmt = select(CongNo)

    if filters.mahd:
        stmt = stmt.where(CongNo.mahd == filters.mahd)
    if filters.thang:
        stmt = stmt.where(CongNo.thang == filters.thang)
    if filters.nam:
        stmt = stmt.where(CongNo.nam == filters.nam)
    if filters.trang_thai:
        stmt = stmt.where(CongNo.trang_thai == filters.trang_thai)
    if filters.makh:
        # Join qua HopDong để lọc theo makh
        stmt = stmt.join(HopDong, CongNo.mahd == HopDong.mahd).where(
            HopDong.makh == filters.makh
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (filters.page - 1) * filters.page_size
    items = list(db.execute(stmt.offset(offset).limit(filters.page_size)).scalars().all())

    return {"total": total, "page": filters.page, "page_size": filters.page_size, "items": items}


def list_cong_no_cua_toi(
    db: Session,
    makh: str,
    filters: CongNoFilter,
) -> dict[str, Any]:
    """
    Khách thuê xem công nợ của chính mình.
    Lọc qua join HopDong theo makh.
    """
    stmt = (
        select(CongNo)
        .join(HopDong, CongNo.mahd == HopDong.mahd)
        .where(HopDong.makh == makh)
    )

    if filters.mahd:
        stmt = stmt.where(CongNo.mahd == filters.mahd)
    if filters.thang:
        stmt = stmt.where(CongNo.thang == filters.thang)
    if filters.nam:
        stmt = stmt.where(CongNo.nam == filters.nam)
    if filters.trang_thai:
        stmt = stmt.where(CongNo.trang_thai == filters.trang_thai)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (filters.page - 1) * filters.page_size
    items = list(db.execute(stmt.offset(offset).limit(filters.page_size)).scalars().all())

    return {"total": total, "page": filters.page, "page_size": filters.page_size, "items": items}


def get_congno_detail(db: Session, macn: str) -> CongNo:
    """Lấy chi tiết công nợ."""
    return _get_congno_or_404(db, macn)
