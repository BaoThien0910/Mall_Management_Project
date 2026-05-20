# File: app/models/congno.py
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, Date, DateTime, DECIMAL, ForeignKey, Index, Integer, String, Unicode, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CongNo(Base):
    __tablename__ = "CONGNO"
    __table_args__ = (
        UniqueConstraint("MAHD", "THANG", "NAM", name="UQ_CONGNO_MAHD_THANG_NAM"),
        CheckConstraint("THANG BETWEEN 1 AND 12", name="CK_CONGNO_THANG"),
        CheckConstraint("TIENTHUE >= 0", name="CK_CONGNO_TIENTHUE"),
        CheckConstraint("TIENDIEN >= 0", name="CK_CONGNO_TIENDIEN"),
        CheckConstraint("TIENNUOC >= 0", name="CK_CONGNO_TIENNUOC"),
        CheckConstraint("PHIBAOTRI >= 0", name="CK_CONGNO_PHIBAOTRI"),
        CheckConstraint("TIENHOAN >= 0", name="CK_CONGNO_TIENHOAN"),
        CheckConstraint("TONGTIEN >= 0", name="CK_CONGNO_TONGTIEN_KHONGAM"),
        CheckConstraint(
            "TONGTIEN = TIENTHUE + TIENDIEN + TIENNUOC + PHIBAOTRI - TIENHOAN",
            name="CK_CONGNO_TONGTIEN_CONGTHUC",
        ),
        CheckConstraint(
            "TRANGTHAI IN (N'Chưa thanh toán', N'Đã thanh toán', N'Quá hạn')",
            name="CK_CONGNO_TRANGTHAI",
        ),
        Index("IX_CONGNO_TRANGTHAI_HAN_THANHTOAN", "TRANGTHAI", "HAN_THANHTOAN"),
        Index("IX_CONGNO_THANG_NAM_TRANGTHAI", "THANG", "NAM", "TRANGTHAI"),
    )

    ma_cong_no: Mapped[str] = mapped_column("MACN", String(20), primary_key=True)
    ma_hop_dong: Mapped[str] = mapped_column(
        "MAHD",
        String(20),
        ForeignKey("HOPDONG.MAHD"),
        nullable=False,
    )
    thang: Mapped[int] = mapped_column("THANG", Integer, nullable=False)
    nam: Mapped[int] = mapped_column("NAM", Integer, nullable=False)
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
    han_thanh_toan: Mapped[date | None] = mapped_column("HAN_THANHTOAN", Date, nullable=True)
    trang_thai: Mapped[str] = mapped_column(
        "TRANGTHAI",
        Unicode(30),
        nullable=False,
        server_default=text("N'Chưa thanh toán'"),
    )
    ngay_lap: Mapped[datetime] = mapped_column(
        "NGAYLAP",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )

    hop_dong: Mapped["HopDong"] = relationship(back_populates="cong_nos")
    hoa_dons: Mapped[list["HoaDon"]] = relationship(back_populates="cong_no")

    def __repr__(self) -> str:
        return f"<CongNo(ma_cong_no={self.ma_cong_no!r}, trang_thai={self.trang_thai!r})>"