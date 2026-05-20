# File: app/services/contract_service.py
from typing import Any, Dict, List

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.constants.statuses import AuditAction, HopDongStatus, MatBangStatus, YeuCauThueThemStatus
from app.exceptions.business_exceptions import ConflictException, ForbiddenException, InvalidStateException, NotFoundException, BadRequestException
from app.models import HopDong, KhachThue, MatBang, YeuCauThueThem
from app.schemas.hopdong import HopDongCreate, HopDongCuaToiFilter, HopDongFilter
from app.services.audit_service import write_audit_log
from app.utils.datetime_helper import current_datetime
from app.utils.pagination import calculate_offset, calculate_total_pages, normalize_pagination
from app.utils.transaction import transaction_context


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _user_attr(current_user: Any, short_name: str, long_name: str) -> Any:
    value = getattr(current_user, short_name, None)
    return value if value is not None else getattr(current_user, long_name, None)


def _role_value(current_user: Any) -> Any:
    return _enum_value(_user_attr(current_user, "ma_vai_tro", "ma_vai_tro"))


def list_contracts(
    db: Session,
    filters: HopDongFilter,
    current_user: Any,
) -> Dict[str, Any]:
    """Liệt kê hợp đồng toàn hệ thống cho nhóm quản lý được phép."""
    if _role_value(current_user) == RoleCode.KHACH_THUE.value:
        raise ForbiddenException("Khách thuê không được xem danh sách toàn bộ hợp đồng")

    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = []
    if filters.ma_khach_thue:
        conditions.append(HopDong.ma_khach_thue == filters.ma_khach_thue)
    if filters.ma_mat_bang:
        conditions.append(HopDong.ma_mat_bang == filters.ma_mat_bang)
    if filters.trang_thai:
        conditions.append(HopDong.trang_thai == _enum_value(filters.trang_thai))
    if filters.ngay_bat_dau_tu:
        conditions.append(HopDong.ngay_bat_dau >= filters.ngay_bat_dau_tu)
    if filters.ngay_bat_dau_den:
        conditions.append(HopDong.ngay_bat_dau <= filters.ngay_bat_dau_den)

    stmt = select(HopDong)
    count_stmt = select(func.count()).select_from(HopDong)
    if conditions:
        clause = and_(*conditions)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(
        stmt.order_by(HopDong.ngay_so_hoa.desc())
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


def get_contract_detail(
    db: Session,
    ma_hd: str,
    current_user: Any,
) -> HopDong:
    """Lấy chi tiết hợp đồng cho nhóm quản trị tài chính."""
    if _role_value(current_user) == RoleCode.KHACH_THUE.value:
        raise ForbiddenException("Khách thuê không được dùng endpoint xem chi tiết nội bộ")

    contract = db.execute(
        select(HopDong).where(HopDong.ma_hop_dong == ma_hd)
    ).scalars().first()
    if contract is None:
        raise NotFoundException("Không tìm thấy hợp đồng")
    return contract


def list_my_contracts(
    db: Session,
    filters: HopDongCuaToiFilter,
    current_user: Any,
) -> Dict[str, Any]:
    """Liệt kê hợp đồng thuộc về khách thuê hiện tại."""
    ma_khach_thue = _user_attr(current_user, "ma_kh", "ma_khach_thue")
    if not ma_khach_thue:
        raise ForbiddenException("Tài khoản hiện tại không phải khách thuê")

    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = [HopDong.ma_khach_thue == ma_khach_thue]
    if filters.trang_thai:
        conditions.append(HopDong.trang_thai == _enum_value(filters.trang_thai))

    clause = and_(*conditions)
    total = db.execute(
        select(func.count()).select_from(HopDong).where(clause)
    ).scalar_one()
    items = db.execute(
        select(HopDong)
        .where(clause)
        .order_by(HopDong.ngay_so_hoa.desc())
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


def create_contract(
    db: Session,
    payload: HopDongCreate,
    current_user: Any,
) -> HopDong:
    """Tạo hợp đồng mới, cập nhật mặt bằng và yêu cầu thuê thêm nếu có."""
    tenant = db.execute(
        select(KhachThue).where(KhachThue.ma_khach_thue == payload.ma_khach_thue)
    ).scalars().first()
    if tenant is None:
        raise NotFoundException("Không tìm thấy khách thuê")

    premise = db.execute(
        select(MatBang).where(MatBang.ma_mat_bang == payload.ma_mat_bang)
    ).scalars().first()
    if premise is None:
        raise NotFoundException("Không tìm thấy mặt bằng")

    active_contract = db.execute(
        select(HopDong).where(
            HopDong.ma_mat_bang == payload.ma_mat_bang,
            HopDong.trang_thai == HopDongStatus.DANG_HIEU_LUC.value,
        )
    ).scalars().first()
    if active_contract is not None:
        raise ConflictException("Mặt bằng đã có hợp đồng đang hiệu lực")

    duplicate_contract = db.execute(
        select(HopDong).where(HopDong.ma_hop_dong == payload.ma_hop_dong)
    ).scalars().first()
    if duplicate_contract is not None:
        raise ConflictException("Mã hợp đồng đã tồn tại")

    ma_nhan_vien_so_hoa = _user_attr(current_user, "ma_nv", "ma_nhan_vien")
    if not ma_nhan_vien_so_hoa:
        raise BadRequestException("Không xác định được nhân viên số hóa hợp đồng")

    rent_request = None
    if payload.ma_yeu_cau:
        rent_request = db.execute(
            select(YeuCauThueThem).where(YeuCauThueThem.ma_yeu_cau == payload.ma_yeu_cau)
        ).scalars().first()
        if rent_request is None:
            raise NotFoundException("Không tìm thấy yêu cầu thuê thêm")
        if rent_request.trang_thai != YeuCauThueThemStatus.DA_DUYET_CHO_SO_HOA_HOP_DONG.value:
            raise InvalidStateException("Yêu cầu thuê thêm chưa ở trạng thái được tạo hợp đồng")
        if rent_request.ma_khach_thue != payload.ma_khach_thue:
            raise BadRequestException("Yêu cầu thuê thêm không thuộc đúng khách thuê")
        if rent_request.ma_mat_bang != payload.ma_mat_bang:
            raise BadRequestException("Yêu cầu thuê thêm không thuộc đúng mặt bằng")

    contract = HopDong(
        ma_hop_dong=payload.ma_hop_dong,
        ma_khach_thue=payload.ma_khach_thue,
        ma_mat_bang=payload.ma_mat_bang,
        ma_nhan_vien_so_hoa=ma_nhan_vien_so_hoa,
        ma_yeu_cau=payload.ma_yeu_cau,
        ngay_bat_dau=payload.ngay_bat_dau,
        ngay_ket_thuc=payload.ngay_ket_thuc,
        gia_thue_thang=payload.gia_thue_thang,
        trang_thai=HopDongStatus.DANG_HIEU_LUC.value,
        ngay_so_hoa=current_datetime(),
    )

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.add(contract)
        premise.trang_thai = MatBangStatus.DANG_THUE.value
        if rent_request is not None:
            rent_request.trang_thai = YeuCauThueThemStatus.DA_TAO_HOP_DONG.value
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="HOPDONG",
            ma_doi_tuong=contract.ma_hop_dong,
            chi_tiet="Tạo hợp đồng và cập nhật trạng thái liên quan",
        )
    return contract
