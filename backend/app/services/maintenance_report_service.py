# File: app/services/maintenance_report_service.py
"""
Service xử lý nghiệp vụ Báo cáo trạng thái mặt bằng.
"""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.baocaobaotri import BaoCaoBaoTri
from app.models.matbang import MatBang
from app.schemas.baocaobaotri import BaoCaoBaoTriCreate
from app.services.audit_service import write_audit_log


# ── Helpers ───────────────────────────────────────────────────────────────────

def _generate_mabc(db: Session) -> str:
    """Sinh mã báo cáo tự động (BC + 8 ký tự UUID)."""
    while True:
        mabc = "BC" + uuid.uuid4().hex[:8].upper()
        if not db.get(BaoCaoBaoTri, mabc):
            return mabc


# ── Business logic ────────────────────────────────────────────────────────────

def create_bao_cao(
    db: Session,
    data: BaoCaoBaoTriCreate,
    matk: str,
) -> BaoCaoBaoTri:
    """
    TP_VHBT lập báo cáo trạng thái mặt bằng.

    Ràng buộc:
    - Mặt bằng phải tồn tại
    - Ngày kiểm tra không ở tương lai (đã validate trong schema)
    - Trạng thái thực tế phải hợp lệ (đã validate trong schema)
    """
    mb = db.get(MatBang, data.mamb)
    if not mb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy mặt bằng với mã: {data.mamb}",
        )

    mabc = _generate_mabc(db)

    bc = BaoCaoBaoTri(
        mabc=mabc,
        mamb=data.mamb,
        nguoilap=matk,
        ngaykiemtra=data.ngaykiemtra,
        trangthai_thucte=data.trangthai_thucte,
        ghichu=data.ghichu,
    )
    db.add(bc)
    db.commit()
    db.refresh(bc)

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="CREATE",
        doi_tuong="BAOCAO_BAOTRI",
        ma_doi_tuong=mabc,
        noi_dung=(
            f"Lập báo cáo trạng thái mặt bằng '{data.mamb}' "
            f"ngày {data.ngaykiemtra} - trạng thái: {data.trangthai_thucte}"
        ),
    )

    return bc
