# File: app/models/khachthue.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, DateTime, Index, String, Unicode, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class KhachThue(Base):
    __tablename__ = "KHACHTHUE"
    __table_args__ = (
        UniqueConstraint("CCCD_MST", name="UQ_KHACHTHUE_CCCD_MST"),
        CheckConstraint(
            "TRANGTHAI IN (N'Đang thuê', N'Ngừng thuê')",
            name="CK_KHACHTHUE_TRANGTHAI",
        ),
        Index("IX_KHACHTHUE_SDT_EMAIL", "SDT", "EMAIL"),
        Index("IX_KHACHTHUE_TRANGTHAI", "TRANGTHAI"),
    )

    ma_khach_thue: Mapped[str] = mapped_column("MAKH", String(20), primary_key=True)
    ten_khach: Mapped[str] = mapped_column("TENKHACH", Unicode(150), nullable=False)
    cccd_mst: Mapped[str] = mapped_column("CCCD_MST", String(30), nullable=False)
    so_dien_thoai: Mapped[str | None] = mapped_column("SDT", String(15), nullable=True)
    email: Mapped[str | None] = mapped_column("EMAIL", String(100), nullable=True)
    dia_chi: Mapped[str | None] = mapped_column("DIACHI", Unicode(255), nullable=True)
    trang_thai: Mapped[str] = mapped_column(
        "TRANGTHAI",
        Unicode(30),
        nullable=False,
        server_default=text("N'Đang thuê'"),
    )
    ngay_tao: Mapped[datetime] = mapped_column(
        "NGAYTAO",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )

    tai_khoan: Mapped["TaiKhoan | None"] = relationship(
        back_populates="khach_thue",
        uselist=False,
        foreign_keys="TaiKhoan.ma_khach_thue",
    )
    hop_dongs: Mapped[list["HopDong"]] = relationship(back_populates="khach_thue")
    yeu_cau_thue_thems: Mapped[list["YeuCauThueThem"]] = relationship(back_populates="khach_thue")
    hoa_dons: Mapped[list["HoaDon"]] = relationship(back_populates="khach_thue")
    su_co_bao_tris: Mapped[list["SuCoBaoTri"]] = relationship(back_populates="khach_thue")

    def __repr__(self) -> str:
        return f"<KhachThue(ma_khach_thue={self.ma_khach_thue!r}, ten_khach={self.ten_khach!r})>"