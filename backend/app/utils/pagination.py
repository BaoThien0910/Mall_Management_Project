"""Trả danh sách có `items`, `total` cho các API có phân trang."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int = 0
    limit: int = 100
