# File: app/models/matbang.py
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import CheckConstraint, DECIMAL, Index, Integer, String, Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MatBang(Base):
    __tablename__ = "MATBANG"
    __table_args__ = (
        CheckConstraint("DIENTICH > 0", name="CK_MATBANG_DIENTICH"),
        CheckConstraint(
            "TRANGTHAI IN (N'Còn trống', N'Đang thuê', N'Đang bảo trì')",
            name="CK_MATBANG_TRANGTHAI",
        ),
        Index("IX_MATBANG_TRANGTHAI_TANG_LOAIMB", "TRANGTHAI", "TANG", "LOAIMB"),
        Index("IX_MATBANG_DIENTICH", "DIENTICH"),
    )

    ma_mat_bang: Mapped[str] = mapped_column("MAMB", String(20), primary_key=True)
    vi_tri: Mapped[str] = mapped_column("VITRI", Unicode(100), nullable=False)
    tang: Mapped[int] = mapped_column("TANG", Integer, nullable=False)
    dien_tich: Mapped[Decimal] = mapped_column("DIENTICH", DECIMAL(10, 2), nullable=False)
    loai_mat_bang: Mapped[str] = mapped_column("LOAIMB", Unicode(50), nullable=False)
    trang_thai: Mapped[str] = mapped_column("TRANGTHAI", Unicode(30), nullable=False)
    ghi_chu: Mapped[str | None] = mapped_column("GHICHU", Unicode(255), nullable=True)

    hop_dongs: Mapped[list["HopDong"]] = relationship(back_populates="mat_bang")
    yeu_cau_thue_thems: Mapped[list["YeuCauThueThem"]] = relationship(back_populates="mat_bang")
    chi_so_dien_nuocs: Mapped[list["ChiSoDienNuoc"]] = relationship(back_populates="mat_bang")
    su_co_bao_tris: Mapped[list["SuCoBaoTri"]] = relationship(back_populates="mat_bang")
    lich_bao_tris: Mapped[list["LichBaoTri"]] = relationship(back_populates="mat_bang")
    bao_cao_bao_tri_chi_tiets: Mapped[list["BaoCaoBaoTriChiTiet"]] = relationship(
        back_populates="mat_bang"
    )

    def __repr__(self) -> str:
        return f"<MatBang(ma_mat_bang={self.ma_mat_bang})>"
