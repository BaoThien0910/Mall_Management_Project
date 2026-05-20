# File: app/middleware/audit_middleware.py
import logging
import time
import uuid
from typing import Any, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import settings
from app.constants.statuses import AuditAction
from app.database import SessionLocal
from app.services.audit_service import write_audit_log


logger = logging.getLogger(__name__)


def _extract_client_ip(request: Request) -> Optional[str]:
    """Lấy IP client từ X-Forwarded-For hoặc request.client."""
    trust_x_forwarded_for = getattr(
        settings,
        "TRUST_X_FORWARDED_FOR",
        True,
    )

    if trust_x_forwarded_for:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            first_ip = forwarded_for.split(",")[0].strip()
            if first_ip:
                return first_ip

    if request.client is not None:
        return request.client.host

    return None


def _write_forbidden_access_audit(
    request: Request,
    ip_address: Optional[str],
) -> None:
    """Ghi audit vượt quyền phụ trợ mà không làm hỏng response chính."""
    ma_tk = getattr(request.state, "ma_tk", None)
    if ma_tk is None:
        # NHATKY yêu cầu mã tài khoản; request ẩn danh không ghi vào bảng audit này.
        return

    chi_tiet = (
        "Truy cập bị từ chối: "
        f"{request.method} {request.url.path} "
        "- HTTP 403"
    )

    db = SessionLocal()
    try:
        write_audit_log(
            db=db,
            ma_tk=ma_tk,
            hanh_dong=AuditAction.VUOT_QUYEN,
            doi_tuong="HTTP_REQUEST",
            ma_doi_tuong=None,
            chi_tiet=chi_tiet,
            ip_address=ip_address,
        )
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Không thể ghi audit log cho sự kiện HTTP 403.")
    finally:
        db.close()


class AuditContextMiddleware(BaseHTTPMiddleware):
    """Gắn metadata request, đo thời gian xử lý và audit sự kiện 403 phù hợp."""

    async def dispatch(
        self,
        request: Request,
        call_next: Any,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        ip_address = _extract_client_ip(request)

        request.state.request_id = request_id
        request.state.ip_address = ip_address
        request.state.request_started_at = time.perf_counter()

        response = await call_next(request)

        process_time_ms = round(
            (time.perf_counter() - request.state.request_started_at) * 1000,
            3,
        )
        request.state.process_time_ms = process_time_ms

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(process_time_ms)

        should_audit_security_events = getattr(
            settings,
            "AUDIT_SECURITY_EVENTS",
            True,
        )
        if response.status_code == 403 and should_audit_security_events:
            _write_forbidden_access_audit(
                request=request,
                ip_address=ip_address,
            )

        return response
