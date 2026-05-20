# File: app/schemas/baocaobaotri.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants.statuses import MatBangStatus
from app.utils.validators import ensure_not_blank


class BaoCaoTrangThaiMatBangCreate(BaseModel):
    ma_mat_bang: str = Field(..., max_length=20)
    trang_thai_thuc_te: MatBangStatus
    noi_dung: str = Field(..., min_length=1, max_length=4000)
    ket_luan: Optional[str] = Field(default=None, max_length=4000)

    @field_validator("ma_mat_bang", "noi_dung")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Giá trị không được để trống.")
        return value


class BaoCaoBaoTriResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_bao_cao_bao_tri: str
    ma_mat_bang: str
    ma_nhan_vien_lap: str
    ma_su_co: Optional[str] = None
    ma_lich_bao_tri: Optional[str] = None
    ngay_lap: datetime
    trang_thai_thuc_te: MatBangStatus
    noi_dung: str
    ket_luan: Optional[str] = None


class BaoCaoBaoTriFilter(BaseModel):
    ma_mat_bang: Optional[str] = Field(default=None, max_length=20)
    ma_nhan_vien_lap: Optional[str] = Field(default=None, max_length=20)
    ma_su_co: Optional[str] = Field(default=None, max_length=20)
    ma_lich_bao_tri: Optional[str] = Field(default=None, max_length=20)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
