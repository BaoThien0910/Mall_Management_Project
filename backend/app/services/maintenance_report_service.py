# File: app/services/maintenance_report_service.py
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.constants.statuses import AuditAction
from app.exceptions.business_exceptions import BadRequestException, NotFoundException
from app.models import BaoCaoBaoTri, MatBang
from app.schemas.baocaobaotri import BaoCaoBaoTriFilter, BaoCaoTrangThaiMatBangCreate
from app.services.audit_service import write_audit_log
from app.utils.datetime_helper import current_datetime
from app.utils.pagination import calculate_offset, calculate_total_pages, normalize_pagination
from app.utils.transaction import transaction_context


def _generate_code(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _user_attr(current_user: Any, short_name: str, long_name: str) -> Any:
    value = getattr(current_user, short_name, None)
    return value if value is not None else getattr(current_user, long_name, None)


def create_premise_status_report(
    db: Session,
    payload: BaoCaoTrangThaiMatBangCreate,
    current_user: Any,
) -> BaoCaoBaoTri:
    """Tạo báo cáo trạng thái thực tế của mặt bằng."""
    premise = db.execute(
        select(MatBang).where(MatBang.ma_mat_bang == payload.ma_mat_bang)
    ).scalars().first()
    if premise is None:
        raise NotFoundException("Không tìm thấy mặt bằng")

    ma_nhan_vien_lap = _user_attr(current_user, "ma_nv", "ma_nhan_vien")
    if not ma_nhan_vien_lap:
        raise BadRequestException("Không xác định được nhân viên lập báo cáo")

    report = BaoCaoBaoTri(
        ma_bao_cao_bao_tri=_generate_code("BCBT"),
        ma_mat_bang=payload.ma_mat_bang,
        ma_nhan_vien_lap=ma_nhan_vien_lap,
        ma_su_co=None,
        ma_lich_bao_tri=None,
        ngay_lap=current_datetime(),
        trang_thai_thuc_te=_enum_value(payload.trang_thai_thuc_te),
        noi_dung=payload.noi_dung,
        ket_luan=payload.ket_luan,
    )
    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.add(report)
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="BAOCAOBAOTRI",
            ma_doi_tuong=report.ma_bao_cao_bao_tri,
            chi_tiet="Lập báo cáo trạng thái mặt bằng",
        )
    return report


def list_maintenance_reports(
    db: Session,
    filters: BaoCaoBaoTriFilter,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Liệt kê báo cáo bảo trì theo bộ lọc."""
    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = []
    if filters.ma_mat_bang:
        conditions.append(BaoCaoBaoTri.ma_mat_bang == filters.ma_mat_bang)
    if filters.ma_nhan_vien_lap:
        conditions.append(BaoCaoBaoTri.ma_nhan_vien_lap == filters.ma_nhan_vien_lap)
    if filters.ma_su_co:
        conditions.append(BaoCaoBaoTri.ma_su_co == filters.ma_su_co)
    if filters.ma_lich_bao_tri:
        conditions.append(BaoCaoBaoTri.ma_lich_bao_tri == filters.ma_lich_bao_tri)

    stmt = select(BaoCaoBaoTri)
    count_stmt = select(func.count()).select_from(BaoCaoBaoTri)
    if conditions:
        clause = and_(*conditions)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(
        stmt.order_by(BaoCaoBaoTri.ngay_lap.desc())
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


def get_maintenance_report_detail(
    db: Session,
    ma_bc_bt: str,
    current_user: Optional[Any] = None,
) -> BaoCaoBaoTri:
    """Lấy chi tiết báo cáo bảo trì."""
    report = db.execute(
        select(BaoCaoBaoTri).where(BaoCaoBaoTri.ma_bao_cao_bao_tri == ma_bc_bt)
    ).scalars().first()
    if report is None:
        raise NotFoundException("Không tìm thấy báo cáo bảo trì")
    return report
