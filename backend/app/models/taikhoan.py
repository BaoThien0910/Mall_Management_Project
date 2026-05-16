from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TaiKhoan(Base):
    __tablename__ = "TaiKhoan"

    ma_tk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_dang_nhap: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    mat_khau_bam: Mapped[str] = mapped_column(String(255), nullable=False)
    vai_tro_ma: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    ma_khach_dai_dien: Mapped[str | None] = mapped_column(String(64), nullable=True)
