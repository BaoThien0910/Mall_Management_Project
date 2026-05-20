# File: app/models/baocaotaichinh.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, DateTime, DECIMAL, ForeignKey, Index, Integer, String, Unicode, UnicodeText, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BaoCaoTaiChinh(Base):
    __tablename__ = "BAOCAOTAICHINH"
    __table_args__ = (
        CheckConstraint(
            "LOAIBAOCAO IN (N'Báo cáo công nợ', N'Báo cáo doanh số')",
            name="CK_BAOCAOTAICHINH_LOAIBAOCAO",
        ),
        CheckConstraint("THANG BETWEEN 1 AND 12", name="CK_BAOCAOTAICHINH_THANG"),
        CheckConstraint(
            "(TONGTIEN IS NULL OR TONGTIEN >= 0)",
            name="CK_BAOCAOTAICHINH_TONGTIEN",
        ),
        CheckConstraint(
            "TRANGTHAI IN (N'Bản nháp', N'Đã ban hành')",
            name="CK_BAOCAOTAICHINH_TRANGTHAI",
        ),
        Index("IX_BAOCAOTAICHINH_LOAI_THANG_NAM", "LOAIBAOCAO", "THANG", "NAM"),
        Index("IX_BAOCAOTAICHINH_TRANGTHAI_MANV", "TRANGTHAI", "MANV_LAP"),
    )

    ma_bao_cao_tai_chinh: Mapped[str] = mapped_column("MABCTC", String(20), primary_key=True)
    loai_bao_cao: Mapped[str] = mapped_column("LOAIBAOCAO", Unicode(50), nullable=False)
    thang: Mapped[int] = mapped_column("THANG", Integer, nullable=False)
    nam: Mapped[int] = mapped_column("NAM", Integer, nullable=False)
    ma_nhan_vien_lap: Mapped[str] = mapped_column(
        "MANV_LAP",
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
    noi_dung: Mapped[str] = mapped_column("NOIDUNG", UnicodeText, nullable=False)
    tong_tien: Mapped[Decimal | None] = mapped_column("TONGTIEN", DECIMAL(18, 2), nullable=True)
    trang_thai: Mapped[str] = mapped_column(
        "TRANGTHAI",
        Unicode(30),
        nullable=False,
        server_default=text("N'Bản nháp'"),
    )

    nhan_vien_lap: Mapped["NhanVien"] = relationship(
        back_populates="bao_cao_tai_chinhs",
        foreign_keys=[ma_nhan_vien_lap],
    )

    def __repr__(self) -> str:
        return f"<BaoCaoTaiChinh(ma_bao_cao_tai_chinh={self.ma_bao_cao_tai_chinh!r}, loai_bao_cao={self.loai_bao_cao!r})>"