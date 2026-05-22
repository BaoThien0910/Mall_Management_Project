# File: app/models/hopdong.py
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, Date, DateTime, DECIMAL, ForeignKey, Index, String, Unicode, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HopDong(Base):
    __tablename__ = "HOPDONG"
    __table_args__ = (
        CheckConstraint("NGAYKETTHUC > NGAYBATDAU", name="CK_HOPDONG_NGAY"),
        CheckConstraint("GIATHUETHANG > 0", name="CK_HOPDONG_GIATHUETHANG"),
        CheckConstraint(
            "TRANGTHAI IN (N'Đang hiệu lực', N'Hết hạn', N'Đã hủy')",
            name="CK_HOPDONG_TRANGTHAI",
        ),
        Index(
            "UX_HOPDONG_MAYC_NOTNULL",
            "MAYC",
            unique=True,
            mssql_where=text("MAYC IS NOT NULL"),
        ),
        Index(
            "UX_HOPDONG_MAMB_DANGHIEULUC",
            "MAMB",
            unique=True,
            mssql_where=text("TRANGTHAI = N'Đang hiệu lực'"),
        ),
        Index("IX_HOPDONG_MAKH_TRANGTHAI", "MAKH", "TRANGTHAI"),
        Index("IX_HOPDONG_MAMB_TRANGTHAI", "MAMB", "TRANGTHAI"),
        Index("IX_HOPDONG_NGAYBATDAU_NGAYKETTHUC", "NGAYBATDAU", "NGAYKETTHUC"),
    )

    ma_hop_dong: Mapped[str] = mapped_column("MAHD", String(20), primary_key=True)
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
    ma_nhan_vien_so_hoa: Mapped[str] = mapped_column(
        "MANV_SOHOA",
        String(20),
        ForeignKey("NHANVIEN.MANV"),
        nullable=False,
    )
    ma_yeu_cau: Mapped[str | None] = mapped_column(
        "MAYC",
        String(20),
        ForeignKey("YC_THUETHEM.MAYC"),
        nullable=True,
    )
    ngay_bat_dau: Mapped[date] = mapped_column("NGAYBATDAU", Date, nullable=False)
    ngay_ket_thuc: Mapped[date] = mapped_column("NGAYKETTHUC", Date, nullable=False)
    gia_thue_thang: Mapped[Decimal] = mapped_column("GIATHUETHANG", DECIMAL(18, 2), nullable=False)
    trang_thai: Mapped[str] = mapped_column("TRANGTHAI", Unicode(30), nullable=False)
    ngay_so_hoa: Mapped[datetime] = mapped_column(
        "NGAYSOHOA",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )

    khach_thue: Mapped["KhachThue"] = relationship(back_populates="hop_dongs")
    mat_bang: Mapped["MatBang"] = relationship(back_populates="hop_dongs")
    nhan_vien_so_hoa: Mapped["NhanVien"] = relationship(
        back_populates="hop_dongs_so_hoa",
        foreign_keys=[ma_nhan_vien_so_hoa],
    )
    yeu_cau_thue_them: Mapped["YeuCauThueThem | None"] = relationship(
        back_populates="hop_dong",
        foreign_keys=[ma_yeu_cau],
    )
    du_lieu_import_tai_chinhs: Mapped[list["DuLieuImportTaiChinh"]] = relationship(
        back_populates="hop_dong"
    )
    cong_nos: Mapped[list["CongNo"]] = relationship(back_populates="hop_dong")

    def __repr__(self) -> str:
        return f"<HopDong(ma_hop_dong={self.ma_hop_dong!r}, trang_thai={self.trang_thai!r})>"