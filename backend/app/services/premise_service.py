# File: app/services/premise_service.py
from typing import Any, Dict, List

from sqlalchemy import and_, func, select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.constants.statuses import AuditAction, HopDongStatus, MatBangStatus
from app.exceptions.business_exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models import HopDong, MatBang
from app.schemas.matbang import MatBangCreate, MatBangFilter, MatBangUpdate
from app.services.audit_service import write_audit_log
from app.utils.pagination import calculate_offset, calculate_total_pages, normalize_pagination
from app.utils.transaction import commit_or_rollback, transaction_context


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _user_attr(current_user: Any, short_name: str, long_name: str) -> Any:
    value = getattr(current_user, short_name, None)
    return value if value is not None else getattr(current_user, long_name, None)


def _role_value(current_user: Any) -> Any:
    return _enum_value(_user_attr(current_user, "ma_vai_tro", "ma_vai_tro"))


def list_premises(
    db: Session,
    filters: MatBangFilter,
    current_user: Any,
) -> Dict[str, Any]:
    """Liệt kê mặt bằng với giới hạn dữ liệu dành cho khách thuê."""
    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = []

    if filters.keyword:
        conditions.append(
            or_(
                MatBang.ma_mat_bang.ilike(f"%{filters.keyword}%"),
                MatBang.vi_tri.ilike(f"%{filters.keyword}%"),
            )
        )

    if _role_value(current_user) == RoleCode.KHACH_THUE.value:
        conditions.append(MatBang.trang_thai == MatBangStatus.CON_TRONG.value)
    elif filters.trang_thai:
        status_list = [s.strip() for s in filters.trang_thai.split(",") if s.strip()]
        if status_list:
            conditions.append(MatBang.trang_thai.in_(status_list))

    if filters.tang is not None:
        try:
            floor_list = [int(f.strip()) for f in str(filters.tang).split(",") if f.strip()]
            if floor_list:
                conditions.append(MatBang.tang.in_(floor_list))
        except ValueError:
            pass

    if filters.loai_mat_bang:
        type_list = [t.strip() for t in filters.loai_mat_bang.split(",") if t.strip()]
        if type_list:
            type_conditions = [MatBang.loai_mat_bang.ilike(f"%{t}%") for t in type_list]
            conditions.append(or_(*type_conditions))
    if filters.dien_tich_tu is not None:
        conditions.append(MatBang.dien_tich >= filters.dien_tich_tu)
    if filters.dien_tich_den is not None:
        conditions.append(MatBang.dien_tich <= filters.dien_tich_den)

    stmt = select(MatBang)
    count_stmt = select(func.count()).select_from(MatBang)
    if conditions:
        clause = and_(*conditions)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(
        stmt.order_by(MatBang.ma_mat_bang.asc())
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


def get_premise_detail(
    db: Session,
    ma_mb: str,
    current_user: Any,
) -> MatBang:
    """Lấy chi tiết mặt bằng và kiểm tra phạm vi xem của khách thuê."""
    premise = db.execute(
        select(MatBang).where(MatBang.ma_mat_bang == ma_mb)
    ).scalars().first()
    if premise is None:
        raise NotFoundException("Không tìm thấy mặt bằng")

    if (
        _role_value(current_user) == RoleCode.KHACH_THUE.value
        and premise.trang_thai != MatBangStatus.CON_TRONG.value
    ):
        raise ForbiddenException("Khách thuê chỉ được xem mặt bằng còn trống")
    return premise


def create_premise(
    db: Session,
    payload: MatBangCreate,
    current_user: Any,
) -> MatBang:
    """Tạo mới mặt bằng."""
    existing = db.execute(
        select(MatBang).where(MatBang.ma_mat_bang == payload.ma_mat_bang)
    ).scalars().first()
    if existing is not None:
        raise ConflictException("Mã mặt bằng đã tồn tại")

    premise = MatBang(
        ma_mat_bang=payload.ma_mat_bang,
        vi_tri=payload.vi_tri,
        tang=payload.tang,
        dien_tich=payload.dien_tich,
        loai_mat_bang=payload.loai_mat_bang,
        trang_thai=_enum_value(payload.trang_thai),
        ghi_chu=payload.ghi_chu,
    )
    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.add(premise)
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="MATBANG",
            ma_doi_tuong=premise.ma_mat_bang,
            chi_tiet="Tạo mới mặt bằng",
        )
    return premise


def update_premise(
    db: Session,
    ma_mb: str,
    payload: MatBangUpdate,
    current_user: Any,
) -> MatBang:
    """Cập nhật các trường được gửi lên của mặt bằng."""
    premise = db.execute(
        select(MatBang).where(MatBang.ma_mat_bang == ma_mb)
    ).scalars().first()
    if premise is None:
        raise NotFoundException("Không tìm thấy mặt bằng")

    updates = payload.model_dump(exclude_unset=True)
    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        for field_name, value in updates.items():
            setattr(premise, field_name, _enum_value(value))
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.CAP_NHAT,
            doi_tuong="MATBANG",
            ma_doi_tuong=premise.ma_mat_bang,
            chi_tiet="Cập nhật mặt bằng",
        )
    return premise


def delete_premise(
    db: Session,
    ma_mb: str,
    current_user: Any,
) -> Dict[str, Any]:
    """Xóa mặt bằng khi không còn bị ràng buộc bởi hợp đồng hiệu lực."""
    premise = db.execute(
        select(MatBang).where(MatBang.ma_mat_bang == ma_mb)
    ).scalars().first()
    if premise is None:
        raise NotFoundException("Không tìm thấy mặt bằng")

    active_contract = db.execute(
        select(HopDong).where(
            HopDong.ma_mat_bang == ma_mb,
            HopDong.trang_thai == HopDongStatus.DANG_HIEU_LUC.value,
        )
    ).scalars().first()
    if active_contract is not None:
        raise ConflictException("Không thể xóa mặt bằng đang có hợp đồng hiệu lực")

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    try:
        db.delete(premise)
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.XOA,
            doi_tuong="MATBANG",
            ma_doi_tuong=ma_mb,
            chi_tiet="Xóa mặt bằng",
        )
        commit_or_rollback(db)
    except IntegrityError as exc:
        db.rollback()
        raise ConflictException("Không thể xóa mặt bằng do còn dữ liệu liên quan") from exc

    return {"ma_mat_bang": ma_mb, "deleted": True}
