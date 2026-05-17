from typing import Any
from fastapi.responses import JSONResponse

def success_response(data: Any = None, message: str = "Thành công", status_code: int = 200) -> JSONResponse:
    """Hàm chuẩn hóa khi API chạy thành công"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data
        }
    )

def error_response(message: str = "Đã xảy ra lỗi", error_code: str = "SYSTEM_ERROR", status_code: int = 400) -> JSONResponse:
    """Hàm chuẩn hóa khi API thất bại"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "error_code": error_code,
            "data": None
        }
    )