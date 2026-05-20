# File: app/models/sk_baotri.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, DateTime, DECIMAL, ForeignKey, Index, String, Unicode, UnicodeText, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SuCoBaoTri(Base):
    __tablename__ = "SK_BAOTRI"
    __table_args__ = (
        CheckConstraint(
            "TRANGTHAI IN (N'Chờ duyệt', N'Đã duyệt', N'Từ chối', N'Đang xử lý', N'Hoàn thành')",
            name="CK_SK_BAOTRI_TRANGTHAI",
        ),
        CheckConstraint(
            "(CHIPHI IS NULL OR CHIPHI >= 0)",
            name="CK_SK_BAOTRI_CHIPHI",
        ),
        CheckConstraint(
            "(TRANGTHAI <> N'Từ chối' OR LYDO_TUCHOI IS NOT NULL)",
            name="CK_SK_BAOTRI_TUCHOI_LYDO",
        ),
        Index("IX_SK_BAOTRI_MAMB_TRANGTHAI", "MAMB", "TRANGTHAI"),
        Index("IX_SK_BAOTRI_MAKH_NGAYGUI", "MAKH", "NGAYGUI"),
        Index("IX_SK_BAOTRI_MANV_XULY_TRANGTHAI", "MANV_XULY", "TRANGTHAI"),
        Index("IX_SK_BAOTRI_MANV_DUYET_PHANCONG", "MANV_DUYET", "MANV_PHANCONG"),
    )

    ma_su_co: Mapped[str] = mapped_column("MASUCO", String(20), primary_key=True)
    ma_mat_bang: Mapped[str] = mapped_column(
        "MAMB",
        String(20),
        ForeignKey("MATBANG.MAMB"),
        nullable=False,
    )
    ma_khach_thue: Mapped[str] = mapped_column(
        "MAKH",
        String(20),
        ForeignKey("KHACHTHUE.MAKH"),
        nullable=False,
    )
    ma_nhan_vien_duyet: Mapped[str | None] = mapped_column(
        "MANV_DUYET",
        String(20),
        ForeignKey("NHANVIEN.MANV"),
        nullable=True,
    )
    ma_nhan_vien_phan_cong: Mapped[str | None] = mapped_column(
        "MANV_PHANCONG",
        String(20),
        ForeignKey("NHANVIEN.MANV"),
        nullable=True,
    )
    ma_nhan_vien_xu_ly: Mapped[str | None] = mapped_column(
        "MANV_XULY",
        String(20),
        ForeignKey("NHANVIEN.MANV"),
        nullable=True,
    )
    ngay_gui: Mapped[datetime] = mapped_column(
        "NGAYGUI",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )
    mo_ta: Mapped[str] = mapped_column("MOTA", UnicodeText, nullable=False)
    trang_thai: Mapped[str] = mapped_column(
        "TRANGTHAI",
        Unicode(30),
        nullable=False,
        server_default=text("N'Chờ duyệt'"),
    )
    ly_do_tu_choi: Mapped[str | None] = mapped_column("LYDO_TUCHOI", UnicodeText, nullable=True)
    ngay_duyet: Mapped[datetime | None] = mapped_column("NGAYDUYET", DATETIME2(), nullable=True)
    ngay_phan_cong: Mapped[datetime | None] = mapped_column("NGAYPHANCONG", DATETIME2(), nullable=True)
    ngay_hoan_thanh: Mapped[datetime | None] = mapped_column("NGAYHOANTHANH", DATETIME2(), nullable=True)
    ket_qua: Mapped[str | None] = mapped_column("KETQUA", UnicodeText, nullable=True)
    chi_phi: Mapped[Decimal | None] = mapped_column("CHIPHI", DECIMAL(18, 2), nullable=True)

    mat_bang: Mapped["MatBang"] = relationship(back_populates="su_co_bao_tris")
    khach_thue: Mapped["KhachThue"] = relationship(back_populates="su_co_bao_tris")
    nhan_vien_duyet: Mapped["NhanVien | None"] = relationship(
        back_populates="su_cos_duyet",
        foreign_keys=[ma_nhan_vien_duyet],
    )
    nhan_vien_phan_cong: Mapped["NhanVien | None"] = relationship(
        back_populates="su_cos_phan_cong",
        foreign_keys=[ma_nhan_vien_phan_cong],
    )
    nhan_vien_xu_ly: Mapped["NhanVien | None"] = relationship(
        back_populates="su_cos_xu_ly",
        foreign_keys=[ma_nhan_vien_xu_ly],
    )
    bao_cao_bao_tris: Mapped[list["BaoCaoBaoTri"]] = relationship(back_populates="su_co_bao_tri")

    def __repr__(self) -> str:
        return f"<SuCoBaoTri(ma_su_co={self.ma_su_co!r}, trang_thai={self.trang_thai!r})>"