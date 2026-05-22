# File: app/utils/validators.py
import re
from datetime import date, datetime, time
from decimal import Decimal


def validate_positive_decimal(value: Decimal) -> bool:
    """Kiểm tra số thập phân lớn hơn 0."""
    return value > 0


def validate_non_negative_decimal(value: Decimal) -> bool:
    """Kiểm tra số thập phân lớn hơn hoặc bằng 0."""
    return value >= 0


def validate_month(month: int) -> bool:
    """Kiểm tra tháng có nằm trong khoảng 1 đến 12 hay không."""
    return 1 <= month <= 12


def validate_year(year: int) -> bool:
    """Kiểm tra năm có nằm trong phạm vi dữ liệu được chấp nhận hay không."""
    return 2000 <= year <= 2100


def validate_phone_number_basic(phone: str) -> bool:
    """Kiểm tra số điện thoại theo quy tắc cú pháp tối giản."""
    return bool(re.fullmatch(r"\+?\d{9,15}", phone))


def validate_email_basic(email: str) -> bool:
    """Kiểm tra email bằng biểu thức chính quy đơn giản."""
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


def ensure_not_blank(value: str | None) -> bool:
    """Đảm bảo chuỗi không None, không rỗng và không chỉ chứa khoảng trắng."""
    return value is not None and bool(value.strip())


def validate_end_greater_than_start(
    start_value: date | datetime,
    end_value: date | datetime,
) -> bool:
    """Kiểm tra giá trị kết thúc phải lớn hơn giá trị bắt đầu."""
    if isinstance(start_value, datetime) and isinstance(end_value, datetime):
        return end_value > start_value

    if isinstance(start_value, datetime) and not isinstance(end_value, datetime):
        normalized_end = datetime.combine(end_value, time.max)
        return normalized_end > start_value

    if not isinstance(start_value, datetime) and isinstance(end_value, datetime):
        normalized_start = datetime.combine(start_value, time.min)
        return end_value > normalized_start

    return end_value > start_value
