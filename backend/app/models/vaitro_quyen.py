# File: app/models/vaitro_quyen.py
from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mssql import DATETIME2
from app.database import Base


class VaiTroQuyen(Base):
    __tablename__ = "VAITRO_QUYEN"

    ma_vai_tro: Mapped[str] = mapped_column(
        "MAVAITRO",
        String(20),
        ForeignKey("VAITRO.MAVAITRO"),
        primary_key=True,
    )
    ma_quyen: Mapped[str] = mapped_column(
        "MAQUYEN",
        String(20),
        ForeignKey("QUYEN.MAQUYEN"),
        primary_key=True,
    )

    vai_tro: Mapped["VaiTro"] = relationship(back_populates="vaitro_quyens")
    quyen: Mapped["Quyen"] = relationship(back_populates="vaitro_quyens")

    def __repr__(self) -> str:
        return f"<VaiTroQuyen(ma_vai_tro={self.ma_vai_tro!r}, ma_quyen={self.ma_quyen!r})>"