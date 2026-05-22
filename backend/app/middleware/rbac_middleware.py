# File: app/middleware/rbac_middleware.py
from typing import Any, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.constants.roles import INTERNAL_STAFF_ROLES, RoleCode


def _role_value(role: RoleCode) -> str:
    """Lấy giá trị chuỗi từ role enum."""
    return role.value if hasattr(role, "value") else str(role)


def _role_matches(
    role_value: Optional[str],
    expected_role: RoleCode,
) -> bool:
    """So sánh role string trong request state với role enum chuẩn."""
    return role_value == _role_value(expected_role)


def _is_internal_role(role_value: Optional[str]) -> bool:
    """Kiểm tra role hiện tại có thuộc nhóm người dùng nội bộ hay không."""
    if role_value is None:
        return False

    return any(
        role_value == _role_value(role)
        for role in INTERNAL_STAFF_ROLES
    )


class RBACContextMiddleware(BaseHTTPMiddleware):
    """Chuẩn hóa role context để các tầng dưới tái sử dụng khi cần."""

    async def dispatch(
        self,
        request: Request,
        call_next: Any,
    ) -> Response:
        request.state.role_code = None
        request.state.is_authenticated = False
        request.state.is_internal_user = False
        request.state.is_customer = False

        ma_vai_tro = getattr(request.state, "ma_vai_tro", None)
        ma_tk = getattr(request.state, "ma_tk", None)

        if ma_tk is not None:
            request.state.is_authenticated = True

        if ma_vai_tro is not None:
            request.state.role_code = ma_vai_tro
            request.state.is_customer = _role_matches(
                ma_vai_tro,
                RoleCode.KHACH_THUE,
            )
            request.state.is_internal_user = _is_internal_role(ma_vai_tro)

        response = await call_next(request)
        return response
