# File: app/schemas/dulieu_import_taichinh.py
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants.statuses import (
    DuLieuImportTaiChinhStatus,
    LoaiKhoanTaiChinh,
)
from app.utils.validators import validate_month, validate_year


class DuLieuImportTaiChinhResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_import: str
    ma_hop_dong: str
    thang: int
    nam: int
    loai_khoan: LoaiKhoanTaiChinh
    so_tien: Decimal
    ghi_chu: Optional[str] = None
    ma_nhan_vien_import: str
    thoi_gian_import: datetime
    ten_file: Optional[str] = None
    dong_excel: Optional[int] = None
    trang_thai: DuLieuImportTaiChinhStatus
    loi_chi_tiet: Optional[str] = None


class DuLieuImportTaiChinhFilter(BaseModel):
    ma_hop_dong: Optional[str] = Field(default=None, max_length=20)
    thang: Optional[int] = None
    nam: Optional[int] = None
    trang_thai: Optional[DuLieuImportTaiChinhStatus] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

    @field_validator("thang")
    @classmethod
    def validate_optional_month(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and not validate_month(value):
            raise ValueError("Tháng phải nằm trong khoảng 1 đến 12.")
        return value

    @field_validator("nam")
    @classmethod
    def validate_optional_year(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and not validate_year(value):
            raise ValueError("Năm phải nằm trong khoảng 2000 đến 2100.")
        return value


class LoiDongImportResponse(BaseModel):
    dong_excel: int = Field(..., ge=1)
    noi_dung_loi: str = Field(..., min_length=1)


class KetQuaImportTaiChinhResponse(BaseModel):
    ten_file: Optional[str] = None
    tong_so_dong: int = Field(..., ge=0)
    so_dong_hop_le: int = Field(..., ge=0)
    so_dong_loi: int = Field(..., ge=0)
    danh_sach_loi: List[LoiDongImportResponse] = Field(default_factory=list)


class BatchDeleteImportRequest(BaseModel):
    ids: List[str] = Field(..., min_length=1)

