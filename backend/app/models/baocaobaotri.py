# File: app/models/baocaobaotri.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Unicode, UnicodeText, UniqueConstraint, text
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BaoCaoBaoTri(Base):
    __tablename__ = "BAOCAOBAOTRI"
    __table_args__ = (
        CheckConstraint("THANG BETWEEN 1 AND 12", name="CK_BAOCAOBAOTRI_THANG"),
        CheckConstraint("NAM BETWEEN 2000 AND 2100", name="CK_BAOCAOBAOTRI_NAM"),
        UniqueConstraint("THANG", "NAM", name="UQ_BAOCAOBAOTRI_THANG_NAM"),
        Index("IX_BAOCAOBAOTRI_THANG_NAM", "THANG", "NAM"),
        Index("IX_BAOCAOBAOTRI_MANV_NGAYLAP", "MANV", "NGAYLAP"),
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
        back_populates="bao_cao_bao_tris_lap",
        foreign_keys=[ma_nhan_vien_lap],
    )
    chi_tiets: Mapped[list["BaoCaoBaoTriChiTiet"]] = relationship(
        back_populates="bao_cao",
        cascade="all, delete-orphan",
        order_by="BaoCaoBaoTriChiTiet.stt",
    )

    def __repr__(self) -> str:
        return f"<BaoCaoBaoTri(ma_bao_cao={self.ma_bao_cao}, ky_chot={self.ky_chot})>"


class BaoCaoBaoTriChiTiet(Base):
    __tablename__ = "BAOCAOBAOTRI_CHITIET"
    __table_args__ = (
        CheckConstraint("STT > 0", name="CK_BCBT_CT_STT"),
        Index("IX_BCBT_CT_MAYC", "MAYC"),
        Index("IX_BCBT_CT_MAMB_TRANGTHAI", "MAMB", "TRANGTHAI"),
    )

    ma_bao_cao: Mapped[str] = mapped_column(
        "MABC",
        String(20),
        ForeignKey("BAOCAOBAOTRI.MABC", ondelete="CASCADE"),
        primary_key=True,
    )
    stt: Mapped[int] = mapped_column("STT", Integer, primary_key=True)
    ma_yeu_cau: Mapped[str] = mapped_column(
        "MAYC",
        String(20),
        ForeignKey("SK_BAOTRI.MASUCO"),
        nullable=False,
    )
    ma_mat_bang: Mapped[str] = mapped_column(
        "MAMB",
        String(20),
        ForeignKey("MATBANG.MAMB"),
        nullable=False,
    )
    ngay_yeu_cau: Mapped[datetime] = mapped_column("NGAYYC", DATETIME2(), nullable=False)
    mo_ta: Mapped[str] = mapped_column("MOTA", UnicodeText, nullable=False)
    trang_thai: Mapped[str] = mapped_column("TRANGTHAI", Unicode(30), nullable=False)
    ngay_giai_quyet: Mapped[datetime | None] = mapped_column("NGAYGIAIQUYET", DATETIME2(), nullable=True)
    ket_qua: Mapped[str | None] = mapped_column("KETQUA", UnicodeText, nullable=True)

    bao_cao: Mapped["BaoCaoBaoTri"] = relationship(back_populates="chi_tiets")
    su_co_bao_tri: Mapped["SuCoBaoTri"] = relationship(back_populates="bao_cao_bao_tri_chi_tiets")
    mat_bang: Mapped["MatBang"] = relationship(back_populates="bao_cao_bao_tri_chi_tiets")

    def __repr__(self) -> str:
        return f"<BaoCaoBaoTriChiTiet(ma_bao_cao={self.ma_bao_cao}, stt={self.stt})>"
