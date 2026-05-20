# File: app/models/dulieu_import_taichinh.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, DateTime, DECIMAL, ForeignKey, Index, Integer, String, Unicode, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DuLieuImportTaiChinh(Base):
    __tablename__ = "DULIEU_IMPORT_TAICHINH"
    __table_args__ = (
        CheckConstraint("THANG BETWEEN 1 AND 12", name="CK_DULIEU_IMPORT_TAICHINH_THANG"),
        CheckConstraint(
            "LOAIKHOAN IN (N'Tiền thuê', N'Tiền điện', N'Tiền nước', N'Phí bảo trì', N'Hoàn trả')",
            name="CK_DULIEU_IMPORT_TAICHINH_LOAIKHOAN",
        ),
        CheckConstraint("SOTIEN > 0", name="CK_DULIEU_IMPORT_TAICHINH_SOTIEN"),
        CheckConstraint(
            "(DONG_EXCEL IS NULL OR DONG_EXCEL > 0)",
            name="CK_DULIEU_IMPORT_TAICHINH_DONG_EXCEL",
        ),
        CheckConstraint(
            "TRANGTHAI IN (N'Hợp lệ', N'Lỗi', N'Đã dùng tính công nợ')",
            name="CK_DULIEU_IMPORT_TAICHINH_TRANGTHAI",
        ),
        Index("IX_DULIEU_IMPORT_TAICHINH_MAHD_THANG_NAM", "MAHD", "THANG", "NAM"),
        Index("IX_DULIEU_IMPORT_TAICHINH_MANV_THOIGIAN", "MANV_IMPORT", "THOIGIAN_IMPORT"),
        Index("IX_DULIEU_IMPORT_TAICHINH_TRANGTHAI", "TRANGTHAI"),
    )

    ma_import: Mapped[str] = mapped_column("MAIMPORT", String(20), primary_key=True)
    ma_hop_dong: Mapped[str] = mapped_column(
        "MAHD",
        String(20),
        ForeignKey("HOPDONG.MAHD"),
        nullable=False,
    )
    thang: Mapped[int] = mapped_column("THANG", Integer, nullable=False)
    nam: Mapped[int] = mapped_column("NAM", Integer, nullable=False)
    loai_khoan: Mapped[str] = mapped_column("LOAIKHOAN", Unicode(50), nullable=False)
    so_tien: Mapped[Decimal] = mapped_column("SOTIEN", DECIMAL(18, 2), nullable=False)
    ghi_chu: Mapped[str | None] = mapped_column("GHICHU", Unicode(255), nullable=True)
    ma_nhan_vien_import: Mapped[str] = mapped_column(
        "MANV_IMPORT",
        String(20),
        ForeignKey("NHANVIEN.MANV"),
        nullable=False,
    )
    thoi_gian_import: Mapped[datetime] = mapped_column(
        "THOIGIAN_IMPORT",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )
    ten_file: Mapped[str | None] = mapped_column("TENFILE", Unicode(255), nullable=True)
    dong_excel: Mapped[int | None] = mapped_column("DONG_EXCEL", Integer, nullable=True)
    trang_thai: Mapped[str] = mapped_column("TRANGTHAI", Unicode(30), nullable=False)
    loi_chi_tiet: Mapped[str | None] = mapped_column("LOI_CHITIET", Unicode(255), nullable=True)

    hop_dong: Mapped["HopDong"] = relationship(back_populates="du_lieu_import_tai_chinhs")
    nhan_vien_import: Mapped["NhanVien"] = relationship(
        back_populates="du_lieu_imports",
        foreign_keys=[ma_nhan_vien_import],
    )

    def __repr__(self) -> str:
        return f"<DuLieuImportTaiChinh(ma_import={self.ma_import!r}, trang_thai={self.trang_thai!r})>"