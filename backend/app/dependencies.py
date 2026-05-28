# File: app/dependencies.py
from typing import Any, Callable, List, Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.constants.roles import RoleCode
from app.database import get_db
from app.exceptions.business_exceptions import (
    ForbiddenException,
    UnauthorizedException,
)
from app.models.taikhoan import TaiKhoan
from app.utils.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/dang-nhap",
    auto_error=False,
)


def _normalize_role_value(role: Any) -> str:
    """Chuẩn hóa RoleCode enum hoặc chuỗi thường về cùng dạng string."""
    return role.value if hasattr(role, "value") else str(role)


def _get_account_identifier_column() -> Any:
    """Lấy cột mã tài khoản phù hợp với biến thể tên model hiện có."""
    if hasattr(TaiKhoan, "ma_tai_khoan"):
        return getattr(TaiKhoan, "ma_tai_khoan")
    return getattr(TaiKhoan, "ma_tk")


def _get_account_status_value(account: TaiKhoan) -> Any:
    """Lấy trạng thái tài khoản theo tên thuộc tính model hiện có."""
    return getattr(account, "trang_thai", None)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> TaiKhoan:
    """Giải mã JWT, xác thực tài khoản và trả về người dùng hiện tại."""
    if token is None or not token.strip():
        raise UnauthorizedException("Thiếu access token")

    try:
        payload = decode_access_token(token)
    except Exception:
        raise UnauthorizedException("Token không hợp lệ hoặc đã hết hạn")
    ma_tk = payload.get("ma_tk") or payload.get("sub")

    if not ma_tk:
        raise UnauthorizedException("Token không chứa thông tin tài khoản")

    account_identifier_column = _get_account_identifier_column()
    stmt = select(TaiKhoan).where(account_identifier_column == ma_tk)
    tai_khoan = db.execute(stmt).scalars().first()

    if tai_khoan is None:
        raise UnauthorizedException("Tài khoản không tồn tại")

    if _get_account_status_value(tai_khoan) != "Hoạt động":
        raise ForbiddenException("Tài khoản đã bị vô hiệu hóa")

    return tai_khoan


def require_roles(
    allowed_roles: List[RoleCode],
) -> Callable[..., TaiKhoan]:
    """Tạo dependency kiểm tra role hiện tại có thuộc nhóm được phép hay không."""

    allowed_role_values = {
        _normalize_role_value(role)
        for role in allowed_roles
    }

    def _role_checker(
        current_user: TaiKhoan = Depends(get_current_user),
    ) -> TaiKhoan:
        current_role = _normalize_role_value(current_user.ma_vai_tro)

        if current_role not in allowed_role_values:
            raise ForbiddenException("Bạn không có quyền truy cập chức năng này")

        return current_user

    return _role_checker
