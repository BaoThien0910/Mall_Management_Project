# File: app/models/vaitro.py
from __future__ import annotations

from sqlalchemy import CheckConstraint, Index, String, Unicode, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mssql import DATETIME2
from app.database import Base


class VaiTro(Base):
    __tablename__ = "VAITRO"
    __table_args__ = (
        UniqueConstraint("TENVAITRO", name="UQ_VAITRO_TENVAITRO"),
        CheckConstraint(
            "TRANGTHAI IN (N'Đang dùng', N'Ngừng dùng')",
            name="CK_VAITRO_TRANGTHAI",
        ),
        Index("IX_VAITRO_TRANGTHAI", "TRANGTHAI"),
    )

    ma_vai_tro: Mapped[str] = mapped_column("MAVAITRO", String(20), primary_key=True)
    ten_vai_tro: Mapped[str] = mapped_column("TENVAITRO", Unicode(100), nullable=False)
    mo_ta: Mapped[str | None] = mapped_column("MOTA", Unicode(255), nullable=True)
    trang_thai: Mapped[str] = mapped_column("TRANGTHAI", Unicode(30), nullable=False)

    tai_khoans: Mapped[list["TaiKhoan"]] = relationship(back_populates="vai_tro")
    vaitro_quyens: Mapped[list["VaiTroQuyen"]] = relationship(back_populates="vai_tro")

    def __repr__(self) -> str:
        return f"<VaiTro(ma_vai_tro={self.ma_vai_tro!r}, ten_vai_tro={self.ten_vai_tro!r})>"