# File: app/models/yc_thuethem.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Unicode, UnicodeText, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class YeuCauThueThem(Base):
    __tablename__ = "YC_THUETHEM"
    __table_args__ = (
        CheckConstraint(
            "TRANGTHAI IN (N'Chờ duyệt', N'Đã duyệt - Chờ số hóa hợp đồng', N'Từ chối', N'Đã tạo hợp đồng')",
            name="CK_YC_THUETHEM_TRANGTHAI",
        ),
        CheckConstraint(
            "(TRANGTHAI <> N'Từ chối' OR LYDO_TUCHOI IS NOT NULL)",
            name="CK_YC_THUETHEM_TUCHOI_LYDO",
        ),
        Index(
            "UX_YC_THUETHEM_PENDING_MAKH_MAMB",
            "MAKH",
            "MAMB",
            unique=True,
            mssql_where=text("TRANGTHAI = N'Chờ duyệt'"),
        ),
        Index("IX_YC_THUETHEM_MAKH_MAMB_TRANGTHAI", "MAKH", "MAMB", "TRANGTHAI"),
        Index("IX_YC_THUETHEM_MAMB_TRANGTHAI", "MAMB", "TRANGTHAI"),
        Index("IX_YC_THUETHEM_MANV_DUYET_NGAYDUYET", "MANV_DUYET", "NGAYDUYET"),
    )

    ma_yeu_cau: Mapped[str] = mapped_column("MAYC", String(20), primary_key=True)
    ma_khach_thue: Mapped[str] = mapped_column(
        "MAKH",
        String(20),
        ForeignKey("KHACHTHUE.MAKH"),
        nullable=False,
    )
    ma_mat_bang: Mapped[str] = mapped_column(
        "MAMB",
        String(20),
        ForeignKey("MATBANG.MAMB"),
        nullable=False,
    )
    ma_nhan_vien_duyet: Mapped[str | None] = mapped_column(
        "MANV_DUYET",
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
    ly_do: Mapped[str] = mapped_column("LYDO", UnicodeText, nullable=False)
    trang_thai: Mapped[str] = mapped_column(
        "TRANGTHAI",
        Unicode(30),
        nullable=False,
        server_default=text("N'Chờ duyệt'"),
    )
    ngay_duyet: Mapped[datetime | None] = mapped_column("NGAYDUYET", DATETIME2(), nullable=True)
    ly_do_tu_choi: Mapped[str | None] = mapped_column("LYDO_TUCHOI", UnicodeText, nullable=True)
    ghi_chu: Mapped[str | None] = mapped_column("GHICHU", Unicode(255), nullable=True)

    khach_thue: Mapped["KhachThue"] = relationship(back_populates="yeu_cau_thue_thems")
    mat_bang: Mapped["MatBang"] = relationship(back_populates="yeu_cau_thue_thems")
    nhan_vien_duyet: Mapped["NhanVien | None"] = relationship(
        back_populates="yeu_cau_thue_them_duyet",
        foreign_keys=[ma_nhan_vien_duyet],
    )
    hop_dong: Mapped["HopDong | None"] = relationship(
        back_populates="yeu_cau_thue_them",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<YeuCauThueThem(ma_yeu_cau={self.ma_yeu_cau!r}, trang_thai={self.trang_thai!r})>"