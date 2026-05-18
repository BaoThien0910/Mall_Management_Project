# File: app/services/payment_service.py
"""
Service xử lý Thanh toán công nợ mô phỏng.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.hoadon import HoaDon
from app.models.congno import CongNo
from app.models.hopdong import HopDong
from app.schemas.payment import TaoGiaoDichInput, MoPhongKetQuaInput
from app.constants.statuses import (
    TrangThaiCongNo,
    TrangThaiHoaDon,
)
from app.services.audit_service import write_audit_log


# ── Helpers ───────────────────────────────────────────────────────────────────

def _gen_mahoadon(db: Session) -> str:
    while True:
        ma = "HD" + uuid.uuid4().hex[:8].upper()
        if not db.get(HoaDon, ma):
            return ma


def _gen_ma_giao_dich() -> str:
    """Sinh mã giao dịch mô phỏng."""
    return "GD" + uuid.uuid4().hex[:12].upper()


def _get_hoadon_or_404(db: Session, mahoadon: str) -> HoaDon:
    hd = db.get(HoaDon, mahoadon)
    if not hd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hóa đơn mã: {mahoadon}",
        )
    return hd


def _get_congno_or_404(db: Session, macn: str) -> CongNo:
    cn = db.get(CongNo, macn)
    if not cn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy công nợ mã: {macn}",
        )
    return cn


def _assert_congno_belongs_to_khach(
    db: Session, cn: CongNo, makh: str
) -> None:
    """Đảm bảo công nợ thuộc khách thuê đang đăng nhập."""
    hd = db.get(HopDong, cn.mahd)
    if not hd or hd.makh != makh:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Công nợ này không thuộc về bạn",
        )


def _assert_hoadon_belongs_to_khach(
    db: Session, hoadon: HoaDon, makh: str
) -> None:
    if hoadon.makh != makh:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hóa đơn này không thuộc về bạn",
        )


# ── Business logic ────────────────────────────────────────────────────────────

def tao_giao_dich(
    db: Session,
    data: TaoGiaoDichInput,
    makh: str,
    matk: str,
) -> HoaDon:
    """
    Tạo giao dịch thanh toán mô phỏng cho một khoản công nợ.

    Ràng buộc:
    - Công nợ phải tồn tại
    - Công nợ thuộc khách thuê đang đăng nhập
    - Công nợ ở trạng thái 'Chưa thanh toán'
    - Snapshot tiền từ CONGNO sang HOADON
    """
    cn = _get_congno_or_404(db, data.macn)
    _assert_congno_belongs_to_khach(db, cn, makh)

    if cn.trang_thai != TrangThaiCongNo.CHUA_THANH_TOAN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Công nợ '{data.macn}' không ở trạng thái 'Chưa thanh toán'",
        )

    mahoadon = _gen_mahoadon(db)
    ma_giao_dich = _gen_ma_giao_dich()

    hoadon = HoaDon(
        mahoadon=mahoadon,
        macn=data.macn,
        makh=makh,
        so_tien_thanh_toan=cn.tong_tien,
        phuong_thuc=data.phuong_thuc,
        ma_giao_dich_mo_phong=ma_giao_dich,
        trang_thai_giao_dich=TrangThaiHoaDon.DANG_XU_LY,
        thoi_gian_giao_dich=datetime.now(),
        # Snapshot từ CONGNO
        tien_thue=cn.tien_thue,
        tien_dien=cn.tien_dien,
        tien_nuoc=cn.tien_nuoc,
        phi_bao_tri=cn.phi_bao_tri,
        tien_hoan_tra=cn.tien_hoan_tra,
        tong_tien=cn.tong_tien,
    )
    db.add(hoadon)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(hoadon)

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="CREATE",
        doi_tuong="HOADON",
        ma_doi_tuong=mahoadon,
        noi_dung=(
            f"Tạo giao dịch thanh toán '{data.phuong_thuc}' "
            f"cho công nợ '{data.macn}' - mã GD: {ma_giao_dich}"
        ),
    )

    return hoadon


def mo_phong_ket_qua(
    db: Session,
    mahoadon: str,
    data: MoPhongKetQuaInput,
    makh: str,
    matk: str,
) -> HoaDon:
    """
    Mô phỏng kết quả thanh toán (Thành công / Thất bại).

    - THANH_CONG: HOADON → 'Thành công', CONGNO → 'Đã thanh toán'
    - THAT_BAI:   HOADON → 'Thất bại', CONGNO giữ nguyên
    - Không cho cập nhật hóa đơn đã ở trạng thái cuối
    """
    hoadon = _get_hoadon_or_404(db, mahoadon)
    _assert_hoadon_belongs_to_khach(db, hoadon, makh)

    TRANG_THAI_CUOI = {TrangThaiHoaDon.THANH_CONG, TrangThaiHoaDon.THAT_BAI}
    if hoadon.trang_thai_giao_dich in TRANG_THAI_CUOI:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Hóa đơn '{mahoadon}' đã ở trạng thái cuối "
                f"'{hoadon.trang_thai_giao_dich}', không thể cập nhật"
            ),
        )

    try:
        if data.ket_qua == "THANH_CONG":
            hoadon.trang_thai_giao_dich = TrangThaiHoaDon.THANH_CONG
            cn = _get_congno_or_404(db, hoadon.macn)
            cn.trang_thai = TrangThaiCongNo.DA_THANH_TOAN
            hanh_dong_log = "PAYMENT_SUCCESS"
            noi_dung_log = f"Thanh toán thành công hóa đơn '{mahoadon}'"
        else:
            hoadon.trang_thai_giao_dich = TrangThaiHoaDon.THAT_BAI
            hanh_dong_log = "PAYMENT_FAILED"
            noi_dung_log = f"Thanh toán thất bại hóa đơn '{mahoadon}'"

        db.commit()

    except Exception:
        db.rollback()
        raise

    db.refresh(hoadon)

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong=hanh_dong_log,
        doi_tuong="HOADON",
        ma_doi_tuong=mahoadon,
        noi_dung=noi_dung_log,
    )

    return hoadon


def get_hoadon_detail(db: Session, mahoadon: str, makh: str) -> HoaDon:
    """Lấy chi tiết hóa đơn (chỉ của khách thuê đang đăng nhập)."""
    hoadon = _get_hoadon_or_404(db, mahoadon)
    _assert_hoadon_belongs_to_khach(db, hoadon, makh)
    return hoadon


def list_hoadon_cua_toi(db: Session, makh: str) -> list[HoaDon]:
    """Lấy tất cả hóa đơn của khách thuê đang đăng nhập."""
    stmt = select(HoaDon).where(HoaDon.makh == makh)
    return list(db.execute(stmt).scalars().all())
