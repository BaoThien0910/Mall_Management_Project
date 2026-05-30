# File: app/services/notification_service.py
import uuid
from typing import Any, Dict, List

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.constants.statuses import AuditAction, DoiTuongNhanThongBao, ThongBaoStatus
from app.exceptions.business_exceptions import ForbiddenException, InvalidStateException, NotFoundException, BadRequestException
from app.models import ThongBao
from app.schemas.thongbao import ThongBaoCreate, ThongBaoFilter, ThuHoiThongBaoRequest
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


def _visibility_clause(current_user: Any) -> Any:
    role = _role_value(current_user)
    if role == RoleCode.KHACH_THUE.value:
        return or_(
            ThongBao.doi_tuong_nhan == DoiTuongNhanThongBao.TOAN_HE_THONG.value,
            ThongBao.doi_tuong_nhan == DoiTuongNhanThongBao.KHACH_THUE.value,
        )
    return or_(
        ThongBao.doi_tuong_nhan == DoiTuongNhanThongBao.TOAN_HE_THONG.value,
        ThongBao.doi_tuong_nhan == DoiTuongNhanThongBao.NOI_BO.value,
    )


def _can_view_announcement(announcement: ThongBao, current_user: Any) -> bool:
    role = _role_value(current_user)
    if announcement.doi_tuong_nhan == DoiTuongNhanThongBao.TOAN_HE_THONG.value:
        return True
    if announcement.doi_tuong_nhan == DoiTuongNhanThongBao.NOI_BO.value:
        return role != RoleCode.KHACH_THUE.value
    if announcement.doi_tuong_nhan == DoiTuongNhanThongBao.KHACH_THUE.value:
        return role == RoleCode.KHACH_THUE.value
    return False


def create_announcement(
    db: Session,
    payload: ThongBaoCreate,
    current_user: Any,
) -> ThongBao:
    """Ban hành thông báo, kế hoạch hoặc quy định."""
    ma_nhan_vien_ban_hanh = _user_attr(current_user, "ma_nv", "ma_nhan_vien")
    if not ma_nhan_vien_ban_hanh:
        raise BadRequestException("Không xác định được nhân viên ban hành")

    announcement = ThongBao(
        ma_thong_bao=_generate_code("TB"),
        ma_nhan_vien_ban_hanh=ma_nhan_vien_ban_hanh,
        tieu_de=payload.tieu_de,
        noi_dung=payload.noi_dung,
        loai_thong_bao=_enum_value(payload.loai_thong_bao),
        doi_tuong_nhan=_enum_value(payload.doi_tuong_nhan),
        ngay_ban_hanh=current_datetime(),
        trang_thai=ThongBaoStatus.DA_BAN_HANH.value,
    )
    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.add(announcement)
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="THONGBAO",
            ma_doi_tuong=announcement.ma_thong_bao,
            chi_tiet="Ban hành thông báo",
        )
    return announcement


def list_announcements(
    db: Session,
    filters: ThongBaoFilter,
    current_user: Any,
) -> Dict[str, Any]:
    """Liệt kê thông báo theo phạm vi người nhận."""
    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = [_visibility_clause(current_user)]
    if filters.loai_thong_bao:
        conditions.append(ThongBao.loai_thong_bao == _enum_value(filters.loai_thong_bao))
    if filters.doi_tuong_nhan:
        conditions.append(ThongBao.doi_tuong_nhan == _enum_value(filters.doi_tuong_nhan))
    if filters.trang_thai:
        conditions.append(ThongBao.trang_thai == _enum_value(filters.trang_thai))

    clause = and_(*conditions)
    total = db.execute(
        select(func.count()).select_from(ThongBao).where(clause)
    ).scalar_one()
    items = db.execute(
        select(ThongBao)
        .where(clause)
        .order_by(ThongBao.ngay_ban_hanh.desc())
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


def get_announcement_detail(
    db: Session,
    ma_tb: str,
    current_user: Any,
) -> ThongBao:
    """Lấy chi tiết thông báo nếu người dùng thuộc nhóm được xem."""
    announcement = db.execute(
        select(ThongBao).where(ThongBao.ma_thong_bao == ma_tb)
    ).scalars().first()
    if announcement is None:
        raise NotFoundException("Không tìm thấy thông báo")
    if not _can_view_announcement(announcement, current_user):
        raise ForbiddenException("Người dùng không thuộc nhóm được xem thông báo")
    return announcement


def revoke_announcement(
    db: Session,
    ma_tb: str,
    payload: ThuHoiThongBaoRequest,
    current_user: Any,
) -> ThongBao:
    """Thu hồi thông báo đã ban hành mà không sửa nội dung gốc."""
    announcement = db.execute(
        select(ThongBao).where(ThongBao.ma_thong_bao == ma_tb)
    ).scalars().first()
    if announcement is None:
        raise NotFoundException("Không tìm thấy thông báo")
    if announcement.trang_thai != ThongBaoStatus.DA_BAN_HANH.value:
        raise InvalidStateException("Chỉ thông báo đã ban hành mới được thu hồi")

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        announcement.trang_thai = ThongBaoStatus.DA_THU_HOI.value
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.CAP_NHAT,
            doi_tuong="THONGBAO",
            ma_doi_tuong=announcement.ma_thong_bao,
            chi_tiet=payload.ly_do or "Thu hồi thông báo",
        )
    return announcement
