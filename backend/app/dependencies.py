from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.taikhoan import TaiKhoan
from app.services.rbac_service import permissions_for_role
from app.utils.security import decode_token

bearer_scheme = HTTPBearer(auto_error=True)


@dataclass
class Principal:
    email: str
    role: str
    permissions: list[str]
    ma_khach_dai_dien: str | None


def has_permission(p: Principal, code: str) -> bool:
    return "*" in p.permissions or code in p.permissions


def get_principal(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Principal:
    raw = creds.credentials
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thiếu token.",
        )

    try:
        payload = decode_token(raw)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e

    email_from_token = str(payload.get("sub", "")).strip().lower()

    tk = db.query(TaiKhoan).filter(TaiKhoan.email_dang_nhap == email_from_token).first()
    if not tk:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tài khoản không tồn tại.")

    return Principal(
        email=tk.email_dang_nhap,
        role=tk.vai_tro_ma,
        permissions=permissions_for_role(tk.vai_tro_ma),
        ma_khach_dai_dien=tk.ma_khach_dai_dien,
    )


def require_permissions(*codes: str):
    def checker(p: Principal = Depends(get_principal)) -> Principal:
        for c in codes:
            if not has_permission(p, c):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Không đủ quyền thực hiện.",
                )
        return p

    return checker


def require_any_permission(*codes: str):
    def checker(p: Principal = Depends(get_principal)) -> Principal:
        if not any(has_permission(p, c) for c in codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không đủ quyền thực hiện.",
            )
        return p

    return checker


def require_roles(*roles: str):
    def checker(p: Principal = Depends(get_principal)) -> Principal:
        if p.role not in roles and p.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vai trò không được phép.",
            )
        return p

    return checker
