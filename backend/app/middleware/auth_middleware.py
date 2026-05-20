# File: app/middleware/auth_middleware.py
from typing import Any, Dict, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.utils.security import decode_access_token


def _extract_bearer_token(
    authorization_header: Optional[str],
) -> Optional[str]:
    """Trích xuất token Bearer hợp lệ từ Authorization header."""
    if authorization_header is None:
        return None

    prefix = "Bearer "
    if not authorization_header.startswith(prefix):
        return None

    token = authorization_header[len(prefix):].strip()
    return token or None


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Chuẩn bị ngữ cảnh xác thực từ JWT mà không chặn request trực tiếp."""

    async def dispatch(
        self,
        request: Request,
        call_next: Any,
    ) -> Response:
        request.state.auth_payload = None
        request.state.auth_error = None
        request.state.ma_tk = None
        request.state.ma_vai_tro = None
        request.state.ma_nv = None
        request.state.ma_kh = None

        authorization_header = request.headers.get("Authorization")
        token = _extract_bearer_token(authorization_header)

        if token is not None:
            try:
                payload: Dict[str, Any] = decode_access_token(token)
                request.state.auth_payload = payload
                request.state.ma_tk = payload.get("ma_tk") or payload.get("sub")
                request.state.ma_vai_tro = payload.get("ma_vai_tro")
                request.state.ma_nv = payload.get("ma_nv")
                request.state.ma_kh = payload.get("ma_kh")
            except Exception as exc:
                request.state.auth_error = exc

        response = await call_next(request)
        return response
