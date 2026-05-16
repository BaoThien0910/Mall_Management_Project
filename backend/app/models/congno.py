"""Công nợ — MVP: thông tin hiển thị + chi tiết dòng lưu JSON."""

import json
from datetime import date
from typing import Any

from sqlalchemy import Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CongNo(Base):
    __tablename__ = "CongNo"

    ma_congno: Mapped[str] = mapped_column(String(48), primary_key=True)
    ma_khach: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    ten_khach_thue: Mapped[str] = mapped_column(String(255), nullable=False)
    ma_matbang: Mapped[str] = mapped_column(String(32), nullable=False)
    ky_thanh_toan: Mapped[str] = mapped_column(String(32), nullable=False)
    ngay_den_han: Mapped[date] = mapped_column(Date, nullable=False)

    tong_phat_sinh: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    da_thanh_toan: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    trang_thai: Mapped[str] = mapped_column(String(24), nullable=False, default="unpaid")

    ghi_chu: Mapped[str | None] = mapped_column(Text, nullable=True)
    chi_tiet_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    def chi_tiet_dong_list(self) -> list[dict[str, Any]]:
        if not self.chi_tiet_json:
            return []
        try:
            data = json.loads(self.chi_tiet_json)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []
