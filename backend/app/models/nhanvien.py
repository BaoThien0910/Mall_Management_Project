# File: app/models/nhanvien.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, Index, String, Unicode, text
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NhanVien(Base):
    __tablename__ = "NHANVIEN"
    __table_args__ = (
        CheckConstraint(
            "PHONGBAN IN (N'Quản trị hệ thống', N'Ban Quản Lý', N'Kinh doanh - Tài chính', N'Vận hành - Bảo trì')",
            name="CK_NHANVIEN_PHONGBAN",
        ),
        CheckConstraint(
            "CHUCVU IN (N'Quản trị viên', N'Ban Quản Lý', N'Trưởng phòng', N'Nhân viên')",
            name="CK_NHANVIEN_CHUCVU",
        ),
        CheckConstraint(
            "TRANGTHAI IN (N'Đang làm', N'Nghỉ', N'Tạm khóa')",
            name="CK_NHANVIEN_TRANGTHAI",
        ),
        Index(
            "UX_NHANVIEN_EMAIL_NOTNULL",
            "EMAIL",
            unique=True,
            mssql_where=text("EMAIL IS NOT NULL"),
        ),
        Index("IX_NHANVIEN_PHONGBAN_CHUCVU", "PHONGBAN", "CHUCVU"),
    )

    ma_nhan_vien: Mapped[str] = mapped_column("MANV", String(20), primary_key=True)
    ho_ten: Mapped[str] = mapped_column("HOTEN", Unicode(100), nullable=False)
    phong_ban: Mapped[str] = mapped_column("PHONGBAN", Unicode(50), nullable=False)
    chuc_vu: Mapped[str] = mapped_column("CHUCVU", Unicode(50), nullable=False)
    so_dien_thoai: Mapped[str | None] = mapped_column("SDT", String(15), nullable=True)
    email: Mapped[str | None] = mapped_column("EMAIL", String(100), nullable=True)
    trang_thai: Mapped[str] = mapped_column(
        "TRANGTHAI",
        Unicode(30),
        nullable=False,
        server_default=text("N'Đang làm'"),
    )
    ngay_tao: Mapped[datetime] = mapped_column(
        "NGAYTAO",
        DATETIME2(),
        nullable=False,
        server_default=text("GETDATE()"),
    )

    tai_khoan: Mapped["TaiKhoan | None"] = relationship(
        back_populates="nhan_vien",
        uselist=False,
        foreign_keys="TaiKhoan.ma_nhan_vien",
    )
    hop_dongs_so_hoa: Mapped[list["HopDong"]] = relationship(
        back_populates="nhan_vien_so_hoa",
        foreign_keys="HopDong.ma_nhan_vien_so_hoa",
    )
    yeu_cau_thue_them_duyet: Mapped[list["YeuCauThueThem"]] = relationship(
        back_populates="nhan_vien_duyet",
        foreign_keys="YeuCauThueThem.ma_nhan_vien_duyet",
    )
    thong_baos_ban_hanh: Mapped[list["ThongBao"]] = relationship(
        back_populates="nhan_vien_ban_hanh",
        foreign_keys="ThongBao.ma_nhan_vien_ban_hanh",
    )
    chi_so_dien_nuocs_nhap: Mapped[list["ChiSoDienNuoc"]] = relationship(
        back_populates="nhan_vien_nhap",
        foreign_keys="ChiSoDienNuoc.ma_nhan_vien_nhap",
    )
    du_lieu_imports: Mapped[list["DuLieuImportTaiChinh"]] = relationship(
        back_populates="nhan_vien_import",
        foreign_keys="DuLieuImportTaiChinh.ma_nhan_vien_import",
    )
    bao_cao_tai_chinhs: Mapped[list["BaoCaoTaiChinh"]] = relationship(
        back_populates="nhan_vien_lap",
        foreign_keys="BaoCaoTaiChinh.ma_nhan_vien_lap",
    )
    su_cos_duyet: Mapped[list["SuCoBaoTri"]] = relationship(
        back_populates="nhan_vien_duyet",
        foreign_keys="SuCoBaoTri.ma_nhan_vien_duyet",
    )
    su_cos_phan_cong: Mapped[list["SuCoBaoTri"]] = relationship(
        back_populates="nhan_vien_phan_cong",
        foreign_keys="SuCoBaoTri.ma_nhan_vien_phan_cong",
    )
    su_cos_xu_ly: Mapped[list["SuCoBaoTri"]] = relationship(
        back_populates="nhan_vien_xu_ly",
        foreign_keys="SuCoBaoTri.ma_nhan_vien_xu_ly",
    )
    bao_cao_bao_tris_lap: Mapped[list["BaoCaoBaoTri"]] = relationship(
        back_populates="nhan_vien_lap",
        foreign_keys="BaoCaoBaoTri.ma_nhan_vien_lap",
    )

    def __repr__(self) -> str:
        return f"<NhanVien(ma_nhan_vien={self.ma_nhan_vien})>"
