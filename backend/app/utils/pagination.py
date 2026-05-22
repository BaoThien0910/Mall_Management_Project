# File: app/utils/pagination.py
from typing import TypedDict


class PaginationMeta(TypedDict):
    """Metadata phân trang chuẩn dùng cho các API danh sách."""

    page: int
    page_size: int
    total: int
    total_pages: int


def normalize_pagination(
    page: int | None,
    page_size: int | None,
    default_page_size: int = 10,
    max_page_size: int = 100,
) -> tuple[int, int]:
    """Chuẩn hóa giá trị page và page_size trước khi truy vấn."""
    normalized_page = page if page is not None and page >= 1 else 1

    if page_size is None or page_size < 1:
        normalized_page_size = default_page_size
    elif page_size > max_page_size:
        normalized_page_size = max_page_size
    else:
        normalized_page_size = page_size

    return normalized_page, normalized_page_size


def calculate_offset(page: int, page_size: int) -> int:
    """Tính offset dùng cho truy vấn phân trang."""
    return (page - 1) * page_size


def calculate_total_pages(total: int, page_size: int) -> int:
    """Tính tổng số trang, làm tròn lên và trả về 0 khi không có dữ liệu."""
    if total <= 0:
        return 0

    return (total + page_size - 1) // page_size
