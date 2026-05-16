"""Seed DB on startup."""

import json
from datetime import UTC, datetime, date
from uuid import uuid4

from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import CongNo, HoaDon, TaiKhoan
from app.utils.security import hash_password


def _seed_invoices_demo(db: Session) -> None:
    if db.query(HoaDon).first() is not None:
        return

    ts = datetime(2025, 10, 3, tzinfo=UTC)
    db.add_all(
        [
            HoaDon(
                so_hoa_don="INV-2025-0988",
                ma_congno="DEB-2025-003",
                so_tien=28500000,
                ngay_tt=ts,
                phuong_thuc="bank_transfer",
                ma_giao_dich=f"TXN-SEED-{uuid4().hex[:12].upper()}",
            ),
            HoaDon(
                so_hoa_don="INV-2025-0910",
                ma_congno="DEB-2025-001",
                so_tien=42000000,
                ngay_tt=datetime(2025, 10, 1, tzinfo=UTC),
                phuong_thuc="momo",
                ma_giao_dich=f"TXN-SEED-{uuid4().hex[:12].upper()}",
            ),
        ]
    )


def bootstrap_db(seed: bool = True) -> None:
    Base.metadata.create_all(bind=engine)
    if not seed:
        return

    db: Session = SessionLocal()
    try:
        if db.query(TaiKhoan).first() is None:
            users = [
                TaiKhoan(
                    email_dang_nhap="a",
                    mat_khau_bam=hash_password("1"),
                    vai_tro_ma="admin",
                    ma_khach_dai_dien=None,
                ),
                TaiKhoan(
                    email_dang_nhap="t",
                    mat_khau_bam=hash_password("1"),
                    vai_tro_ma="tenant",
                    ma_khach_dai_dien="STARBUCKS",
                ),
                TaiKhoan(
                    email_dang_nhap="s",
                    mat_khau_bam=hash_password("1"),
                    vai_tro_ma="staff",
                    ma_khach_dai_dien=None,
                ),
                TaiKhoan(
                    email_dang_nhap="b",
                    mat_khau_bam=hash_password("1"),
                    vai_tro_ma="management",
                    ma_khach_dai_dien=None,
                ),
            ]
            db.add_all(users)

            lines_starbucks = [
                {
                    "key": "1",
                    "type": "rent",
                    "description": "Tiền thuê mặt bằng tháng 10/2025",
                    "amount": 38000000,
                },
                {"key": "2", "type": "utility", "description": "Điện nước (chỉ số T10)", "amount": 5200000},
                {"key": "3", "type": "service", "description": "Phí dịch vụ chung", "amount": 1200000},
                {"key": "4", "type": "penalty", "description": "Phạt chậm trả (5 ngày)", "amount": 600000},
            ]
            debts = [
                CongNo(
                    ma_congno="DEB-2025-001",
                    ten_khach_thue="Starbucks",
                    ma_khach="STARBUCKS",
                    ma_matbang="GF-01",
                    ky_thanh_toan="10/2025",
                    ngay_den_han=date(2025, 11, 5),
                    tong_phat_sinh=45000000,
                    da_thanh_toan=0,
                    trang_thai="overdue",
                    ghi_chu="Công nợ tạo từ hợp đồng (mô phỏng)",
                    chi_tiet_json=json.dumps(lines_starbucks, ensure_ascii=False),
                ),
                CongNo(
                    ma_congno="DEB-2025-002",
                    ten_khach_thue="Uniqlo",
                    ma_khach="UNIQLO",
                    ma_matbang="L2-12",
                    ky_thanh_toan="10/2025",
                    ngay_den_han=date(2025, 11, 10),
                    tong_phat_sinh=82000000,
                    da_thanh_toan=41000000,
                    trang_thai="partial",
                    ghi_chu=None,
                    chi_tiet_json=json.dumps(
                        [
                            {
                                "key": "1",
                                "type": "rent",
                                "description": "Tiền thuê tháng 10/2025",
                                "amount": 75000000,
                            },
                            {
                                "key": "2",
                                "type": "utility",
                                "description": "Điện nước",
                                "amount": 7000000,
                            },
                        ],
                        ensure_ascii=False,
                    ),
                ),
                CongNo(
                    ma_congno="DEB-2025-003",
                    ten_khach_thue="Highlands Coffee",
                    ma_khach="HIGHLANDS",
                    ma_matbang="GF-08",
                    ky_thanh_toan="09/2025",
                    ngay_den_han=date(2025, 10, 5),
                    tong_phat_sinh=28500000,
                    da_thanh_toan=28500000,
                    trang_thai="paid",
                    ghi_chu=None,
                    chi_tiet_json=None,
                ),
                CongNo(
                    ma_congno="DEB-2025-004",
                    ten_khach_thue="Starbucks",
                    ma_khach="STARBUCKS",
                    ma_matbang="GF-01",
                    ky_thanh_toan="11/2025",
                    ngay_den_han=date(2025, 12, 5),
                    tong_phat_sinh=45000000,
                    da_thanh_toan=0,
                    trang_thai="unpaid",
                    ghi_chu=None,
                    chi_tiet_json=None,
                ),
            ]
            db.add_all(debts)
            db.commit()

        _seed_invoices_demo(db)
        db.commit()
    finally:
        db.close()
