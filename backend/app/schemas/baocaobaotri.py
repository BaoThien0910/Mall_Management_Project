# File: app/schemas/baocaobaotri.py
"""
Pydantic v2 schemas cho module Báo cáo trạng thái mặt bằng.
"""

from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.constants.statuses import TrangThaiMatBang


# ── Create ────────────────────────────────────────────────────────────────────

class BaoCaoBaoTriCreate(BaseModel):
    mamb: str = Field(..., min_length=1, max_length=20, description="Mã mặt bằng kiểm tra")
    ngaykiemtra: date = Field(..., description="Ngày kiểm tra thực tế (không được ở tương lai)")
    trangthai_thucte: str = Field(
        ..., description="Trạng thái thực tế quan sát được"
    )
    ghichu: Optional[str] = Field(None, max_length=1000, description="Ghi chú bổ sung")

    @field_validator("trangthai_thucte")
    @classmethod
    def validate_trangthai(cls, v: str) -> str:
        if v not in TrangThaiMatBang.ALL:
            raise ValueError(
                f"Trạng thái thực tế không hợp lệ. Chấp nhận: {TrangThaiMatBang.ALL}"
            )
        return v

    @field_validator("ngaykiemtra")
    @classmethod
    def validate_ngaykiemtra(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Ngày kiểm tra không được ở tương lai")
        return v


# ── Response ──────────────────────────────────────────────────────────────────

class BaoCaoBaoTriResponse(BaseModel):
    mabc: str
    mamb: str
    nguoilap: str          # matk của người lập báo cáo
    ngaykiemtra: date
    trangthai_thucte: str
    ghichu: Optional[str]

    model_config = {"from_attributes": True}
