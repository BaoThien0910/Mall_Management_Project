import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from app.utils.response import error_response

# Cấu hình ghi log lỗi ra terminal/file để dev xem
logger = logging.getLogger("app_exception_handler")

def setup_exception_handlers(app: FastAPI) -> None:
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Bắt các lỗi do lập trình viên chủ động raise (Ví dụ: 401 Sai mật khẩu, 404 Không tìm thấy)"""
        return error_response(
            message=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            status_code=exc.status_code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Bắt các lỗi do Frontend gửi thiếu trường hoặc sai định dạng dữ liệu (Lỗi 422 mặc định của FastAPI)"""
        # Lấy chi tiết danh sách các trường bị lỗi gửi sai
        errors = exc.errors()
        error_messages = []
        for err in errors:
            loc = " -> ".join(str(x) for x in err["loc"])
            error_messages.append(f"Trường [{loc}]: {err['msg']}")
        
        full_message = "Dữ liệu gửi lên không hợp lệ: " + " | ".join(error_messages)
        
        return error_response(
            message=full_message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    @app.exception_handler(Exception)
    async def universal_exception_handler(request: Request, exc: Exception):
        """Bắt tất cả các lỗi crash hệ thống nằm ngoài tầm kiểm soát (Ví dụ: Lỗi sập SQL Server, lỗi code Python chia cho 0)"""
        # Ghi lại toàn bộ log lỗi thô ra terminal để lập trình viên vào xem và sửa
        logger.error(f"Crash hệ thống tại API {request.url.path}: {str(exc)}", exc_info=True)
        
        # Chỉ trả về thông báo chung an toàn cho người dùng, tuyệt đối không lộ log lỗi hệ thống
        return error_response(
            message="Hệ thống đang bận hoặc xảy ra sự cố kỹ thuật. Vui lòng thử lại sau!",
            error_code="INTERNAL_SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )