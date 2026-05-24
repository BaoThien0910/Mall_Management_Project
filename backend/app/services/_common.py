# File: app/services/_common.py
from datetime import datetime
from typing import Any, Iterable, Optional
from uuid import uuid4


def generate_code(prefix: str, max_length: int = 20) -> str:
    """Sinh mã ngắn phù hợp varchar(20)."""
    suffix_length = max_length - len(prefix)
    return f"{prefix}{uuid4().hex[:suffix_length].upper()}"


def get_value(obj: Any, names: Iterable[str], default: Any = None) -> Any:
    """Đọc giá trị từ object theo nhiều tên thuộc tính khả dĩ."""
    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


def get_column(model: Any, names: Iterable[str]) -> Any:
    """Lấy column ORM theo nhiều tên thuộc tính khả dĩ."""
    for name in names:
        if hasattr(model, name):
            return getattr(model, name)
    raise AttributeError(f"Không tìm thấy column trong {model}: {list(names)}")


def set_first_existing(obj: Any, names: Iterable[str], value: Any) -> None:
    """Set giá trị vào thuộc tính đầu tiên tồn tại trên object."""
    for name in names:
        if hasattr(obj, name):
            setattr(obj, name, value)
            return
    setattr(obj, list(names)[0], value)


def utc_now_naive() -> datetime:
    """Trả về datetime hiện tại dạng naive, phù hợp cột datetime2 hiện tại."""
    return datetime.now()
