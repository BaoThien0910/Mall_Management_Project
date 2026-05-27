# File: app/services/account_service.py
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.constants.statuses import AuditAction
from app.exceptions.business_exceptions import ConflictException, InvalidStateException, NotFoundException
from app.models import HopDong, KhachThue, NhanVien, TaiKhoan, VaiTro
from app.schemas.taikhoan import TaiKhoanCreate, TaiKhoanDisableRequest, TaiKhoanEnableRequest, TaiKhoanFilter
from app.services.audit_service import write_audit_log
from app.utils.datetime_helper import current_datetime
from app.utils.pagination import calculate_offset, calculate_total_pages, normalize_pagination
from app.utils.security import hash_password
from app.utils.transaction import transaction_context


_ACCOUNT_ACTIVE = "Hoạt động"
_ACCOUNT_DISABLED = "Vô hiệu"


def _generate_code(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"


def _user_attr(current_user: Any, short_name: str, long_name: str) -> Any:
    value = getattr(current_user, short_name, None)
    return value if value is not None else getattr(current_user, long_name, None)


def list_accounts(
    db: Session,
    filters: TaiKhoanFilter,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Liệt kê tài khoản theo bộ lọc và phân trang."""
    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = []

    if filters.keyword:
        conditions.append(TaiKhoan.ten_dang_nhap.ilike(f"%{filters.keyword}%"))
    if filters.ma_vai_tro:
        conditions.append(TaiKhoan.ma_vai_tro == filters.ma_vai_tro)
    if filters.trang_thai:
        conditions.append(TaiKhoan.trang_thai == filters.trang_thai)

    stmt = select(TaiKhoan)
    count_stmt = select(func.count()).select_from(TaiKhoan)
    if conditions:
        clause = and_(*conditions)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(
        stmt.order_by(TaiKhoan.ngay_tao.desc())
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


def create_account(
    db: Session,
    payload: TaiKhoanCreate,
    current_user: Any,
) -> TaiKhoan:
    """Tạo tài khoản nhân viên hoặc khách thuê theo quy tắc nghiệp vụ."""
    existing_account = db.execute(
        select(TaiKhoan).where(TaiKhoan.ten_dang_nhap == payload.ten_dang_nhap)
    ).scalars().first()
    if existing_account is not None:
        raise ConflictException("Tên đăng nhập đã tồn tại")

    role = db.execute(
        select(VaiTro).where(VaiTro.ma_vai_tro == payload.ma_vai_tro)
    ).scalars().first()
    if role is None:
        raise NotFoundException("Không tìm thấy vai trò")

    if payload.ma_nhan_vien:
        employee = db.execute(
            select(NhanVien).where(NhanVien.ma_nhan_vien == payload.ma_nhan_vien)
        ).scalars().first()
        if employee is None:
            raise NotFoundException("Không tìm thấy nhân viên")

        linked_account = db.execute(
            select(TaiKhoan).where(TaiKhoan.ma_nhan_vien == payload.ma_nhan_vien)
        ).scalars().first()
        if linked_account is not None:
            raise ConflictException("Nhân viên đã có tài khoản")

    if payload.ma_khach_thue:
        tenant = db.execute(
            select(KhachThue).where(KhachThue.ma_khach_thue == payload.ma_khach_thue)
        ).scalars().first()
        if tenant is None:
            raise NotFoundException("Không tìm thấy khách thuê")

        linked_account = db.execute(
            select(TaiKhoan).where(TaiKhoan.ma_khach_thue == payload.ma_khach_thue)
        ).scalars().first()
        if linked_account is not None:
            raise ConflictException("Khách thuê đã có tài khoản")

        digitized_contract = db.execute(
            select(HopDong).where(HopDong.ma_khach_thue == payload.ma_khach_thue)
        ).scalars().first()
        if digitized_contract is None:
            raise InvalidStateException("Khách thuê chưa có hợp đồng được số hóa")

    account = TaiKhoan(
        ma_tai_khoan=_generate_code("TK"),
        ten_dang_nhap=payload.ten_dang_nhap,
        mat_khau=hash_password(payload.mat_khau_tam),
        trang_thai=_ACCOUNT_ACTIVE,
        bat_buoc_doi_mk=True,
        so_lan_dang_nhap_sai=0,
        khoa_den=None,
        ma_nhan_vien=payload.ma_nhan_vien,
        ma_khach_thue=payload.ma_khach_thue,
        ma_vai_tro=payload.ma_vai_tro,
        ngay_tao=current_datetime(),
    )

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.add(account)
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="TAIKHOAN",
            ma_doi_tuong=account.ma_tai_khoan,
            chi_tiet="Tạo tài khoản",
        )
    return account


def disable_account(
    db: Session,
    ma_tk: str,
    payload: TaiKhoanDisableRequest,
    current_user: Any,
) -> TaiKhoan:
    """Vô hiệu hóa tài khoản đang hoạt động."""
    account = db.execute(
        select(TaiKhoan).where(TaiKhoan.ma_tai_khoan == ma_tk)
    ).scalars().first()
    if account is None:
        raise NotFoundException("Không tìm thấy tài khoản")
    if account.trang_thai == _ACCOUNT_DISABLED:
        raise InvalidStateException("Tài khoản đã bị vô hiệu hóa")

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        account.trang_thai = _ACCOUNT_DISABLED
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.CAP_NHAT,
            doi_tuong="TAIKHOAN",
            ma_doi_tuong=account.ma_tai_khoan,
            chi_tiet=payload.ly_do or "Vô hiệu hóa tài khoản",
        )
    return account


def enable_account(
    db: Session,
    ma_tk: str,
    payload: TaiKhoanEnableRequest,
    current_user: Any,
) -> TaiKhoan:
    """Khôi phục tài khoản đã bị vô hiệu hóa."""
    account = db.execute(
        select(TaiKhoan).where(TaiKhoan.ma_tai_khoan == ma_tk)
    ).scalars().first()
    if account is None:
        raise NotFoundException("Không tìm thấy tài khoản")
    if account.trang_thai == _ACCOUNT_ACTIVE:
        raise InvalidStateException("Tài khoản đang hoạt động")

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        account.trang_thai = _ACCOUNT_ACTIVE
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.CAP_NHAT,
            doi_tuong="TAIKHOAN",
            ma_doi_tuong=account.ma_tai_khoan,
            chi_tiet=payload.ly_do or "Khôi phục tài khoản",
        )
    return account
