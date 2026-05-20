# File: app/exceptions/handlers.py
import logging
from typing import Any, Dict, List, Sequence, Tuple

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.exceptions.business_exceptions import AppException
from app.utils.response import error_response


logger = logging.getLogger(__name__)


def _format_validation_field(loc: Sequence[Any]) -> str:
    """Chuẩn hóa đường dẫn field từ loc của FastAPI/Pydantic."""
    if not loc:
        return "unknown"

    parts: List[str] = [str(item) for item in loc]
    scope = parts[0]

    if scope == "body":
        remaining = parts[1:]
        return ".".join(remaining) if remaining else "body"

    if scope in {"query", "path", "header", "cookie"}:
        remaining = parts[1:]
        suffix = ".".join(remaining) if remaining else ""
        return f"{scope}.{suffix}" if suffix else scope

    return ".".join(parts)


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    """Xử lý exception nghiệp vụ và trả response lỗi chuẩn hóa."""
    content = error_response(
        message=exc.message,
        errors=exc.errors,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Chuẩn hóa lỗi validate request của FastAPI/Pydantic."""
    formatted_errors: List[Dict[str, Any]] = []

    for error in exc.errors():
        loc = error.get("loc", ())
        formatted_errors.append(
            {
                "field": _format_validation_field(loc),
                "message": error.get("msg", "Dữ liệu không hợp lệ"),
                "type": error.get("type", "validation_error"),
            }
        )

    content = error_response(
        message="Dữ liệu gửi lên không hợp lệ",
        errors=formatted_errors,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=content,
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Chuẩn hóa HTTPException phát sinh từ dependency hoặc router cũ."""
    message = exc.detail if isinstance(exc.detail, str) else "Đã xảy ra lỗi HTTP"
    content = error_response(
        message=message,
        errors=None,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


async def integrity_error_handler(
    request: Request,
    exc: IntegrityError,
) -> JSONResponse:
    """Ẩn chi tiết SQL thô và trả lỗi xung đột dữ liệu chuẩn hóa."""
    logger.warning(
        "IntegrityError occurred during request processing.",
        exc_info=exc,
    )

    content = error_response(
        message="Thao tác gây xung đột dữ liệu",
        errors=[
            {
                "field": "database",
                "message": "Vi phạm ràng buộc dữ liệu",
            }
        ],
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=content,
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Fallback cho lỗi ngoài dự kiến, không lộ traceback ra client."""
    logger.exception(
        "Unhandled exception",
        exc_info=exc,
    )

    content = error_response(
        message="Đã xảy ra lỗi hệ thống",
        errors=None,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Đăng ký toàn bộ exception handler tập trung cho ứng dụng."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(
        RequestValidationError,
        request_validation_exception_handler,
    )
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
