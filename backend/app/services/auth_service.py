"""Đăng nhập / phát JWT."""

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.taikhoan import TaiKhoan
from app.schemas.auth import LoginBody
from app.services.rbac_service import permissions_for_role
from app.utils.security import create_access_token, verify_password


def authenticate_login(db: Session, body: LoginBody) -> TaiKhoan | None:
    email = body.email.strip().lower()
    user = db.query(TaiKhoan).filter(TaiKhoan.email_dang_nhap == email).first()
    if not user:
        return None
    if not verify_password(body.password, user.mat_khau_bam):
        return None
    return user


def issue_token_for_user(user: TaiKhoan) -> str:
    perms = permissions_for_role(user.vai_tro_ma)
    return create_access_token(
        {
            "sub": user.email_dang_nhap,
            "role": user.vai_tro_ma,
            "permissions": perms,
        }
    )


def build_login_response(user: TaiKhoan) -> dict:
    settings = get_settings()
    _ = settings  # dùng sau khi cấu hình refresh token
    token = issue_token_for_user(user)
    return {
        "token": token,
        "role": user.vai_tro_ma,
        "email": user.email_dang_nhap,
        "permissions": permissions_for_role(user.vai_tro_ma),
    }
