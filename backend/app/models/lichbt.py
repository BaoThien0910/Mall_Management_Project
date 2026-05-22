# File: app/models/lichbt.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, DateTime, DECIMAL, ForeignKey, Index, String, Unicode, UnicodeText, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LichBaoTri(Base):
    __tablename__ = "LICHBT"
    __table_args__ = (
        CheckConstraint(
            "NGAYTHUCHIEN_DUKIEN > NGAYLAP",
            name="CK_LICHBT_NGAYTHUCHIEN",
        ),
        CheckConstraint(
            "TRANGTHAI IN (N'Chưa thực hiện', N'Đang thực hiện', N'Hoàn thành', N'Hủy')",
            name="CK_LICHBT_TRANGTHAI",
        ),
        CheckConstraint(
            "(CHIPHI IS NULL OR CHIPHI >= 0)",
            name="CK_LICHBT_CHIPHI",
        ),
        Index("IX_LICHBT_MAMB_TRANGTHAI_NGAY", "MAMB", "TRANGTHAI", "NGAYTHUCHIEN_DUKIEN"),
        Index("IX_LICHBT_MANV_THUCHIEN_TRANGTHAI", "MANV_THUCHIEN", "TRANGTHAI"),
    )

    ma_lich_bao_tri: Mapped[str] = mapped_column("MALICHBT", String(20), primary_key=True)
    ma_mat_bang: Mapped[str] = mapped_column(
        "MAMB",
        String(20),
        ForeignKey("MATBANG.MAMB"),
        nullable=False,
    )
    ma_nhan_vien_lap: Mapped[str] = mapped_column(
        "MANV_LAP",
        String(20),
        ForeignKey("NHANVIEN.MANV"),
        nullable=False,
    )
    ma_nhan_vien_thuc_hien: Mapped[str] = mapped_column(
        "MANV_THUCHIEN",
        String(20),
        ForeignKey("NHANVIEN.MANV"),
        nullable=False,
    )
    ngay_lap: Mapped[datetime] = mapped_column(
        "NGAYLAP",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )
    ngay_thuc_hien_du_kien: Mapped[datetime] = mapped_column(
        "NGAYTHUCHIEN_DUKIEN",
        DATETIME2(),
        nullable=False,
    )
    noi_dung: Mapped[str] = mapped_column("NOIDUNG", UnicodeText, nullable=False)
    trang_thai: Mapped[str] = mapped_column(
        "TRANGTHAI",
        Unicode(30),
        nullable=False,
        server_default=text("N'Chưa thực hiện'"),
    )
    ket_qua: Mapped[str | None] = mapped_column("KETQUA", UnicodeText, nullable=True)
    chi_phi: Mapped[Decimal | None] = mapped_column("CHIPHI", DECIMAL(18, 2), nullable=True)

    mat_bang: Mapped["MatBang"] = relationship(back_populates="lich_bao_tris")
    nhan_vien_lap: Mapped["NhanVien"] = relationship(
        back_populates="lich_bao_tris_lap",
        foreign_keys=[ma_nhan_vien_lap],
    )
    nhan_vien_thuc_hien: Mapped["NhanVien"] = relationship(
        back_populates="lich_bao_tris_thuc_hien",
        foreign_keys=[ma_nhan_vien_thuc_hien],
    )
    bao_cao_bao_tris: Mapped[list["BaoCaoBaoTri"]] = relationship(back_populates="lich_bao_tri")

    def __repr__(self) -> str:
        return f"<LichBaoTri(ma_lich_bao_tri={self.ma_lich_bao_tri!r}, trang_thai={self.trang_thai!r})>"