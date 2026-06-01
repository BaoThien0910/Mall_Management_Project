# File: app/schemas/congno.py
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TinhCongNoThangRequest(BaseModel):
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2000, le=2100)
    han_thanh_toan: Optional[date] = None


class CongNoFilter(BaseModel):
    ma_hop_dong: Optional[str] = None
    keyword: Optional[str] = None
    ma_khach_thue: Optional[str] = None
    thang: Optional[int] = Field(default=None, ge=1, le=12)
    nam: Optional[int] = Field(default=None, ge=2000, le=2100)
    trang_thai: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class CongNoCuaToiFilter(BaseModel):
    ma_hop_dong: Optional[str] = None
    keyword: Optional[str] = None
    thang: Optional[int] = Field(default=None, ge=1, le=12)
    nam: Optional[int] = Field(default=None, ge=2000, le=2100)
    trang_thai: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class ThieuChiSoDienNuocItem(BaseModel):
    ma_hop_dong: str
    ma_mat_bang: str
    ly_do: str


class ThieuDuLieuImportItem(BaseModel):
    ma_hop_dong: str
    ly_do: str


class TinhCongNoThangResponse(BaseModel):
    thang: int
    nam: int
    so_cong_no_da_tao: int
    so_cong_no_bo_qua: int
    so_hop_dong_thieu_chi_so: int
    so_hop_dong_thieu_du_lieu: int
    danh_sach_ma_cn: List[str]
    danh_sach_ma_hd_bo_qua: List[str]
    danh_sach_thieu_chi_so: List[ThieuChiSoDienNuocItem]
    danh_sach_thieu_du_lieu: List[ThieuDuLieuImportItem]


class CongNoResponse(BaseModel):
    ma_cong_no: str
    ma_hop_dong: str
    thang: int
    nam: int
    tien_thue: Decimal
    tien_dien: Decimal
    tien_nuoc: Decimal
    phi_bao_tri: Decimal
    tien_hoan: Decimal
    tong_tien: Decimal
    han_thanh_toan: Optional[date]
    trang_thai: str
    ngay_lap: datetime

    model_config = ConfigDict(from_attributes=True)
