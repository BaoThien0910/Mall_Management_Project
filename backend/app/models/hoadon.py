from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HoaDon(Base):
    __tablename__ = "HoaDon"

    ma_hd: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    so_hoa_don: Mapped[str] = mapped_column(String(48), unique=True, nullable=False, index=True)
    ma_congno: Mapped[str] = mapped_column(
        String(48), ForeignKey("CongNo.ma_congno"), nullable=False, index=True
    )
    so_tien: Mapped[int] = mapped_column(Integer, nullable=False)
    ngay_tt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    phuong_thuc: Mapped[str] = mapped_column(String(48), nullable=False)
    ma_giao_dich: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
