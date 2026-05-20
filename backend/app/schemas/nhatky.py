# File: app/schemas/nhatky.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.constants.statuses import AuditAction


class NhatKyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_nhat_ky: str
    ma_tai_khoan: str
    thoi_gian: datetime
    hanh_dong: AuditAction
    doi_tuong: str
    ma_doi_tuong: Optional[str] = None
    gia_tri_cu: Optional[str] = None
    gia_tri_moi: Optional[str] = None
    chi_tiet: Optional[str] = None
    ip_address: Optional[str] = None


class NhatKyFilter(BaseModel):
    ma_tai_khoan: Optional[str] = Field(default=None, max_length=20)
    hanh_dong: Optional[AuditAction] = None
    doi_tuong: Optional[str] = Field(default=None, max_length=100)
    tu_ngay: Optional[datetime] = None
    den_ngay: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

    @model_validator(mode="after")
    def validate_datetime_range(self) -> "NhatKyFilter":
        if (
            self.tu_ngay is not None
            and self.den_ngay is not None
            and self.den_ngay < self.tu_ngay
        ):
            raise ValueError("Đến ngày phải lớn hơn hoặc bằng từ ngày.")
        return self
