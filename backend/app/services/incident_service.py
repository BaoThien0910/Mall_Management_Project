# File: app/services/incident_service.py
import uuid
from typing import Any, Dict, List

from sqlalchemy import and_, func, select, or_
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.constants.statuses import AuditAction, HopDongStatus, SuCoBaoTriStatus
from app.exceptions.business_exceptions import BadRequestException, ForbiddenException, InvalidStateException, NotFoundException
from app.models import HopDong, NhanVien, SuCoBaoTri
from app.schemas.sk_baotri import CapNhatKetQuaXuLySuCoRequest, DuyetSuCoBaoTriRequest, NhapChiPhiBaoTriRequest, PhanCongSuCoBaoTriRequest, SuCoBaoTriCreate, SuCoBaoTriFilter
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


def create_incident(
    db: Session,
    payload: SuCoBaoTriCreate,
    current_user: Any,
) -> SuCoBaoTri:
    """Tạo sự cố bảo trì từ khách thuê."""
    ma_khach_thue = _user_attr(current_user, "ma_kh", "ma_khach_thue")
    if not ma_khach_thue:
        raise ForbiddenException("Tài khoản hiện tại không phải khách thuê")

    active_contract = db.execute(
        select(HopDong).where(
            HopDong.ma_khach_thue == ma_khach_thue,
            HopDong.ma_mat_bang == payload.ma_mat_bang,
            HopDong.trang_thai == HopDongStatus.DANG_HIEU_LUC.value,
        )
    ).scalars().first()
    if active_contract is None:
        raise ForbiddenException("Mặt bằng không thuộc hợp đồng đang hiệu lực của khách thuê")

    incident = SuCoBaoTri(
        ma_su_co=_generate_code("SC"),
        ma_mat_bang=payload.ma_mat_bang,
        ma_khach_thue=ma_khach_thue,
        ngay_gui=current_datetime(),
        mo_ta=payload.mo_ta,
        trang_thai=SuCoBaoTriStatus.CHO_DUYET.value,
    )
    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.add(incident)
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="SK_BAOTRI",
            ma_doi_tuong=incident.ma_su_co,
            chi_tiet="Gửi yêu cầu xử lý sự cố bảo trì",
        )
    return incident


def list_incidents(
    db: Session,
    filters: SuCoBaoTriFilter,
    current_user: Any,
) -> Dict[str, Any]:
    """Liệt kê sự cố theo phạm vi dữ liệu của người dùng hiện tại."""
    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = []
    role = _role_value(current_user)

    if role == RoleCode.NV_VHBT.value:
        conditions.append(SuCoBaoTri.ma_nhan_vien_xu_ly == _user_attr(current_user, "ma_nv", "ma_nhan_vien"))
    elif role == RoleCode.KHACH_THUE.value:
        conditions.append(SuCoBaoTri.ma_khach_thue == _user_attr(current_user, "ma_kh", "ma_khach_thue"))

    if filters.ma_mat_bang:
        conditions.append(SuCoBaoTri.ma_mat_bang == filters.ma_mat_bang)
    if filters.ma_khach_thue:
        conditions.append(SuCoBaoTri.ma_khach_thue == filters.ma_khach_thue)
    if filters.trang_thai:
        status_list = [s.strip() for s in filters.trang_thai.split(",") if s.strip()]
        if status_list:
            conditions.append(SuCoBaoTri.trang_thai.in_(status_list))
    if filters.ma_nhan_vien_xu_ly:
        conditions.append(SuCoBaoTri.ma_nhan_vien_xu_ly == filters.ma_nhan_vien_xu_ly)

    from datetime import time, datetime
    if filters.tu_ngay:
        conditions.append(SuCoBaoTri.ngay_gui >= filters.tu_ngay)
    if filters.den_ngay:
        if filters.den_ngay.time() == time.min:
            den_ngay_dt = datetime.combine(filters.den_ngay.date(), time.max)
            conditions.append(SuCoBaoTri.ngay_gui <= den_ngay_dt)
        else:
            conditions.append(SuCoBaoTri.ngay_gui <= filters.den_ngay)

    if filters.keyword:
        conditions.append(
            or_(
                SuCoBaoTri.ma_mat_bang.ilike(f"%{filters.keyword}%"),
                SuCoBaoTri.ma_khach_thue.ilike(f"%{filters.keyword}%"),
            )
        )

    stmt = select(SuCoBaoTri)
    count_stmt = select(func.count()).select_from(SuCoBaoTri)
    if conditions:
        clause = and_(*conditions)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = db.execute(count_stmt).scalar_one()

    # Determine order clause
    order_clause = SuCoBaoTri.ngay_gui.desc()
    if filters.sort_by == "trang_thai":
        order_clause = SuCoBaoTri.trang_thai.asc() if filters.order == "asc" else SuCoBaoTri.trang_thai.desc()
    elif filters.sort_by == "ngay_gui":
        order_clause = SuCoBaoTri.ngay_gui.asc() if filters.order == "asc" else SuCoBaoTri.ngay_gui.desc()

    items = db.execute(
        stmt.order_by(order_clause)
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


def review_incident(
    db: Session,
    ma_su_co: str,
    payload: DuyetSuCoBaoTriRequest,
    current_user: Any,
) -> SuCoBaoTri:
    """Duyệt hoặc từ chối sự cố bảo trì đang chờ xử lý."""
    incident = db.execute(
        select(SuCoBaoTri).where(SuCoBaoTri.ma_su_co == ma_su_co)
    ).scalars().first()
    if incident is None:
        raise NotFoundException("Không tìm thấy sự cố bảo trì")
    if incident.trang_thai != SuCoBaoTriStatus.CHO_DUYET.value:
        raise InvalidStateException("Sự cố không còn ở trạng thái chờ duyệt")

    ma_nhan_vien_duyet = _user_attr(current_user, "ma_nv", "ma_nhan_vien")
    if not ma_nhan_vien_duyet:
        raise BadRequestException("Không xác định được nhân viên duyệt")

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        incident.ma_nhan_vien_duyet = ma_nhan_vien_duyet
        incident.ngay_duyet = current_datetime()
        if payload.ket_qua == "DUYET":
            incident.trang_thai = SuCoBaoTriStatus.DA_DUYET.value
            detail = "Duyệt sự cố bảo trì"
        else:
            incident.trang_thai = SuCoBaoTriStatus.TU_CHOI.value
            incident.ly_do_tu_choi = payload.ly_do_tu_choi
            detail = "Từ chối sự cố bảo trì"
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.DUYET,
            doi_tuong="SK_BAOTRI",
            ma_doi_tuong=incident.ma_su_co,
            chi_tiet=detail,
        )
    return incident


def assign_incident(
    db: Session,
    ma_su_co: str,
    payload: PhanCongSuCoBaoTriRequest,
    current_user: Any,
) -> SuCoBaoTri:
    """Phân công sự cố đã duyệt cho nhân viên Vận hành - Bảo trì."""
    incident = db.execute(
        select(SuCoBaoTri).where(SuCoBaoTri.ma_su_co == ma_su_co)
    ).scalars().first()
    if incident is None:
        raise NotFoundException("Không tìm thấy sự cố bảo trì")
    if incident.trang_thai != SuCoBaoTriStatus.DA_DUYET.value:
        raise InvalidStateException("Chỉ sự cố đã duyệt mới được phân công")

    assignee = db.execute(
        select(NhanVien).where(NhanVien.ma_nhan_vien == payload.ma_nhan_vien_xu_ly)
    ).scalars().first()
    if assignee is None:
        raise NotFoundException("Không tìm thấy nhân viên xử lý")
    if assignee.phong_ban != "Vận hành - Bảo trì":
        raise BadRequestException("Nhân viên xử lý không thuộc phòng Vận hành - Bảo trì")

    ma_nhan_vien_phan_cong = _user_attr(current_user, "ma_nv", "ma_nhan_vien")
    if not ma_nhan_vien_phan_cong:
        raise BadRequestException("Không xác định được nhân viên phân công")

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        incident.ma_nhan_vien_phan_cong = ma_nhan_vien_phan_cong
        incident.ma_nhan_vien_xu_ly = payload.ma_nhan_vien_xu_ly
        incident.ngay_phan_cong = current_datetime()
        incident.trang_thai = SuCoBaoTriStatus.DANG_XU_LY.value
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.CAP_NHAT,
            doi_tuong="SK_BAOTRI",
            ma_doi_tuong=incident.ma_su_co,
            chi_tiet="Phân công xử lý sự cố bảo trì",
        )
    return incident


def update_incident_result(
    db: Session,
    ma_su_co: str,
    payload: CapNhatKetQuaXuLySuCoRequest,
    current_user: Any,
) -> SuCoBaoTri:
    """Cập nhật kết quả xử lý sự cố và hoàn thành quy trình."""
    incident = db.execute(
        select(SuCoBaoTri).where(SuCoBaoTri.ma_su_co == ma_su_co)
    ).scalars().first()
    if incident is None:
        raise NotFoundException("Không tìm thấy sự cố bảo trì")
    if incident.trang_thai != SuCoBaoTriStatus.DANG_XU_LY.value:
        raise InvalidStateException("Sự cố chưa ở trạng thái đang xử lý")

    role = _role_value(current_user)
    if role == RoleCode.NV_VHBT.value:
        if incident.ma_nhan_vien_xu_ly != _user_attr(current_user, "ma_nv", "ma_nhan_vien"):
            raise ForbiddenException("Nhân viên chỉ được cập nhật sự cố được phân công cho mình")

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        incident.ket_qua = payload.ket_qua
        incident.ngay_hoan_thanh = payload.ngay_hoan_thanh
        incident.trang_thai = SuCoBaoTriStatus.HOAN_THANH.value
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.CAP_NHAT,
            doi_tuong="SK_BAOTRI",
            ma_doi_tuong=incident.ma_su_co,
            chi_tiet="Cập nhật kết quả xử lý sự cố",
        )
    return incident


def update_incident_cost(
    db: Session,
    ma_su_co: str,
    payload: NhapChiPhiBaoTriRequest,
    current_user: Any,
) -> SuCoBaoTri:
    """Cập nhật chi phí cho sự cố đang xử lý hoặc đã hoàn thành."""
    incident = db.execute(
        select(SuCoBaoTri).where(SuCoBaoTri.ma_su_co == ma_su_co)
    ).scalars().first()
    if incident is None:
        raise NotFoundException("Không tìm thấy sự cố bảo trì")
    if incident.trang_thai not in {SuCoBaoTriStatus.DANG_XU_LY.value, SuCoBaoTriStatus.HOAN_THANH.value}:
        raise InvalidStateException("Trạng thái sự cố không cho phép nhập chi phí")

    role = _role_value(current_user)
    if role == RoleCode.NV_VHBT.value:
        if incident.ma_nhan_vien_xu_ly != _user_attr(current_user, "ma_nv", "ma_nhan_vien"):
            raise ForbiddenException("Nhân viên chỉ được nhập chi phí cho sự cố được phân công")

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        incident.chi_phi = payload.chi_phi
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.CAP_NHAT,
            doi_tuong="SK_BAOTRI",
            ma_doi_tuong=incident.ma_su_co,
            chi_tiet="Nhập chi phí bảo trì cho sự cố",
        )
    return incident
