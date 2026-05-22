# File: app/utils/response.py
from typing import Any, Dict, List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.inspection import inspect as sqlalchemy_inspect

SENSITIVE_RESPONSE_FIELDS = {
    "mat_khau",
}

def _is_sqlalchemy_model(value: Any) -> bool:
    """Kiểm tra một object có phải SQLAlchemy ORM instance hay không."""
    try:
        inspection = sqlalchemy_inspect(value, raiseerr=False)
    except Exception:
        return False

    return inspection is not None and hasattr(inspection, "mapper")


def _serialize_sqlalchemy_model(instance: Any) -> Dict[str, Any]:
    """
    Chuyển SQLAlchemy ORM model thành dict chỉ gồm các column,
    đồng thời loại bỏ các trường nhạy cảm khỏi response.
    """
    inspection = sqlalchemy_inspect(instance)

    return {
        column.key: _serialize_response_data(getattr(instance, column.key))
        for column in inspection.mapper.column_attrs
        if column.key not in SENSITIVE_RESPONSE_FIELDS
    }


def _serialize_response_data(data: Any) -> Any:
    """
    Chuẩn hóa dữ liệu trước khi đưa vào response:
    - ORM model -> dict
    - List ORM -> List[dict]
    - Dict chứa ORM -> Dict đã serialize
    - datetime, Decimal, Enum... -> jsonable_encoder xử lý tiếp
    """
    if data is None:
        return None

    if _is_sqlalchemy_model(data):
        return _serialize_sqlalchemy_model(data)

    if isinstance(data, dict):
        return {
            key: _serialize_response_data(value)
            for key, value in data.items()
            if key not in SENSITIVE_RESPONSE_FIELDS
        }

    if isinstance(data, (list, tuple, set)):
        return [
            _serialize_response_data(item)
            for item in data
        ]

    return jsonable_encoder(data)


def success_response(
    message: str,
    data: Any = None,
) -> Dict[str, Any]:
    """Tạo response thành công theo chuẩn thống nhất của hệ thống."""
    return {
        "success": True,
        "message": message,
        "data": _serialize_response_data(data),
        "errors": None,
    }


def error_response(
    message: str,
    errors: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Tạo response lỗi theo chuẩn thống nhất của hệ thống."""
    return {
        "success": False,
        "message": message,
        "data": None,
        "errors": _serialize_response_data(errors or []),
    }


def paginated_response(
    message: str,
    items: List[Any],
    page: int,
    page_size: int,
    total: int,
) -> Dict[str, Any]:
    """Tạo response phân trang theo chuẩn thống nhất của hệ thống."""
    total_pages = 0
    if total > 0:
        total_pages = (total + page_size - 1) // page_size

    return success_response(
        message=message,
        data={
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            },
        },
    )