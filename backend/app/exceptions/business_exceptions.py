# File: app/exceptions/business_exceptions.py
from typing import Any, Dict, List, Optional


class AppException(Exception):
    """Base exception nghiệp vụ dùng chung toàn backend."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


class BadRequestException(AppException):
    """Lỗi request hoặc dữ liệu đầu vào không hợp lệ theo ngữ cảnh nghiệp vụ."""

    def __init__(
        self,
        message: str = "Yêu cầu không hợp lệ",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=400,
            errors=errors,
        )


class UnauthorizedException(AppException):
    """Lỗi xác thực người dùng hoặc token."""

    def __init__(
        self,
        message: str = "Người dùng chưa được xác thực",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=401,
            errors=errors,
        )


class ForbiddenException(AppException):
    """Lỗi vượt quyền hoặc truy cập ngoài phạm vi dữ liệu được phép."""

    def __init__(
        self,
        message: str = "Bạn không có quyền thực hiện thao tác này",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=403,
            errors=errors,
        )


class NotFoundException(AppException):
    """Lỗi không tìm thấy dữ liệu được yêu cầu."""

    def __init__(
        self,
        message: str = "Không tìm thấy dữ liệu",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=404,
            errors=errors,
        )


class ConflictException(AppException):
    """Lỗi xung đột dữ liệu hoặc thao tác bị trùng."""

    def __init__(
        self,
        message: str = "Dữ liệu bị xung đột",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=409,
            errors=errors,
        )


class InvalidStateException(AppException):
    """Lỗi trạng thái bản ghi hiện tại không cho phép thực hiện thao tác."""

    def __init__(
        self,
        message: str = "Trạng thái dữ liệu không cho phép thực hiện thao tác",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=409,
            errors=errors,
        )


class ValidationBusinessException(AppException):
    """Lỗi validate nghiệp vụ tổng hợp với nhiều chi tiết sai sót."""

    def __init__(
        self,
        message: str = "Dữ liệu nghiệp vụ không hợp lệ",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=422,
            errors=errors,
        )


class InternalServerException(AppException):
    """Lỗi hệ thống nội bộ đã được chủ động bọc lại."""

    def __init__(
        self,
        message: str = "Đã xảy ra lỗi hệ thống",
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=500,
            errors=errors,
        )
