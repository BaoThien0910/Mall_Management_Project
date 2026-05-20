# File: app/services/maintenance_schedule_service.py
import uuid
from typing import Any, Dict, List

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.constants.statuses import AuditAction, LichBaoTriStatus
from app.exceptions.business_exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models import LichBaoTri, MatBang, NhanVien
from app.schemas.lichbt import LichBaoTriCreate, LichBaoTriFilter
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


def _role_value(current_user: Any) -> Any:
    return _enum_value(_user_attr(current_user, "ma_vai_tro", "ma_vai_tro"))


def create_maintenance_schedule(
    db: Session,
    payload: LichBaoTriCreate,
    current_user: Any,
) -> LichBaoTri:
    """Lập lịch bảo trì cho mặt bằng."""
    premise = db.execute(
        select(MatBang).where(MatBang.ma_mat_bang == payload.ma_mat_bang)
    ).scalars().first()
    if premise is None:
        raise NotFoundException("Không tìm thấy mặt bằng")

    assignee = db.execute(
        select(NhanVien).where(NhanVien.ma_nhan_vien == payload.ma_nhan_vien_thuc_hien)
    ).scalars().first()
    if assignee is None:
        raise NotFoundException("Không tìm thấy nhân viên thực hiện")
    if assignee.phong_ban != "Vận hành - Bảo trì":
        raise BadRequestException("Nhân viên thực hiện không thuộc phòng Vận hành - Bảo trì")
    if payload.ngay_thuc_hien_du_kien <= current_datetime():
        raise BadRequestException("Ngày thực hiện dự kiến phải nằm trong tương lai")

    ma_nhan_vien_lap = _user_attr(current_user, "ma_nv", "ma_nhan_vien")
    if not ma_nhan_vien_lap:
        raise BadRequestException("Không xác định được nhân viên lập lịch")

    schedule = LichBaoTri(
        ma_lich_bao_tri=_generate_code("LBT"),
        ma_mat_bang=payload.ma_mat_bang,
        ma_nhan_vien_lap=ma_nhan_vien_lap,
        ma_nhan_vien_thuc_hien=payload.ma_nhan_vien_thuc_hien,
        ngay_lap=current_datetime(),
        ngay_thuc_hien_du_kien=payload.ngay_thuc_hien_du_kien,
        noi_dung=payload.noi_dung,
        trang_thai=LichBaoTriStatus.CHUA_THUC_HIEN.value,
        ket_qua=None,
        chi_phi=None,
    )

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.add(schedule)
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="LICHBT",
            ma_doi_tuong=schedule.ma_lich_bao_tri,
            chi_tiet="Lập lịch bảo trì",
        )
    return schedule


def list_maintenance_schedules(
    db: Session,
    filters: LichBaoTriFilter,
    current_user: Any,
) -> Dict[str, Any]:
    """Liệt kê lịch bảo trì theo phạm vi vai trò."""
    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = []
    if _role_value(current_user) == RoleCode.NV_VHBT.value:
        conditions.append(LichBaoTri.ma_nhan_vien_thuc_hien == _user_attr(current_user, "ma_nv", "ma_nhan_vien"))
    if filters.ma_mat_bang:
        conditions.append(LichBaoTri.ma_mat_bang == filters.ma_mat_bang)
    if filters.ma_nhan_vien_thuc_hien:
        conditions.append(LichBaoTri.ma_nhan_vien_thuc_hien == filters.ma_nhan_vien_thuc_hien)
    if filters.trang_thai:
        conditions.append(LichBaoTri.trang_thai == _enum_value(filters.trang_thai))

    stmt = select(LichBaoTri)
    count_stmt = select(func.count()).select_from(LichBaoTri)
    if conditions:
        clause = and_(*conditions)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(
        stmt.order_by(LichBaoTri.ngay_thuc_hien_du_kien.desc())
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


def get_maintenance_schedule_detail(
    db: Session,
    ma_lich_bt: str,
    current_user: Any,
) -> LichBaoTri:
    """Lấy chi tiết lịch bảo trì theo phạm vi truy cập."""
    schedule = db.execute(
        select(LichBaoTri).where(LichBaoTri.ma_lich_bao_tri == ma_lich_bt)
    ).scalars().first()
    if schedule is None:
        raise NotFoundException("Không tìm thấy lịch bảo trì")
    if _role_value(current_user) == RoleCode.NV_VHBT.value:
        if schedule.ma_nhan_vien_thuc_hien != _user_attr(current_user, "ma_nv", "ma_nhan_vien"):
            raise ForbiddenException("Nhân viên chỉ được xem lịch được phân công")
    return schedule
