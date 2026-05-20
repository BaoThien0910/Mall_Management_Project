# File: app/schemas/hoadon.py
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants.statuses import HoaDonStatus, PhuongThucThanhToan
from app.utils.validators import ensure_not_blank


class TaoGiaoDichThanhToanRequest(BaseModel):
    ma_cong_no: str = Field(..., max_length=20)
    phuong_thuc: PhuongThucThanhToan

    @field_validator("ma_cong_no")
    @classmethod
    def validate_debt_code(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Mã công nợ không được để trống.")
        return value


class MoPhongKetQuaThanhToanRequest(BaseModel):
    ket_qua: str = Field(..., max_length=30)

    @field_validator("ket_qua")
    @classmethod
    def validate_result(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"THANH_CONG", "THAT_BAI"}:
            raise ValueError("Kết quả chỉ được là THANH_CONG hoặc THAT_BAI.")
        return normalized


class HoaDonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_hoa_don: str
    ma_cong_no: str
    ma_khach_thue: str
    tien_thue: Decimal
    tien_dien: Decimal
    tien_nuoc: Decimal
    phi_bao_tri: Decimal
    tien_hoan: Decimal
    tong_tien: Decimal
    so_tien: Decimal
    phuong_thuc: PhuongThucThanhToan
    ma_giao_dich_cong: Optional[str] = None
    thoi_gian_giao_dich: datetime
    trang_thai: HoaDonStatus
    noi_dung: Optional[str] = None
    ghi_chu: Optional[str] = None


class HoaDonFilter(BaseModel):
    ma_cong_no: Optional[str] = Field(default=None, max_length=20)
    ma_khach_thue: Optional[str] = Field(default=None, max_length=20)
    trang_thai: Optional[HoaDonStatus] = None
    phuong_thuc: Optional[PhuongThucThanhToan] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
