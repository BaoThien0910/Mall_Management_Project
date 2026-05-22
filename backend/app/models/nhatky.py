# File: app/models/nhatky.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Unicode, UnicodeText, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NhatKy(Base):
    __tablename__ = "NHATKY"
    __table_args__ = (
        CheckConstraint(
            "HANHDONG IN (N'Đăng nhập', N'Đăng xuất', N'Tạo mới', N'Cập nhật', N'Xóa', N'Duyệt', N'Vượt quyền')",
            name="CK_NHATKY_HANHDONG",
        ),
        Index("IX_NHATKY_MATK_THOIGIAN", "MATK", "THOIGIAN"),
        Index("IX_NHATKY_HANHDONG_DOITUONG", "HANHDONG", "DOITUONG"),
    )

    ma_nhat_ky: Mapped[str] = mapped_column("MANHATKY", String(20), primary_key=True)
    ma_tai_khoan: Mapped[str] = mapped_column(
        "MATK",
        String(20),
        ForeignKey("TAIKHOAN.MATK"),
        nullable=False,
    )
    thoi_gian: Mapped[datetime] = mapped_column(
        "THOIGIAN",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )
    hanh_dong: Mapped[str] = mapped_column("HANHDONG", Unicode(50), nullable=False)
    doi_tuong: Mapped[str] = mapped_column("DOITUONG", Unicode(100), nullable=False)
    ma_doi_tuong: Mapped[str | None] = mapped_column("MADOITUONG", String(20), nullable=True)
    gia_tri_cu: Mapped[str | None] = mapped_column("GIATRICU", UnicodeText, nullable=True)
    gia_tri_moi: Mapped[str | None] = mapped_column("GIATRIMOI", UnicodeText, nullable=True)
    chi_tiet: Mapped[str | None] = mapped_column("CHITIET", UnicodeText, nullable=True)
    ip_address: Mapped[str | None] = mapped_column("IP_ADDRESS", String(45), nullable=True)

    tai_khoan: Mapped["TaiKhoan"] = relationship(back_populates="nhat_kys")

    def __repr__(self) -> str:
        return f"<NhatKy(ma_nhat_ky={self.ma_nhat_ky!r}, hanh_dong={self.hanh_dong!r})>"