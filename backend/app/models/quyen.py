# File: app/models/quyen.py
from __future__ import annotations
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import CheckConstraint, Index, String, Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Quyen(Base):
    __tablename__ = "QUYEN"
    __table_args__ = (
        CheckConstraint(
            "HANHDONG IN ('Xem', 'Tạo', 'Sửa', 'Xóa', 'Duyệt', 'Thanh toán', 'Import')",
            name="CK_QUYEN_HANHDONG",
        ),
        Index("IX_QUYEN_MODULE_HANHDONG", "MODULE", "HANHDONG"),
    )

    ma_quyen: Mapped[str] = mapped_column("MAQUYEN", String(20), primary_key=True)
    ten_quyen: Mapped[str] = mapped_column("TENQUYEN", Unicode(100), nullable=False)
    module: Mapped[str] = mapped_column("MODULE", String(50), nullable=False)
    hanh_dong: Mapped[str] = mapped_column("HANHDONG", String(50), nullable=False)
    mo_ta: Mapped[str | None] = mapped_column("MOTA", Unicode(255), nullable=True)

    vaitro_quyens: Mapped[list["VaiTroQuyen"]] = relationship(back_populates="quyen")

    def __repr__(self) -> str:
        return f"<Quyen(ma_quyen={self.ma_quyen!r}, module={self.module!r}, hanh_dong={self.hanh_dong!r})>"