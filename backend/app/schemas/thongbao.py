# File: app/schemas/thongbao.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants.statuses import (
    DoiTuongNhanThongBao,
    LoaiThongBao,
    ThongBaoStatus,
)
from app.utils.validators import ensure_not_blank


class ThongBaoCreate(BaseModel):
    tieu_de: str = Field(..., min_length=1, max_length=255)
    noi_dung: str = Field(..., min_length=1, max_length=4000)
    loai_thong_bao: LoaiThongBao
    doi_tuong_nhan: DoiTuongNhanThongBao

    @field_validator("tieu_de", "noi_dung")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Giá trị không được để trống.")
        return value


class ThuHoiThongBaoRequest(BaseModel):
    ly_do: Optional[str] = Field(default=None, max_length=500)


class ThongBaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_thong_bao: str
    ma_nhan_vien_ban_hanh: str
    tieu_de: str
    noi_dung: str
    loai_thong_bao: LoaiThongBao
    doi_tuong_nhan: DoiTuongNhanThongBao
    ngay_ban_hanh: datetime
    trang_thai: ThongBaoStatus


class ThongBaoFilter(BaseModel):
    loai_thong_bao: Optional[LoaiThongBao] = None
    doi_tuong_nhan: Optional[DoiTuongNhanThongBao] = None
    trang_thai: Optional[ThongBaoStatus] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
