# File: app/models/chisodiennuoc.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, DateTime, DECIMAL, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ChiSoDienNuoc(Base):
    __tablename__ = "CHISODIENNUOC"
    __table_args__ = (
        UniqueConstraint("MAMB", "THANG", "NAM", name="UQ_CHISODIENNUOC_MAMB_THANG_NAM"),
        CheckConstraint("THANG BETWEEN 1 AND 12", name="CK_CHISODIENNUOC_THANG"),
        CheckConstraint("CHISODIENDAU >= 0", name="CK_CHISODIENNUOC_DIEN_DAU"),
        CheckConstraint("CHISODIENCUOI >= CHISODIENDAU", name="CK_CHISODIENNUOC_DIEN_CUOI"),
        CheckConstraint("CHISONUOCDAU >= 0", name="CK_CHISODIENNUOC_NUOC_DAU"),
        CheckConstraint("CHISONUOCCUOI >= CHISONUOCDAU", name="CK_CHISODIENNUOC_NUOC_CUOI"),
        Index("IX_CHISODIENNUOC_MANV_NGAY", "MANV_NHAP", "NGAYNHAP"),
        CheckConstraint("SODIEN_TIEUTHU >= 0",name="CK_CHISODIENNUOC_SODIEN_TIEUTHU",),
        CheckConstraint("SONUOC_TIEUTHU >= 0",name="CK_CHISODIENNUOC_SONUOC_TIEUTHU",),
        CheckConstraint("DONGIA_DIEN > 0",name="CK_CHISODIENNUOC_DONGIA_DIEN",),
        CheckConstraint("DONGIA_NUOC > 0",name="CK_CHISODIENNUOC_DONGIA_NUOC",),
        CheckConstraint("TIENDIEN >= 0",name="CK_CHISODIENNUOC_TIENDIEN",),
        CheckConstraint("TIENNUOC >= 0",name="CK_CHISODIENNUOC_TIENNUOC",),
    )

    ma_chi_so_dien_nuoc: Mapped[str] = mapped_column("MACSDN", String(20), primary_key=True)
    ma_mat_bang: Mapped[str] = mapped_column(
        "MAMB",
        String(20),
        ForeignKey("MATBANG.MAMB"),
        nullable=False,
    )
    ma_nhan_vien_nhap: Mapped[str] = mapped_column(
        "MANV_NHAP",
        String(20),
        ForeignKey("NHANVIEN.MANV"),
        nullable=False,
    )
    thang: Mapped[int] = mapped_column("THANG", Integer, nullable=False)
    nam: Mapped[int] = mapped_column("NAM", Integer, nullable=False)
    chi_so_dien_dau: Mapped[Decimal] = mapped_column("CHISODIENDAU", DECIMAL(18, 2), nullable=False)
    chi_so_dien_cuoi: Mapped[Decimal] = mapped_column("CHISODIENCUOI", DECIMAL(18, 2), nullable=False)
    chi_so_nuoc_dau: Mapped[Decimal] = mapped_column("CHISONUOCDAU", DECIMAL(18, 2), nullable=False)
    chi_so_nuoc_cuoi: Mapped[Decimal] = mapped_column("CHISONUOCCUOI", DECIMAL(18, 2), nullable=False)
    ngay_nhap: Mapped[datetime] = mapped_column(
        "NGAYNHAP",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )

    mat_bang: Mapped["MatBang"] = relationship(back_populates="chi_so_dien_nuocs")
    nhan_vien_nhap: Mapped["NhanVien"] = relationship(
        back_populates="chi_so_dien_nuocs_nhap",
        foreign_keys=[ma_nhan_vien_nhap],
    )

    so_dien_tieu_thu: Mapped[Decimal] = mapped_column(
        "SODIEN_TIEUTHU",
        DECIMAL(18, 2),
        nullable=False,
        server_default=text("0"),
    )

    so_nuoc_tieu_thu: Mapped[Decimal] = mapped_column(
        "SONUOC_TIEUTHU",
        DECIMAL(18, 2),
        nullable=False,
        server_default=text("0"),
    )

    don_gia_dien: Mapped[Decimal] = mapped_column(
        "DONGIA_DIEN",
        DECIMAL(18, 2),
        nullable=False,
        server_default=text("3500"),
    )

    don_gia_nuoc: Mapped[Decimal] = mapped_column(
        "DONGIA_NUOC",
        DECIMAL(18, 2),
        nullable=False,
        server_default=text("2200"),
    )

    tien_dien: Mapped[Decimal] = mapped_column(
        "TIENDIEN",
        DECIMAL(18, 2),
        nullable=False,
        server_default=text("0"),
    )

    tien_nuoc: Mapped[Decimal] = mapped_column(
        "TIENNUOC",
        DECIMAL(18, 2),
        nullable=False,
        server_default=text("0"),
    )
    def __repr__(self) -> str:
        return f"<ChiSoDienNuoc(ma_chi_so_dien_nuoc={self.ma_chi_so_dien_nuoc!r}, thang={self.thang!r}, nam={self.nam!r})>"