# File: app/services/rbac_service.py
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.constants.statuses import AuditAction
from app.exceptions.business_exceptions import BadRequestException, NotFoundException
from app.models import Quyen, VaiTro, VaiTroQuyen
from app.schemas.rbac import VaiTroQuyenAssignRequest
from app.services.audit_service import write_audit_log
from app.utils.transaction import transaction_context


def _user_attr(current_user: Any, short_name: str, long_name: str) -> Any:
    value = getattr(current_user, short_name, None)
    return value if value is not None else getattr(current_user, long_name, None)


def list_roles(
    db: Session,
    current_user: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Trả về danh sách vai trò dưới dạng dữ liệu JSON-safe."""
    roles = db.execute(
        select(VaiTro).order_by(VaiTro.ma_vai_tro.asc())
    ).scalars().all()

    return [
        {
            "ma_vai_tro": role.ma_vai_tro,
            "ten_vai_tro": role.ten_vai_tro,
            "mo_ta": role.mo_ta,
            "trang_thai": role.trang_thai,
        }
        for role in roles
    ]


def list_permissions(
    db: Session,
    current_user: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Trả về danh sách quyền dưới dạng dữ liệu JSON-safe."""
    permissions = db.execute(
        select(Quyen).order_by(Quyen.ma_quyen.asc())
    ).scalars().all()

    return [
        {
            "ma_quyen": permission.ma_quyen,
            "ten_quyen": permission.ten_quyen,
            "module": permission.module,
            "hanh_dong": permission.hanh_dong,
            "mo_ta": permission.mo_ta,
        }
        for permission in permissions
    ]


def get_permissions_by_role(
    db: Session,
    ma_vai_tro: str,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    role = db.execute(
        select(VaiTro).where(VaiTro.ma_vai_tro == ma_vai_tro)
    ).scalars().first()

    if role is None:
        raise NotFoundException("Không tìm thấy vai trò")

    permissions = db.execute(
        select(Quyen)
        .join(VaiTroQuyen, VaiTroQuyen.ma_quyen == Quyen.ma_quyen)
        .where(VaiTroQuyen.ma_vai_tro == ma_vai_tro)
        .order_by(Quyen.ma_quyen.asc())
    ).scalars().all()

    return {
        "ma_vai_tro": role.ma_vai_tro,
        "danh_sach_quyen": [
            {
                "ma_quyen": permission.ma_quyen,
                "ten_quyen": permission.ten_quyen,
                "module": permission.module,
                "hanh_dong": permission.hanh_dong,
                "mo_ta": permission.mo_ta,
            }
            for permission in permissions
        ],
    }


def assign_permissions_to_role(
    db: Session,
    ma_vai_tro: str,
    payload: VaiTroQuyenAssignRequest,
    current_user: Any,
) -> Dict[str, Any]:
    """Ghi đè tập quyền của vai trò trong một transaction."""
    role = db.execute(
        select(VaiTro).where(VaiTro.ma_vai_tro == ma_vai_tro)
    ).scalars().first()
    if role is None:
        raise NotFoundException("Không tìm thấy vai trò")

    requested_codes = list(payload.danh_sach_ma_quyen)
    permissions = db.execute(
        select(Quyen).where(Quyen.ma_quyen.in_(requested_codes))
    ).scalars().all()
    found_codes = {permission.ma_quyen for permission in permissions}
    missing_codes = [code for code in requested_codes if code not in found_codes]
    if missing_codes:
        raise BadRequestException(
            "Một hoặc nhiều mã quyền không tồn tại: " + ", ".join(missing_codes)
        )

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.execute(delete(VaiTroQuyen).where(VaiTroQuyen.ma_vai_tro == ma_vai_tro))
        for code in requested_codes:
            db.add(VaiTroQuyen(ma_vai_tro=ma_vai_tro, ma_quyen=code))
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.CAP_NHAT,
            doi_tuong="VAITRO_QUYEN",
            ma_doi_tuong=ma_vai_tro,
            chi_tiet="Gán quyền cho vai trò",
        )

    return {
        "ma_vai_tro": ma_vai_tro,
        "danh_sach_quyen": [
        {
            "ma_quyen": permission.ma_quyen,
            "ten_quyen": permission.ten_quyen,
            "module": permission.module,
            "hanh_dong": permission.hanh_dong,
            "mo_ta": permission.mo_ta,
        }
        for permission in permissions
    ],
    }
