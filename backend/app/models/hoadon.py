# File: app/models/hoadon.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, DateTime, DECIMAL, ForeignKey, Index, String, Unicode, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HoaDon(Base):
    __tablename__ = "HOADON"
    __table_args__ = (
        CheckConstraint("TIENTHUE >= 0", name="CK_HOADON_TIENTHUE"),
        CheckConstraint("TIENDIEN >= 0", name="CK_HOADON_TIENDIEN"),
        CheckConstraint("TIENNUOC >= 0", name="CK_HOADON_TIENNUOC"),
        CheckConstraint("PHIBAOTRI >= 0", name="CK_HOADON_PHIBAOTRI"),
        CheckConstraint("TIENHOAN >= 0", name="CK_HOADON_TIENHOAN"),
        CheckConstraint("TONGTIEN >= 0", name="CK_HOADON_TONGTIEN_KHONGAM"),
        CheckConstraint(
            "TONGTIEN = TIENTHUE + TIENDIEN + TIENNUOC + PHIBAOTRI - TIENHOAN",
            name="CK_HOADON_TONGTIEN_CONGTHUC",
        ),
        CheckConstraint("SOTIEN > 0", name="CK_HOADON_SOTIEN_DUONG"),
        CheckConstraint("SOTIEN = TONGTIEN", name="CK_HOADON_SOTIEN_TONGTIEN"),
        CheckConstraint(
            "PHUONGTHUC IN (N'VNPay', N'MoMo', N'ZaloPay')",
            name="CK_HOADON_PHUONGTHUC",
        ),
        CheckConstraint(
            "TRANGTHAI IN (N'Đang xử lý', N'Thành công', N'Thất bại')",
            name="CK_HOADON_TRANGTHAI",
        ),
        Index(
            "UX_HOADON_MACN_THANHCONG",
            "MACN",
            unique=True,
            mssql_where=text("TRANGTHAI = N'Thành công'"),
        ),
        Index("IX_HOADON_MACN_TRANGTHAI", "MACN", "TRANGTHAI"),
        Index("IX_HOADON_MAKH_THOIGIANGD", "MAKH", "THOIGIANGD"),
        Index("IX_HOADON_MAGIAODICHCONG", "MAGIAODICHCONG"),
    )

    ma_hoa_don: Mapped[str] = mapped_column("MAHOADON", String(20), primary_key=True)
    ma_cong_no: Mapped[str] = mapped_column(
        "MACN",
        String(20),
        ForeignKey("CONGNO.MACN"),
        nullable=False,
    )
    ma_khach_thue: Mapped[str] = mapped_column(
        "MAKH",
        String(20),
        ForeignKey("KHACHTHUE.MAKH"),
        nullable=False,
    )
    tien_thue: Mapped[Decimal] = mapped_column("TIENTHUE", DECIMAL(18, 2), nullable=False)
    tien_dien: Mapped[Decimal] = mapped_column("TIENDIEN", DECIMAL(18, 2), nullable=False)
    tien_nuoc: Mapped[Decimal] = mapped_column("TIENNUOC", DECIMAL(18, 2), nullable=False)
    phi_bao_tri: Mapped[Decimal] = mapped_column(
        "PHIBAOTRI",
        DECIMAL(18, 2),
        nullable=False,
        server_default=text("0"),
    )
    tien_hoan: Mapped[Decimal] = mapped_column(
        "TIENHOAN",
        DECIMAL(18, 2),
        nullable=False,
        server_default=text("0"),
    )
    tong_tien: Mapped[Decimal] = mapped_column("TONGTIEN", DECIMAL(18, 2), nullable=False)
    so_tien: Mapped[Decimal] = mapped_column("SOTIEN", DECIMAL(18, 2), nullable=False)
    phuong_thuc: Mapped[str] = mapped_column("PHUONGTHUC", Unicode(50), nullable=False)
    ma_giao_dich_cong: Mapped[str | None] = mapped_column("MAGIAODICHCONG", String(100), nullable=True)
    thoi_gian_giao_dich: Mapped[datetime] = mapped_column(
        "THOIGIANGD",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )
    trang_thai: Mapped[str] = mapped_column(
        "TRANGTHAI",
        Unicode(30),
        nullable=False,
        server_default=text("N'Đang xử lý'"),
    )
    noi_dung: Mapped[str | None] = mapped_column("NOIDUNG", Unicode(255), nullable=True)
    ghi_chu: Mapped[str | None] = mapped_column("GHICHU", Unicode(255), nullable=True)

    cong_no: Mapped["CongNo"] = relationship(back_populates="hoa_dons")
    khach_thue: Mapped["KhachThue"] = relationship(back_populates="hoa_dons")

    def __repr__(self) -> str:
        return f"<HoaDon(ma_hoa_don={self.ma_hoa_don!r}, trang_thai={self.trang_thai!r})>"