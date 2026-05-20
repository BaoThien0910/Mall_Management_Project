# File: app/utils/datetime_helper.py
from datetime import date, datetime


def current_datetime() -> datetime:
    """Trả về thời gian hiện tại từ một điểm gọi tập trung để dễ thay đổi về sau."""
    return datetime.now()


def current_date() -> date:
    """Trả về ngày hiện tại."""
    return current_datetime().date()


def is_future_date(value: date | datetime) -> bool:
    """Kiểm tra ngày hoặc thời điểm có nằm trong tương lai hay không."""
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value > datetime.now(tz=value.tzinfo)
        return value > current_datetime()

    return value > current_date()


def validate_date_range(
    start_date: date,
    end_date: date,
) -> bool:
    """Kiểm tra ngày kết thúc phải lớn hơn ngày bắt đầu."""
    return end_date > start_date


def month_year_key(month: int, year: int) -> str:
    """Tạo khóa tháng-năm theo định dạng MM-YYYY."""
    return f"{month:02d}-{year}"
