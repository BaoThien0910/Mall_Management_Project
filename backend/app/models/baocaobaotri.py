# File: app/models/baocaobaotri.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Unicode, UnicodeText, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BaoCaoBaoTri(Base):
    __tablename__ = "BAOCAOBAOTRI"
    __table_args__ = (
        CheckConstraint(
            "TRANGTHAI_THUCTE IN (N'Còn trống', N'Đang thuê', N'Đang bảo trì')",
            name="CK_BAOCAOBAOTRI_TRANGTHAI_THUCTE",
        ),
        Index("IX_BAOCAOBAOTRI_MAMB_NGAYLAP", "MAMB", "NGAYLAP"),
        Index("IX_BAOCAOBAOTRI_MANV_LAP", "MANV_LAP"),
        Index("IX_BAOCAOBAOTRI_MASUCO_MALICHBT", "MASUCO", "MALICHBT"),
    )

    ma_bao_cao_bao_tri: Mapped[str] = mapped_column("MABC_BT", String(20), primary_key=True)
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
    ma_su_co: Mapped[str | None] = mapped_column(
        "MASUCO",
        String(20),
        ForeignKey("SK_BAOTRI.MASUCO"),
        nullable=True,
    )
    ma_lich_bao_tri: Mapped[str | None] = mapped_column(
        "MALICHBT",
        String(20),
        ForeignKey("LICHBT.MALICHBT"),
        nullable=True,
    )
    ngay_lap: Mapped[datetime] = mapped_column(
        "NGAYLAP",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )
    trang_thai_thuc_te: Mapped[str] = mapped_column("TRANGTHAI_THUCTE", Unicode(30), nullable=False)
    noi_dung: Mapped[str] = mapped_column("NOIDUNG", UnicodeText, nullable=False)
    ket_luan: Mapped[str | None] = mapped_column("KETLUAN", UnicodeText, nullable=True)

    mat_bang: Mapped["MatBang"] = relationship(back_populates="bao_cao_bao_tris")
    nhan_vien_lap: Mapped["NhanVien"] = relationship(
        back_populates="bao_cao_bao_tris_lap",
        foreign_keys=[ma_nhan_vien_lap],
    )
    su_co_bao_tri: Mapped["SuCoBaoTri | None"] = relationship(
        back_populates="bao_cao_bao_tris",
        foreign_keys=[ma_su_co],
    )
    lich_bao_tri: Mapped["LichBaoTri | None"] = relationship(
        back_populates="bao_cao_bao_tris",
        foreign_keys=[ma_lich_bao_tri],
    )

    def __repr__(self) -> str:
        return f"<BaoCaoBaoTri(ma_bao_cao_bao_tri={self.ma_bao_cao_bao_tri!r})>"