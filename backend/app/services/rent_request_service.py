# File: app/services/rent_request_service.py
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.constants.statuses import AuditAction, HopDongStatus, MatBangStatus, YeuCauThueThemStatus
from app.exceptions.business_exceptions import BadRequestException, ConflictException, ForbiddenException, InvalidStateException, NotFoundException
from app.models import HopDong, MatBang, YeuCauThueThem
from app.schemas.yc_thuethem import DuyetYeuCauThueThemRequest, YeuCauThueThemCreate, YeuCauThueThemFilter
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


def create_rent_request(
    db: Session,
    payload: YeuCauThueThemCreate,
    current_user: Any,
) -> YeuCauThueThem:
    """Tạo yêu cầu thuê thêm cho khách thuê đang có hợp đồng hiệu lực."""
    ma_khach_thue = _user_attr(current_user, "ma_kh", "ma_khach_thue")
    if not ma_khach_thue:
        raise ForbiddenException("Tài khoản hiện tại không phải khách thuê")

    active_contract = db.execute(
        select(HopDong).where(
            HopDong.ma_khach_thue == ma_khach_thue,
            HopDong.trang_thai == HopDongStatus.DANG_HIEU_LUC.value,
        )
    ).scalars().first()
    if active_contract is None:
        raise InvalidStateException("Khách thuê chưa có hợp đồng đang hiệu lực")

    premise = db.execute(
        select(MatBang).where(MatBang.ma_mat_bang == payload.ma_mat_bang)
    ).scalars().first()
    if premise is None:
        raise NotFoundException("Không tìm thấy mặt bằng")
    if premise.trang_thai != MatBangStatus.CON_TRONG.value:
        raise InvalidStateException("Mặt bằng hiện không còn trống")

    pending_request = db.execute(
        select(YeuCauThueThem).where(
            YeuCauThueThem.ma_khach_thue == ma_khach_thue,
            YeuCauThueThem.ma_mat_bang == payload.ma_mat_bang,
            YeuCauThueThem.trang_thai == YeuCauThueThemStatus.CHO_DUYET.value,
        )
    ).scalars().first()
    if pending_request is not None:
        raise ConflictException("Đã tồn tại yêu cầu chờ duyệt cho mặt bằng này")

    request = YeuCauThueThem(
        ma_yeu_cau=_generate_code("YC"),
        ma_khach_thue=ma_khach_thue,
        ma_mat_bang=payload.ma_mat_bang,
        ngay_gui=current_datetime(),
        ly_do=payload.ly_do,
        trang_thai=YeuCauThueThemStatus.CHO_DUYET.value,
    )
    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.add(request)
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="YC_THUETHEM",
            ma_doi_tuong=request.ma_yeu_cau,
            chi_tiet="Gửi yêu cầu thuê thêm mặt bằng",
        )
    return request


def list_rent_requests(
    db: Session,
    filters: YeuCauThueThemFilter,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Liệt kê yêu cầu thuê thêm dành cho BQL."""
    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = []
    if filters.ma_khach_thue:
        conditions.append(YeuCauThueThem.ma_khach_thue == filters.ma_khach_thue)
    if filters.ma_mat_bang:
        conditions.append(YeuCauThueThem.ma_mat_bang == filters.ma_mat_bang)
    if filters.trang_thai:
        conditions.append(YeuCauThueThem.trang_thai == _enum_value(filters.trang_thai))

    stmt = select(YeuCauThueThem)
    count_stmt = select(func.count()).select_from(YeuCauThueThem)
    if conditions:
        clause = and_(*conditions)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(
        stmt.order_by(YeuCauThueThem.ngay_gui.desc())
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


def list_my_rent_requests(
    db: Session,
    filters: YeuCauThueThemFilter,
    current_user: Any,
) -> Dict[str, Any]:
    """Liệt kê yêu cầu thuê thêm của khách thuê hiện tại."""
    ma_khach_thue = _user_attr(current_user, "ma_kh", "ma_khach_thue")
    if not ma_khach_thue:
        raise ForbiddenException("Tài khoản hiện tại không phải khách thuê")

    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = [YeuCauThueThem.ma_khach_thue == ma_khach_thue]
    if filters.ma_mat_bang:
        conditions.append(YeuCauThueThem.ma_mat_bang == filters.ma_mat_bang)
    if filters.trang_thai:
        conditions.append(YeuCauThueThem.trang_thai == _enum_value(filters.trang_thai))

    clause = and_(*conditions)
    total = db.execute(
        select(func.count()).select_from(YeuCauThueThem).where(clause)
    ).scalar_one()
    items = db.execute(
        select(YeuCauThueThem)
        .where(clause)
        .order_by(YeuCauThueThem.ngay_gui.desc())
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


def review_rent_request(
    db: Session,
    ma_yc: str,
    payload: DuyetYeuCauThueThemRequest,
    current_user: Any,
) -> YeuCauThueThem:
    """Duyệt hoặc từ chối yêu cầu thuê thêm đang chờ xử lý."""
    request = db.execute(
        select(YeuCauThueThem).where(YeuCauThueThem.ma_yeu_cau == ma_yc)
    ).scalars().first()
    if request is None:
        raise NotFoundException("Không tìm thấy yêu cầu thuê thêm")
    if request.trang_thai != YeuCauThueThemStatus.CHO_DUYET.value:
        raise InvalidStateException("Yêu cầu thuê thêm không còn ở trạng thái chờ duyệt")

    ma_nhan_vien = _user_attr(current_user, "ma_nv", "ma_nhan_vien")
    if not ma_nhan_vien:
        raise BadRequestException("Không xác định được nhân viên duyệt")

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        request.ma_nhan_vien_duyet = ma_nhan_vien
        request.ngay_duyet = current_datetime()
        if payload.ket_qua == "DUYET":
            request.trang_thai = YeuCauThueThemStatus.DA_DUYET_CHO_SO_HOA_HOP_DONG.value
            request.ghi_chu = payload.ghi_chu_cho_kdtc
            action_detail = "Duyệt yêu cầu thuê thêm"
        else:
            request.trang_thai = YeuCauThueThemStatus.TU_CHOI.value
            request.ly_do_tu_choi = payload.ly_do_tu_choi
            action_detail = "Từ chối yêu cầu thuê thêm"

        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.DUYET,
            doi_tuong="YC_THUETHEM",
            ma_doi_tuong=request.ma_yeu_cau,
            chi_tiet=action_detail,
        )
    return request
