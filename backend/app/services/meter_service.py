# File: app/services/meter_service.py
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.constants.statuses import AuditAction
from app.exceptions.business_exceptions import ConflictException, NotFoundException, BadRequestException
from app.models import ChiSoDienNuoc, MatBang
from app.schemas.chisodiennuoc import ChiSoDienNuocCreate, ChiSoDienNuocFilter
from app.services.audit_service import write_audit_log
from app.utils.datetime_helper import current_datetime
from app.utils.pagination import calculate_offset, calculate_total_pages, normalize_pagination
from app.utils.transaction import transaction_context


def _generate_code(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"


def _user_attr(current_user: Any, short_name: str, long_name: str) -> Any:
    value = getattr(current_user, short_name, None)
    return value if value is not None else getattr(current_user, long_name, None)


def create_meter_reading(
    db: Session,
    payload: ChiSoDienNuocCreate,
    current_user: Any,
) -> ChiSoDienNuoc:
    """Tạo bản ghi chỉ số điện nước cho một mặt bằng."""
    premise = db.execute(
        select(MatBang).where(MatBang.ma_mat_bang == payload.ma_mat_bang)
    ).scalars().first()
    if premise is None:
        raise NotFoundException("Không tìm thấy mặt bằng")

    duplicate = db.execute(
        select(ChiSoDienNuoc).where(
            ChiSoDienNuoc.ma_mat_bang == payload.ma_mat_bang,
            ChiSoDienNuoc.thang == payload.thang,
            ChiSoDienNuoc.nam == payload.nam,
        )
    ).scalars().first()
    if duplicate is not None:
        raise ConflictException("Đã tồn tại chỉ số điện nước của kỳ này")

    ma_nhan_vien_nhap = _user_attr(current_user, "ma_nv", "ma_nhan_vien")
    if not ma_nhan_vien_nhap:
        raise BadRequestException("Không xác định được nhân viên nhập chỉ số")

    reading = ChiSoDienNuoc(
        ma_chi_so_dien_nuoc=_generate_code("CSDN"),
        ma_mat_bang=payload.ma_mat_bang,
        ma_nhan_vien_nhap=ma_nhan_vien_nhap,
        thang=payload.thang,
        nam=payload.nam,
        chi_so_dien_dau=payload.chi_so_dien_dau,
        chi_so_dien_cuoi=payload.chi_so_dien_cuoi,
        chi_so_nuoc_dau=payload.chi_so_nuoc_dau,
        chi_so_nuoc_cuoi=payload.chi_so_nuoc_cuoi,
        ngay_nhap=current_datetime(),
    )
    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.add(reading)
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="CHISODIENNUOC",
            ma_doi_tuong=reading.ma_chi_so_dien_nuoc,
            chi_tiet="Nhập chỉ số điện nước",
        )
    return reading


def list_meter_readings(
    db: Session,
    filters: ChiSoDienNuocFilter,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Liệt kê chỉ số điện nước theo bộ lọc."""
    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = []
    if filters.ma_mat_bang:
        conditions.append(ChiSoDienNuoc.ma_mat_bang == filters.ma_mat_bang)
    if filters.thang is not None:
        conditions.append(ChiSoDienNuoc.thang == filters.thang)
    if filters.nam is not None:
        conditions.append(ChiSoDienNuoc.nam == filters.nam)

    stmt = select(ChiSoDienNuoc)
    count_stmt = select(func.count()).select_from(ChiSoDienNuoc)
    if conditions:
        clause = and_(*conditions)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(
        stmt.order_by(ChiSoDienNuoc.nam.desc(), ChiSoDienNuoc.thang.desc())
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    ).scalars().all()
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": calculate_total_pages(total, page_size),
        },
    }
