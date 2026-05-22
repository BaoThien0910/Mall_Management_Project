# File: app/services/audit_service.py
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.constants.statuses import AuditAction
from app.models import NhatKy
from app.schemas.nhatky import NhatKyFilter
from app.utils.datetime_helper import current_datetime
from app.utils.pagination import calculate_offset, calculate_total_pages, normalize_pagination


def _generate_code(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def write_audit_log(
    db: Session,
    ma_tk: str,
    hanh_dong: AuditAction,
    doi_tuong: str,
    ma_doi_tuong: Optional[str] = None,
    gia_tri_cu: Optional[str] = None,
    gia_tri_moi: Optional[str] = None,
    chi_tiet: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> NhatKy:
    """Tạo bản ghi audit log nhưng không tự commit transaction."""
    audit_log = NhatKy(
        ma_nhat_ky=_generate_code("NK"),
        ma_tai_khoan=ma_tk,
        thoi_gian=current_datetime(),
        hanh_dong=_enum_value(hanh_dong),
        doi_tuong=doi_tuong,
        ma_doi_tuong=ma_doi_tuong,
        gia_tri_cu=gia_tri_cu,
        gia_tri_moi=gia_tri_moi,
        chi_tiet=chi_tiet,
        ip_address=ip_address,
    )
    db.add(audit_log)
    db.flush()
    return audit_log


def list_audit_logs(
    db: Session,
    filters: NhatKyFilter,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Liệt kê nhật ký thao tác có lọc và phân trang."""
    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = []

    if filters.ma_tai_khoan:
        conditions.append(NhatKy.ma_tai_khoan == filters.ma_tai_khoan)
    if filters.hanh_dong:
        conditions.append(NhatKy.hanh_dong == _enum_value(filters.hanh_dong))
    if filters.doi_tuong:
        conditions.append(NhatKy.doi_tuong.ilike(f"%{filters.doi_tuong}%"))
    if filters.tu_ngay:
        conditions.append(NhatKy.thoi_gian >= filters.tu_ngay)
    if filters.den_ngay:
        conditions.append(NhatKy.thoi_gian <= filters.den_ngay)

    stmt = select(NhatKy)
    count_stmt = select(func.count()).select_from(NhatKy)
    if conditions:
        clause = and_(*conditions)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(
        stmt.order_by(NhatKy.thoi_gian.desc())
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
