# File: app/models/taikhoan.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Unicode,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaiKhoan(Base):
    __tablename__ = "TAIKHOAN"
    __table_args__ = (
        UniqueConstraint("TENDANGNHAP", name="UQ_TAIKHOAN_TENDANGNHAP"),
        CheckConstraint(
            "TRANGTHAI IN (N'Hoạt động', N'Vô hiệu')",
            name="CK_TAIKHOAN_TRANGTHAI",
        ),
        CheckConstraint(
            "SOLAN_DANGNHAPSAI >= 0",
            name="CK_TAIKHOAN_SOLAN_DANGNHAPSAI",
        ),
        CheckConstraint(
            "((MANV IS NOT NULL AND MAKH IS NULL) OR (MANV IS NULL AND MAKH IS NOT NULL))",
            name="CK_TAIKHOAN_CHUTHE",
        ),
        Index(
            "UX_TAIKHOAN_MANV_NOTNULL",
            "MANV",
            unique=True,
            mssql_where=text("MANV IS NOT NULL"),
        ),
        Index(
            "UX_TAIKHOAN_MAKH_NOTNULL",
            "MAKH",
            unique=True,
            mssql_where=text("MAKH IS NOT NULL"),
        ),
        Index("IX_TAIKHOAN_MAVAITRO_TRANGTHAI", "MAVAITRO", "TRANGTHAI"),
        Index("IX_TAIKHOAN_MANV_MAKH", "MANV", "MAKH"),
    )

    ma_tai_khoan: Mapped[str] = mapped_column("MATK", String(20), primary_key=True)
    ten_dang_nhap: Mapped[str] = mapped_column("TENDANGNHAP", String(50), nullable=False)
    mat_khau: Mapped[str] = mapped_column("MATKHAU", String(255), nullable=False)
    trang_thai: Mapped[str] = mapped_column(
        "TRANGTHAI",
        Unicode(20),
        nullable=False,
        server_default=text("N'Hoạt động'"),
    )
    bat_buoc_doi_mk: Mapped[bool] = mapped_column(
        "BATBUOC_DOIMK",
        Boolean,
        nullable=False,
        server_default=text("1"),
    )
    so_lan_dang_nhap_sai: Mapped[int] = mapped_column(
        "SOLAN_DANGNHAPSAI",
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    khoa_den: Mapped[datetime | None] = mapped_column("KHOA_DEN", DATETIME2(), nullable=True)
    ma_nhan_vien: Mapped[str | None] = mapped_column(
        "MANV",
        String(20),
        ForeignKey("NHANVIEN.MANV"),
        nullable=True,
    )
    ma_khach_thue: Mapped[str | None] = mapped_column(
        "MAKH",
        String(20),
        ForeignKey("KHACHTHUE.MAKH"),
        nullable=True,
    )
    ma_vai_tro: Mapped[str] = mapped_column(
        "MAVAITRO",
        String(20),
        ForeignKey("VAITRO.MAVAITRO"),
        nullable=False,
    )
    ngay_tao: Mapped[datetime] = mapped_column(
        "NGAYTAO",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )

    vai_tro: Mapped["VaiTro"] = relationship(back_populates="tai_khoans")
    nhan_vien: Mapped["NhanVien | None"] = relationship(
        back_populates="tai_khoan",
        foreign_keys=[ma_nhan_vien],
    )
    khach_thue: Mapped["KhachThue | None"] = relationship(
        back_populates="tai_khoan",
        foreign_keys=[ma_khach_thue],
    )
    nhat_kys: Mapped[list["NhatKy"]] = relationship(back_populates="tai_khoan")

    def __repr__(self) -> str:
        return f"<TaiKhoan(ma_tai_khoan={self.ma_tai_khoan!r}, ten_dang_nhap={self.ten_dang_nhap!r})>"