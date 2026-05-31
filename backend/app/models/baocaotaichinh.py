# File: app/models/baocaotaichinh.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DECIMAL, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BaoCaoTaiChinh(Base):
    __tablename__ = "BAOCAOTAICHINH"
    __table_args__ = (
        CheckConstraint("THANG BETWEEN 1 AND 12", name="CK_BAOCAOTAICHINH_THANG"),
        CheckConstraint("NAM BETWEEN 2000 AND 2100", name="CK_BAOCAOTAICHINH_NAM"),
        UniqueConstraint("THANG", "NAM", name="UQ_BAOCAOTAICHINH_THANG_NAM"),
        Index("IX_BAOCAOTAICHINH_THANG_NAM", "THANG", "NAM"),
        Index("IX_BAOCAOTAICHINH_MANV_NGAYLAP", "MANV", "NGAYLAP"),
    )

    ma_bao_cao: Mapped[str] = mapped_column("MABC", String(20), primary_key=True)
    ma_nhan_vien_lap: Mapped[str] = mapped_column(
        "MANV",
        String(20),
        ForeignKey("NHANVIEN.MANV"),
        nullable=False,
    )
    thang: Mapped[int] = mapped_column("THANG", Integer, nullable=False)
    nam: Mapped[int] = mapped_column("NAM", Integer, nullable=False)
    ky_chot: Mapped[str] = mapped_column("KYCHOT", String(7), nullable=False)
    ngay_lap: Mapped[datetime] = mapped_column(
        "NGAYLAP",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )

    nhan_vien_lap: Mapped["NhanVien"] = relationship(
        back_populates="bao_cao_tai_chinhs",
        foreign_keys=[ma_nhan_vien_lap],
    )
    chi_tiets: Mapped[list["BaoCaoTaiChinhChiTiet"]] = relationship(
        back_populates="bao_cao",
        cascade="all, delete-orphan",
        order_by="BaoCaoTaiChinhChiTiet.stt",
    )

    def __repr__(self) -> str:
        return f"<BaoCaoTaiChinh(ma_bao_cao={self.ma_bao_cao}, ky_chot={self.ky_chot})>"


class BaoCaoTaiChinhChiTiet(Base):
    __tablename__ = "BAOCAOTAICHINH_CHITIET"
    __table_args__ = (
        CheckConstraint("STT > 0", name="CK_BCTC_CT_STT"),
        CheckConstraint("TIENTHUE >= 0", name="CK_BCTC_CT_TIENTHUE"),
        CheckConstraint("TIENDIEN >= 0", name="CK_BCTC_CT_TIENDIEN"),
        CheckConstraint("TIENNUOC >= 0", name="CK_BCTC_CT_TIENNUOC"),
        CheckConstraint("TIENHOANTRA >= 0", name="CK_BCTC_CT_TIENHOANTRA"),
        CheckConstraint("CHIPHI_BAOTRI >= 0", name="CK_BCTC_CT_CHIPHI_BAOTRI"),
        CheckConstraint("TONGTIEN >= 0", name="CK_BCTC_CT_TONGTIEN"),
        CheckConstraint("DA_THANH_TOAN >= 0", name="CK_BCTC_CT_DA_THANH_TOAN"),
        CheckConstraint("NO >= 0", name="CK_BCTC_CT_NO"),
        Index("IX_BCTC_CT_MAHD", "MAHD"),
        Index("IX_BCTC_CT_MAKH_MAMB", "MAKH", "MAMB"),
    )

    ma_bao_cao: Mapped[str] = mapped_column(
        "MABC",
        String(20),
        ForeignKey("BAOCAOTAICHINH.MABC", ondelete="CASCADE"),
        primary_key=True,
    )
    stt: Mapped[int] = mapped_column("STT", Integer, primary_key=True)
    ma_hop_dong: Mapped[str] = mapped_column(
        "MAHD",
        String(20),
        ForeignKey("HOPDONG.MAHD"),
        nullable=False,
    )
    ma_khach_thue: Mapped[str] = mapped_column("MAKH", String(20), nullable=False)
    ma_mat_bang: Mapped[str] = mapped_column("MAMB", String(20), nullable=False)
    ky: Mapped[str] = mapped_column("KY", String(7), nullable=False)
    tien_thue: Mapped[Decimal] = mapped_column("TIENTHUE", DECIMAL(18, 2), nullable=False)
    tien_dien: Mapped[Decimal] = mapped_column("TIENDIEN", DECIMAL(18, 2), nullable=False)
    tien_nuoc: Mapped[Decimal] = mapped_column("TIENNUOC", DECIMAL(18, 2), nullable=False)
    tien_hoan_tra: Mapped[Decimal] = mapped_column("TIENHOANTRA", DECIMAL(18, 2), nullable=False)
    chi_phi_bao_tri: Mapped[Decimal] = mapped_column("CHIPHI_BAOTRI", DECIMAL(18, 2), nullable=False)
    tong_tien: Mapped[Decimal] = mapped_column("TONGTIEN", DECIMAL(18, 2), nullable=False)
    da_thanh_toan: Mapped[Decimal] = mapped_column("DA_THANH_TOAN", DECIMAL(18, 2), nullable=False)
    no: Mapped[Decimal] = mapped_column("NO", DECIMAL(18, 2), nullable=False)

    bao_cao: Mapped["BaoCaoTaiChinh"] = relationship(back_populates="chi_tiets")
    hop_dong: Mapped["HopDong"] = relationship()

    def __repr__(self) -> str:
        return f"<BaoCaoTaiChinhChiTiet(ma_bao_cao={self.ma_bao_cao}, stt={self.stt})>"
