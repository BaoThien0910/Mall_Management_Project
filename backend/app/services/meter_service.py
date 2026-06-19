# File: app/services/meter_service.py
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.constants.billing import ELECTRICITY_UNIT_PRICE, WATER_UNIT_PRICE
from app.exceptions.business_exceptions import BadRequestException, ConflictException, NotFoundException
from app.models.chisodiennuoc import ChiSoDienNuoc
from app.models.matbang import MatBang
from app.services._common import generate_code, get_column, get_value


def _current_employee_id(current_user: Any) -> str:
    ma_nv = get_value(current_user, ["ma_nv", "ma_nhan_vien", "manv"])
    if not ma_nv:
        raise BadRequestException("Tài khoản hiện tại không gắn với nhân viên")
    return ma_nv


def _to_decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def _serialize_meter_reading(item: ChiSoDienNuoc) -> Dict[str, Any]:
    return {
        "ma_chi_so_dien_nuoc": get_value(item, ["ma_chi_so_dien_nuoc", "ma_csdn"], ""),
        "ma_mat_bang": get_value(item, ["ma_mat_bang", "ma_mb"], ""),
        "ma_nhan_vien_nhap": get_value(item, ["ma_nhan_vien_nhap", "ma_nv_nhap"], ""),
        "thang": item.thang,
        "nam": item.nam,
        "chi_so_dien_dau": item.chi_so_dien_dau,
        "chi_so_dien_cuoi": item.chi_so_dien_cuoi,
        "chi_so_nuoc_dau": item.chi_so_nuoc_dau,
        "chi_so_nuoc_cuoi": item.chi_so_nuoc_cuoi,
        "so_dien_tieu_thu": item.so_dien_tieu_thu,
        "so_nuoc_tieu_thu": item.so_nuoc_tieu_thu,
        "don_gia_dien": item.don_gia_dien,
        "don_gia_nuoc": item.don_gia_nuoc,
        "tien_dien": item.tien_dien,
        "tien_nuoc": item.tien_nuoc,
        "ngay_nhap": item.ngay_nhap,
    }


def create_meter_reading(
    db: Session,
    payload: Any,
    current_user: Any,
) -> Dict[str, Any]:
    """Nhập chỉ số điện nước và tự tính tiền điện/nước theo đơn giá cố định."""
    ma_mat_bang = get_value(payload, ["ma_mat_bang", "ma_mb"])
    thang = get_value(payload, ["thang"])
    nam = get_value(payload, ["nam"])
    ma_nhan_vien_nhap = _current_employee_id(current_user)

    mat_bang_id_col = get_column(MatBang, ["ma_mat_bang", "ma_mb"])
    mat_bang = db.execute(
        select(MatBang).where(mat_bang_id_col == ma_mat_bang)
    ).scalars().first()
    if mat_bang is None:
        raise NotFoundException("Không tìm thấy mặt bằng")

    meter_mamb_col = get_column(ChiSoDienNuoc, ["ma_mat_bang", "ma_mb"])
    existing = db.execute(
        select(ChiSoDienNuoc).where(
            meter_mamb_col == ma_mat_bang,
            ChiSoDienNuoc.thang == thang,
            ChiSoDienNuoc.nam == nam,
        )
    ).scalars().first()
    if existing is not None:
        raise ConflictException("Mặt bằng đã có chỉ số điện nước trong tháng/năm này")

    chi_so_dien_dau = _to_decimal(get_value(payload, ["chi_so_dien_dau"]))
    chi_so_dien_cuoi = _to_decimal(get_value(payload, ["chi_so_dien_cuoi"]))
    chi_so_nuoc_dau = _to_decimal(get_value(payload, ["chi_so_nuoc_dau"]))
    chi_so_nuoc_cuoi = _to_decimal(get_value(payload, ["chi_so_nuoc_cuoi"]))

    if chi_so_dien_cuoi < chi_so_dien_dau:
        raise BadRequestException("Chỉ số điện cuối phải lớn hơn hoặc bằng chỉ số điện đầu")
    if chi_so_nuoc_cuoi < chi_so_nuoc_dau:
        raise BadRequestException("Chỉ số nước cuối phải lớn hơn hoặc bằng chỉ số nước đầu")

    so_dien_tieu_thu = chi_so_dien_cuoi - chi_so_dien_dau
    so_nuoc_tieu_thu = chi_so_nuoc_cuoi - chi_so_nuoc_dau
    tien_dien = so_dien_tieu_thu * ELECTRICITY_UNIT_PRICE
    tien_nuoc = so_nuoc_tieu_thu * WATER_UNIT_PRICE

    item = ChiSoDienNuoc(
        ma_chi_so_dien_nuoc=generate_code("CSDN"),
        ma_mat_bang=ma_mat_bang,
        ma_nhan_vien_nhap=ma_nhan_vien_nhap,
        thang=thang,
        nam=nam,
        chi_so_dien_dau=chi_so_dien_dau,
        chi_so_dien_cuoi=chi_so_dien_cuoi,
        chi_so_nuoc_dau=chi_so_nuoc_dau,
        chi_so_nuoc_cuoi=chi_so_nuoc_cuoi,
        so_dien_tieu_thu=so_dien_tieu_thu,
        so_nuoc_tieu_thu=so_nuoc_tieu_thu,
        don_gia_dien=ELECTRICITY_UNIT_PRICE,
        don_gia_nuoc=WATER_UNIT_PRICE,
        tien_dien=tien_dien,
        tien_nuoc=tien_nuoc,
    )

    try:
        db.add(item)
        db.commit()
        db.refresh(item)
    except Exception:
        db.rollback()
        raise

    return _serialize_meter_reading(item)


def list_meter_readings(
    db: Session,
    filters: Optional[Any] = None,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Lấy danh sách chỉ số điện nước."""
    stmt = select(ChiSoDienNuoc)

    ma_mat_bang = get_value(filters, ["ma_mat_bang", "ma_mb"], None) if filters else None
    thang = get_value(filters, ["thang"], None) if filters else None
    nam = get_value(filters, ["nam"], None) if filters else None
    page = get_value(filters, ["page"], 1) if filters else 1
    page_size = get_value(filters, ["page_size"], 10) if filters else 10

    if ma_mat_bang:
        stmt = stmt.where(get_column(ChiSoDienNuoc, ["ma_mat_bang", "ma_mb"]).ilike(f"%{ma_mat_bang}%"))
    if thang:
        stmt = stmt.where(ChiSoDienNuoc.thang == thang)
    if nam:
        stmt = stmt.where(ChiSoDienNuoc.nam == nam)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(total_stmt).scalar_one()

    items = db.execute(
        stmt.order_by(ChiSoDienNuoc.nam.desc(), ChiSoDienNuoc.thang.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).scalars().all()

    return {
        "items": [_serialize_meter_reading(item) for item in items],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size if total else 0,
        },
    }
