# File: app/schemas/import_taichinh.py
"""
Pydantic v2 schemas cho module Import dữ liệu tài chính từ Excel.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Response cho từng dòng import ────────────────────────────────────────────

class DongImportResponse(BaseModel):
    """Thông tin một dòng dữ liệu trong file import."""
    so_dong: int
    mahd: Optional[str]
    thang: Optional[int]
    nam: Optional[int]
    loai_khoan: Optional[str]
    so_tien: Optional[float]
    ghi_chu: Optional[str]
    trang_thai: str          # "Hợp lệ" | "Lỗi" | "Đã dùng tính công nợ"
    loi_chi_tiet: Optional[str]

    model_config = {"from_attributes": True}


class DuLieuImportResponse(BaseModel):
    """Response đại diện cho một bản ghi trong bảng DULIEU_IMPORT_TAICHINH."""
    ma_import: str
    mahd: Optional[str]
    thang: Optional[int]
    nam: Optional[int]
    loai_khoan: Optional[str]
    so_tien: Optional[float]
    ghi_chu: Optional[str]
    manv_import: Optional[str]
    thoi_gian_import: Optional[datetime]
    ten_file: Optional[str]
    so_dong_excel: Optional[int]
    trang_thai: str
    loi_chi_tiet: Optional[str]

    model_config = {"from_attributes": True}


# ── Response sau khi import file ─────────────────────────────────────────────

class ImportKetQuaResponse(BaseModel):
    """Kết quả tổng hợp sau khi import file Excel."""
    ten_file: str
    tong_dong: int
    so_dong_hop_le: int
    so_dong_loi: int
    danh_sach_loi: list[DongImportResponse]


# ── Filter / Query params ─────────────────────────────────────────────────────

class ImportTaiChinhFilter(BaseModel):
    mahd: Optional[str] = None
    thang: Optional[int] = Field(None, ge=1, le=12)
    nam: Optional[int] = Field(None, ge=2000)
    trang_thai: Optional[str] = None
    manv_import: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
