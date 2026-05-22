# File: app/services/auth_service.py
from datetime import timedelta
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants.statuses import AuditAction
from app.exceptions.business_exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models import TaiKhoan
from app.schemas.auth import DangNhapRequest, DoiMatKhauRequest
from app.services.audit_service import write_audit_log
from app.utils.datetime_helper import current_datetime
from app.utils.security import create_access_token, hash_password, is_password_strong, verify_password
from app.utils.transaction import commit_or_rollback, transaction_context


_ACCOUNT_DISABLED = "Vô hiệu"


def _user_attr(current_user: Any, short_name: str, long_name: str) -> Any:
    value = getattr(current_user, short_name, None)
    return value if value is not None else getattr(current_user, long_name, None)


def login(
    db: Session,
    payload: DangNhapRequest,
    ip_address: Optional[str] = None,
) -> Dict[str, Any]:
    """Xác thực tài khoản, cập nhật trạng thái đăng nhập và phát hành JWT."""
    account = db.execute(
        select(TaiKhoan).where(TaiKhoan.ten_dang_nhap == payload.ten_dang_nhap)
    ).scalars().first()

    if account is None:
        # Không ghi audit log do chưa xác định được MATK.
        raise BadRequestException("Tên đăng nhập hoặc mật khẩu không đúng")

    if account.trang_thai == _ACCOUNT_DISABLED:
        raise ForbiddenException("Tài khoản đã bị vô hiệu hóa")

    now = current_datetime()
    if account.khoa_den is not None and account.khoa_den > now:
        raise ForbiddenException("Tài khoản đang bị khóa tạm thời")

    if not verify_password(payload.mat_khau, account.mat_khau):
        account.so_lan_dang_nhap_sai += 1
        if account.so_lan_dang_nhap_sai >= 5:
            account.khoa_den = now + timedelta(minutes=15)

        write_audit_log(
            db=db,
            ma_tk=account.ma_tai_khoan,
            hanh_dong=AuditAction.DANG_NHAP,
            doi_tuong="TAIKHOAN",
            ma_doi_tuong=account.ma_tai_khoan,
            chi_tiet="Đăng nhập thất bại",
            ip_address=ip_address,
        )
        commit_or_rollback(db)
        raise BadRequestException("Tên đăng nhập hoặc mật khẩu không đúng")

    account.so_lan_dang_nhap_sai = 0
    account.khoa_den = None

    token = create_access_token(
        subject=account.ma_tai_khoan,
        extra_claims={
            "ma_tk": account.ma_tai_khoan,
            "ma_vai_tro": account.ma_vai_tro,
            "ma_nv": account.ma_nhan_vien,
            "ma_kh": account.ma_khach_thue,
        },
    )

    write_audit_log(
        db=db,
        ma_tk=account.ma_tai_khoan,
        hanh_dong=AuditAction.DANG_NHAP,
        doi_tuong="TAIKHOAN",
        ma_doi_tuong=account.ma_tai_khoan,
        chi_tiet="Đăng nhập thành công",
        ip_address=ip_address,
    )
    commit_or_rollback(db)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


def logout(
    db: Session,
    current_user: Any,
) -> Dict[str, Any]:
    """Ghi nhận thao tác đăng xuất trong hệ thống JWT stateless."""
    ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        write_audit_log(
            db=db,
            ma_tk=ma_tk,
            hanh_dong=AuditAction.DANG_XUAT,
            doi_tuong="TAIKHOAN",
            ma_doi_tuong=ma_tk,
            chi_tiet="Đăng xuất",
        )
    return {"message": "Đăng xuất thành công"}


def change_password(
    db: Session,
    payload: DoiMatKhauRequest,
    current_user: Any,
) -> TaiKhoan:
    """Đổi mật khẩu hiện tại của tài khoản đang đăng nhập."""
    ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    account = db.execute(
        select(TaiKhoan).where(TaiKhoan.ma_tai_khoan == ma_tk)
    ).scalars().first()
    if account is None:
        raise NotFoundException("Không tìm thấy tài khoản hiện tại")

    if not verify_password(payload.mat_khau_cu, account.mat_khau):
        raise BadRequestException("Mật khẩu hiện tại không đúng")
    if not is_password_strong(payload.mat_khau_moi):
        raise BadRequestException("Mật khẩu mới chưa đáp ứng yêu cầu bảo mật")

    with transaction_context(db):
        account.mat_khau = hash_password(payload.mat_khau_moi)
        account.bat_buoc_doi_mk = False
        write_audit_log(
            db=db,
            ma_tk=account.ma_tai_khoan,
            hanh_dong=AuditAction.CAP_NHAT,
            doi_tuong="TAIKHOAN",
            ma_doi_tuong=account.ma_tai_khoan,
            chi_tiet="Đổi mật khẩu",
        )
    return account


def get_current_user_info(
    db: Session,
    current_user: Any,
) -> Dict[str, Any]:
    """Trả về thông tin tài khoản hiện tại từ database."""
    ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    account = db.execute(
        select(TaiKhoan).where(TaiKhoan.ma_tai_khoan == ma_tk)
    ).scalars().first()
    if account is None:
        raise NotFoundException("Không tìm thấy tài khoản hiện tại")

    return {
        "ma_tai_khoan": account.ma_tai_khoan,
        "ten_dang_nhap": account.ten_dang_nhap,
        "ma_vai_tro": account.ma_vai_tro,
        "ma_nhan_vien": account.ma_nhan_vien,
        "ma_khach_thue": account.ma_khach_thue,
    }
