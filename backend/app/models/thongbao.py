# File: app/models/thongbao.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Unicode, UnicodeText, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ThongBao(Base):
    __tablename__ = "THONGBAO"
    __table_args__ = (
        CheckConstraint(
            "LOAITHONGBAO IN (N'Thông báo', N'Kế hoạch', N'Quy định')",
            name="CK_THONGBAO_LOAITHONGBAO",
        ),
        CheckConstraint(
            "DOITUONGNHAN IN (N'Toàn hệ thống', N'Nội bộ', N'Khách thuê')",
            name="CK_THONGBAO_DOITUONGNHAN",
        ),
        CheckConstraint(
            "TRANGTHAI IN (N'Đã ban hành', N'Đã thu hồi')",
            name="CK_THONGBAO_TRANGTHAI",
        ),
        Index("IX_THONGBAO_DOITUONG_TRANGTHAI", "DOITUONGNHAN", "TRANGTHAI"),
        Index("IX_THONGBAO_LOAI_NGAY", "LOAITHONGBAO", "NGAYBANHANH"),
    )

    ma_thong_bao: Mapped[str] = mapped_column("MATB", String(20), primary_key=True)
    ma_nhan_vien_ban_hanh: Mapped[str] = mapped_column(
        "MANV_BANHANH",
        String(20),
        ForeignKey("NHANVIEN.MANV"),
        nullable=False,
    )
    tieu_de: Mapped[str] = mapped_column("TIEUDE", Unicode(255), nullable=False)
    noi_dung: Mapped[str] = mapped_column("NOIDUNG", UnicodeText, nullable=False)
    loai_thong_bao: Mapped[str] = mapped_column("LOAITHONGBAO", Unicode(50), nullable=False)
    doi_tuong_nhan: Mapped[str] = mapped_column("DOITUONGNHAN", Unicode(50), nullable=False)
    ngay_ban_hanh: Mapped[datetime] = mapped_column(
        "NGAYBANHANH",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )
    trang_thai: Mapped[str] = mapped_column(
        "TRANGTHAI",
        Unicode(30),
        nullable=False,
        server_default=text("N'Đã ban hành'"),
    )

    nhan_vien_ban_hanh: Mapped["NhanVien"] = relationship(
        back_populates="thong_baos_ban_hanh",
        foreign_keys=[ma_nhan_vien_ban_hanh],
    )

    def __repr__(self) -> str:
        return f"<ThongBao(ma_thong_bao={self.ma_thong_bao!r}, tieu_de={self.tieu_de!r})>"