# File: app/schemas/lichbt.py
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants.statuses import LichBaoTriStatus
from app.utils.validators import ensure_not_blank


class LichBaoTriCreate(BaseModel):
    ma_mat_bang: str = Field(..., max_length=20)
    ma_nhan_vien_thuc_hien: str = Field(..., max_length=20)
    ngay_thuc_hien_du_kien: datetime
    noi_dung: str = Field(..., min_length=1, max_length=4000)

    @field_validator("ma_mat_bang", "ma_nhan_vien_thuc_hien", "noi_dung")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Giá trị không được để trống.")
        return value


class LichBaoTriResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_lich_bao_tri: str
    ma_mat_bang: str
    ma_nhan_vien_lap: str
    ma_nhan_vien_thuc_hien: str
    ngay_lap: datetime
    ngay_thuc_hien_du_kien: datetime
    noi_dung: str
    trang_thai: LichBaoTriStatus
    ket_qua: Optional[str] = None
    chi_phi: Optional[Decimal] = None


class LichBaoTriFilter(BaseModel):
    ma_mat_bang: Optional[str] = Field(default=None, max_length=20)
    ma_nhan_vien_thuc_hien: Optional[str] = Field(default=None, max_length=20)
    trang_thai: Optional[LichBaoTriStatus] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
